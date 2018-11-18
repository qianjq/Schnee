from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, Http404

from view_record.decorator import record_view
from helper.paginator import getPages
from sonata.models import Article, Art_Tag, Art_Comment
from sonata.forms import ArticleForm

import random

# 文章相关视图函数

def random_recommend():
    articles = Article.objects.all()
    num = 7 if len(articles) >= 7 else len(articles) 
    random_articles = random.sample(list(articles), num)
    return sorted(random_articles, key=lambda x: x.publish_time, reverse=True)

def author_recommend():
    articles = Article.objects.filter(recommend=True)
    num = 7 if len(articles) >= 7 else len(articles) 
    author_articles = random.sample(list(articles), num)
    return sorted(author_articles, key=lambda x: x.publish_time, reverse=True)

def article_list_show(request, pages, articles):
    random_articles = random_recommend()    
    recommend_articles = author_recommend()

    context = { 
        'articles': articles, 
        'pages': pages,  
        'random_articles': random_articles, 
        'recommend_articles': recommend_articles,
    }
    return render(request, 'sonata/article_list.html', context)

def article_index(request):
    """ 显示文章的列表 """
    articles = Article.objects.all()
    pages, articles = getPages(request, articles)
    return article_list_show(request, pages, articles)

@record_view(Article)
def article_show(request, article_id):
    """ 显示单篇文章的内容 """
    cur_article = Article.objects.get(id=article_id)

    # 检查该篇博文的阅读记录是否存在于cookies中，若无则阅读量+1
    if str("article_%s_readed" % (article_id)) not in request.COOKIES:
        cur_article.read_num += 1
        cur_article.save()

    pre_article = Article.objects.filter(id__gt=article_id).order_by('id')
    next_article = Article.objects.filter(id__lt=article_id).order_by('-id')

    pre_article = pre_article[0] if pre_article.count() > 0 else None
    next_article = next_article[0] if next_article.count() > 0 else None

    random_articles = random_recommend()
    recommend_articles = author_recommend()

    comments = Art_Comment.objects.filter(article__id=cur_article.id).order_by('publish_time')

    context = {
        'cur_article': cur_article,
        'pre_article': pre_article,
        'next_article': next_article,
        'comments': comments,
        'random_articles': random_articles,
        'recommend_articles': recommend_articles,
    }

    response = render(request, 'sonata/article_single.html', context)
    
    # 这里设置在浏览器被关闭之前不会重新对博文阅读数量进行计数
    response.set_cookie("article_%s_readed" % (article_id),"True")
    return response

def search_article(request):
    try:
        wd = request.GET['wd']
        if not wd:
            return HttpResponseRedirect(reverse('sonata:article_index'))
    
        articles = Article.objects.filter(caption__icontains=wd)
        pages, articles = getPages(request, articles)
        return article_list_show(request, pages, articles)
    except Exception:
        raise Http404

def tag_articles(request, tag_name):
    try:
        tag = Art_Tag.objects.get(tag_name=tag_name)
        articles = tag.article_set.all()
        pages, articles = getPages(request, articles)
        return article_list_show(request, pages, articles)
    except Exception:
        raise Http404

def recommend_articles(request):
    articles = Article.objects.filter(recommend=True)
    pages, articles = getPages(request, articles)
    return article_list_show(request, pages, articles)

# 评论相关视图函数

def new_comment(request, article_id):
    article = Article.objects.get(id=article_id)
    text = request.POST['comment_text']
    Art_Comment.objects.create(article=article, author=request.user, content=text)
    return HttpResponseRedirect(reverse('sonata:article_show', args=[article_id]))

def delete_comment(request, article_id, comment_id):
    try:
        del_comment = Art_Comment.objects.get(id=comment_id)
        del_comment.delete()
    finally:
        return HttpResponseRedirect(reverse('sonata:article_show', args=[article_id]))

