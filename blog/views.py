from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, Http404

from view_record.decorator import record_view
from helper.paginator import getPages
from blog.models import Blog, Tag, Comment, Reply
from blog.forms import BlogForm
from users.models import Message

import random

# 博客相关视图函数

def random_recommend():
    blogs = Blog.objects.all()
    num = 7 if len(blogs) >= 7 else len(blogs) 
    random_blogs = random.sample(list(blogs), num)
    return sorted(random_blogs, key=lambda x: x.publish_time, reverse=True)

def author_recommend():
    blogs = Blog.objects.filter(recommend=True)
    num = 7 if len(blogs) >= 7 else len(blogs) 
    author_blogs = random.sample(list(blogs), num)
    return sorted(author_blogs, key=lambda x: x.publish_time, reverse=True)

def blog_list_show(request, pages, blogs):
    random_blogs = random_recommend()    
    recommend_blogs = author_recommend()

    context = { 
        'blogs': blogs, 
        'pages': pages,  
        'random_blogs': random_blogs, 
        'recommend_blogs': recommend_blogs,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_index(request):
    """ 显示博客的列表 """
    blogs = Blog.objects.all()
    pages, blogs = getPages(request, blogs)
    return blog_list_show(request, pages, blogs)

@record_view(Blog)
def blog_show(request, blog_id):
    """ 显示单篇博客的内容 """
    cur_blog = Blog.objects.get(id=blog_id)

    # 检查该篇博文的阅读记录是否存在于cookies中，若无则阅读量+1
    if str("blog_%s_readed" % (blog_id)) not in request.COOKIES:
        cur_blog.read_num += 1
        cur_blog.save()

    pre_blog = Blog.objects.filter(id__gt=blog_id).order_by('id')
    next_blog = Blog.objects.filter(id__lt=blog_id).order_by('-id')

    pre_blog = pre_blog[0] if pre_blog.count() > 0 else None
    next_blog = next_blog[0] if next_blog.count() > 0 else None

    random_blogs = random_recommend()
    recommend_blogs = author_recommend()

    comments = Comment.objects.filter(blog__id=cur_blog.id).order_by('publish_time')

    context = {
        'cur_blog': cur_blog,
        'pre_blog': pre_blog,
        'next_blog': next_blog,
        'comments': comments,
        'random_blogs': random_blogs,
        'recommend_blogs': recommend_blogs,
    }

    response = render(request, 'blog/blog_single.html', context)
    
    # 这里设置在浏览器被关闭之前不会重新对博文阅读数量进行计数
    response.set_cookie("blog_%s_readed" % (blog_id),"True")
    return response

def search_blog(request):
    try:
        wd = request.GET['wd']
        if not wd:
            return HttpResponseRedirect(reverse('blog:blog_index'))
    
        blogs = Blog.objects.filter(caption__icontains=wd)
        pages, blogs = getPages(request, blogs)
        return blog_list_show(request, pages, blogs)
    except Exception:
        raise Http404

def tag_blogs(request, tag_name):
    try:
        tag = Tag.objects.get(tag_name=tag_name)
        blogs = tag.blog_set.all()
        pages, blogs = getPages(request, blogs)
        return blog_list_show(request, pages, blogs)
    except Exception:
        raise Http404

def recommend_blogs(request):
    blogs = Blog.objects.filter(recommend=True)
    pages, blogs = getPages(request, blogs)
    return blog_list_show(request, pages, blogs)

# 评论相关视图函数

def new_comment(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    text = request.POST['comment_text']
    Comment.objects.create(blog=blog, author=request.user, content=text)
    text = str(request.user) + " 在博客 " + str(blog.caption) + " 留下新的评论 " + \
        " [点击此处查看](http://www.schnee.pro/blog/blog/" + str(blog.id) + ")"
    Message.objects.create(text=text, receiver=blog.author, sender=request.user)
    return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))

def delete_comment(request, blog_id, comment_id):
    try:
        del_comment = Comment.objects.get(id=comment_id)
        del_comment.delete()
    finally:
        return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))

# 回复相关视图函数

def new_reply(request, blog_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    text = request.POST['reply_text']
    Reply.objects.create(comment=comment, author=request.user, content=text)
    
    # 通知博客作者
    blog = Blog.objects.get(id=blog_id)
    text = "你的博客 " + str(blog.caption) + " 中的评论有新的回复 " + \
        " [点击此处查看](http://www.schnee.pro/blog/blog/" + str(blog.id) + ")"
    Message.objects.create(text=text, receiver=blog.author, sender=request.user)

    # 通知评论的作者
    text = str(request.user) + " 在博客 " + str(blog.caption) + " 中在你的评论下回复了你 " + \
        " [点击此处查看](http://www.schnee.pro/blog/blog/" + str(blog.id) + ")"
    Message.objects.create(text=text, receiver=comment.author, sender=request.user)
    
    # 通知其他回复者
    replys = comment.reply_set.all()
    text = " 在博客 " + str(blog.caption) + " 中你回复的评论有新的回复 " + \
        " [点击此处查看](http://www.schnee.pro/blog/blog/" + str(blog.id) + ")"
    for reply in replys:
        Message.objects.create(text=text, receiver=reply.author, sender=request.user)

    return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))

def delete_reply(request, blog_id, reply_id):
    try:
        del_reply = Reply.objects.get(id=reply_id)
        del_reply.delete()
    finally:
        return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))

