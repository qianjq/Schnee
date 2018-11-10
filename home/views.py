from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, StreamingHttpResponse, HttpResponse
from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from helper.update_data import update_userInfo_unread_count

    
# Create your views here.
def index(requset):
    return render(requset, 'home/index.html')

def home(request):
    try:
        update_userInfo_unread_count(request.user)
    finally:
        return render(request, 'home/home.html')

def gallery(request):
    return render(request, 'home/gallery.html')

def lab(request):
    return render(request, 'home/lab.html')

def about(request):
    return render(request, 'home/about.html')

def test_page(request):
    return render(request, 'home/test_page.html')

def developing(request):
    return render(request, 'home/developing.html')