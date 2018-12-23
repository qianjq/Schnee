# -*- coding: utf-8 -*-
import markdown
import markdownx
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist

from users.models import UserInfo
from blog.models import Blog, Comment
from sonata.models import Article
from helper.update_data import update_userInfo_unread_count

register = template.Library()

@register.filter
def getUnreadCount(user):
    try:
        update_userInfo_unread_count(user)
        info = UserInfo.objects.get(user=user)
    except ObjectDoesNotExist:
        return 0
    else:
        return info.unread_count

@register.filter(is_safe = True)
@stringfilter
def custom_markdown(value):
    return mark_safe(markdown.markdown(value,
                              extensions = ['markdown.extensions.extra',
                                            'markdown.extensions.toc',
                                            'markdown.extensions.sane_lists',
                                            'markdown.extensions.nl2br',
                                            'markdown.extensions.codehilite',],
                              safe_mode = True,
                              enable_attributes = False))

@register.filter(is_safe = True)
@stringfilter
def get_all_blog_tags(blog_id):
    blog = Blog.objects.get(id=blog_id)
    tag_names = []
    for tag in blog.tags.all():
        tag_names.append(tag.tag_name)
    return tag_names


@register.filter(is_safe = True)
@stringfilter
def get_comment_count(blog_id):
    blog = Blog.objects.get(id=blog_id)
    return blog.comment_set.count()


@register.filter(is_safe = True)
@stringfilter
def get_all_article_tags(article_id):
    article = Article.objects.get(id=article_id)
    tag_names = []
    for tag in article.tags.all():
        tag_names.append(tag.tag_name)
    return tag_names

@register.filter(is_safe = True)
@stringfilter
def get_article_comment_count(atricle_id):
    article = Article.objects.get(id=atricle_id)
    return article.art_comment_set.count()


@register.filter(is_safe = True)
@stringfilter
def get_friends(info_id):
    info = UserInfo.objects.get(id=info_id)
    friends = []
    for friend in info.friends.all():
        friends.append(friend)
    return friends

@register.filter(is_safe = True)
def reply_set(comment_id):
    comment = Comment.objects.get(id=comment_id)
    return comment.reply_set.all()