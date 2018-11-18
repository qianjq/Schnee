from django import forms
#from markdown import MarkdownFormField
from sonata.models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'caption',
            'content',
        ]
        labels = {
            'caption': 'Caption',
            'content': ''
        }