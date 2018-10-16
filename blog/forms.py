from django import forms
#from markdown import MarkdownFormField
from blog.models import Tag, Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = [
            'caption',
            'content',
        ]
        labels = {
            'caption': 'Caption',
            'content': 'Content',
        }