from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, Http404

from view_record.decorator import record_view
from helper.paginator import getPages
from blog.models import Blog, Tag, Comment
from blog.forms import BlogForm

import random

def check_admin_user(request):
    try:
        username = request.user.username
        return True if username in settings.ADMIN_USERNAME else False
    except:
        return False

def random_recommend():
    blogs = Blog.objects.all()
    random_blogs = random.sample(list(blogs), 1)
    return sorted(random_blogs, key=lambda x: x.publish_time, reverse=True)

def blog_index(request):
    """ 显示博客的列表 """
    blogs = Blog.objects.all()
    pages, blogs = getPages(request, blogs) #分页处理
    random_blogs = random_recommend()
    is_admin = check_admin_user(request)
    context = { 
        'blogs': blogs, 
        'pages': pages,  
        'random_blogs': random_blogs, 
        'is_admin': is_admin
    }
    return render(request, 'blog/blog_list.html', context)

@record_view(Blog)
def blog_show(request, blog_id):
    """ 显示单篇博客的内容 """
    cur_blog = Blog.objects.get(id=blog_id)
    if str("blog_%s_readed" % (blog_id)) not in request.COOKIES:
        cur_blog.read_num += 1
        cur_blog.save()

    pre_blog = Blog.objects.filter(id__gt=blog_id).order_by('id')
    next_blog = Blog.objects.filter(id__lt=blog_id).order_by('-id')

    pre_blog = pre_blog[0] if pre_blog.count() > 0 else None
    next_blog = next_blog[0] if next_blog.count() > 0 else None

    random_blogs = random_recommend()

    comments = Comment.objects.filter(blog__id=cur_blog.id).order_by('publish_time')

    is_admin = check_admin_user(request)

    context = {
        'cur_blog': cur_blog,
        'pre_blog': pre_blog,
        'next_blog': next_blog,
        'comments': comments,
        'random_blogs': random_blogs,
        'is_admin': is_admin,
    }
    response = render(request, 'blog/blog_single.html', context)
    # 这里设置在浏览器被关闭之前不会重新对博文阅读数量进行计数
    response.set_cookie("blog_%s_readed" % (blog_id),"True")
    return response

def new_blog(request):
    if not check_admin_user(request):
        raise Http404

    if request.method != 'POST':
        form = BlogForm()
    else:
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.author = request.user
            new_blog.save()

            tags_list = request.POST['tags'].split(';')
            for name in tags_list[:-1]:
                print("'"+name.strip()+"'")
                cur_tag = Tag.objects.get(tag_name=name.strip())
                new_blog.tags.add(cur_tag)
            
            new_blog.save()
            return HttpResponseRedirect(reverse('blog:blog_index'))
    
    tags = Tag.objects.all()
    context = { 'form': form, 'tags': tags }
    return render(request, 'blog/new_blog.html', context)

def delete_blog(request, blog_id):
    try:
        del_blog = Blog.objects.get(id=blog_id)
        del_blog.delete()
    finally:
        return HttpResponseRedirect(reverse('blog:blog_index'))

def edit_blog(request, blog_id):
    if not check_admin_user(request):
        raise Http404

    cur_blog = Blog.objects.get(id=blog_id)

    if request.method != 'POST':
        form = BlogForm(instance=cur_blog)
    else:
        form = BlogForm(instance=cur_blog, data=request.POST)
        if form.is_valid():
            form.save()

            for tag in cur_blog.tags.all():
                cur_blog.tags.remove(tag)

            tags_list = request.POST['tags'].split(';')
            for name in tags_list[:-1]:
                cur_tag = Tag.objects.get(tag_name=name.strip())
                cur_blog.tags.add(cur_tag)
            
            cur_blog.save()
            return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))

    tag_text = ""
    for tag in cur_blog.tags.all():
        tag_text += tag.tag_name + "; "

    tags = Tag.objects.all()
    context = {
        'blog': cur_blog,
        'form': form,
        'tags': tags,
        'tag_text': tag_text
    }
    return render(request, 'blog/edit_blog.html', context)

def manage_tags(request):
    if not check_admin_user(request):
        raise Http404

    tags = Tag.objects.all()
    context = { 'tags': tags }
    return render(request, 'blog/manage_tags.html', context)

def new_tag(request):
    try:
        tag_name = request.POST['new_tag_name']
        Tag.objects.create(tag_name=tag_name);
    finally:
        return HttpResponseRedirect(reverse('blog:manage_tags'))

def delete_tag(request, tag_id):
    try:
        del_tag = Tag.objects.get(id=tag_id)
        del_tag.delete()
    finally:
        return HttpResponseRedirect(reverse('blog:manage_tags'))

def edit_tag(request, tag_id):
    try:
        new_tag_name = request.POST['edit_tag_name']
        tag = Tag.objects.get(id=tag_id)
        tag.tag_name = new_tag_name
        tag.save()
    finally:
        return HttpResponseRedirect(reverse('blog:manage_tags'))

def new_comment(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    text = request.POST['comment_text']
    Comment.objects.create(blog=blog, author=request.user, content=text)
    print("blog_id", blog_id)
    return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))

def delete_comment(request, blog_id, comment_id):
    try:
        del_comment = Comment.objects.get(id=comment_id)
        print(del_comment)
        del_comment.delete()
    finally:
        return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))

def blog_search(request):
    try:
        wd = request.GET['wd']
        if not wd:
            return HttpResponseRedirect(reverse('blog:blog_index'))
    
        blogs = Blog.objects.filter(caption__icontains=wd)
        no_res = True if len(blogs) == 0 else False

        pages, blogs = getPages(request,blogs)

        is_admin = check_admin_user(request)
 
        context = { 
            'blogs': blogs, 
            'pages': pages, 
            'no_res': no_res,
            'is_admin': is_admin, 
            'wd': wd,
        }
        return render(request, 'blog/blog_list.html', context)
    except Exception:
        raise Http404