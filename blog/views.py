from django.shortcuts import render
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, Http404

from helper.paginator import getPages
from blog.models import Blog, Tag
from blog.forms import BlogForm

def check_admin_user(request):
    try:
        username = request.user.username
        return True if username in settings.ADMIN_USERNAME else False
    except Exception as e:
        return False
        
# Create your views here.
def blog_index(request):
    """ 显示博客的列表 """
    blogs = Blog.objects.all()
    pages, blogs = getPages(request, blogs) #分页处理
    is_admin = check_admin_user(request)
    # print(is_admin)
    context = { 'blogs': blogs, 'pages': pages, 'is_admin': is_admin }
    return render(request, 'blog/blog_list.html', context)

def blog_show(request, blog_id):
    """ 显示单篇博客的内容 """
    cur_blog = Blog.objects.get(id=blog_id)
    cur_blog.read_num += 1
    cur_blog.save()

    pre_blog = Blog.objects.filter(id__gt=blog_id).order_by('id')
    next_blog = Blog.objects.filter(id__lt=blog_id).order_by('-id')

    pre_blog = pre_blog[0] if pre_blog.count() > 0 else None
    next_blog = next_blog[0] if next_blog.count() > 0 else None

    is_admin = check_admin_user(request)

    context = {
        'cur_blog': cur_blog,
        'pre_blog': pre_blog,
        'next_blog': next_blog,
        'is_admin': is_admin
    }
    return render(request, 'blog/blog_single.html', context)

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
            return HttpResponseRedirect(reverse('blog:blog_index'))
    
    context = { 'form': form }
    return render(request, 'blog/new_blog.html', context)

def edit_blog(request, blog_id):
    if not check_admin_user(request):
        raise Http404

    blog = Blog.objects.get(id=blog_id)

    if request.method != 'POST':
        form = BlogForm(instance=blog)
    else:
        form = BlogForm(instance=blog, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('blog:blog_show', args=[blog_id]))
    context = {
        'blog': blog,
        'form': form
    }
    return render(request, 'blog/edit_blog.html', context)