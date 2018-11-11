from django import forms
#from markdown import MarkdownFormField
from users.models import UserInfo, Message


#class ProfileForm(forms.Form):
 #   upProfile = forms.FileField()

class InfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = [
            'nickname',
            'gender',
            'language',
            'email',
            'intro',
        
        ]
        labels = {
            'nickname': 'Nickname',
            'gender': 'Gender',
            'language': 'Language',
            'email': 'Email',
            'intro': 'User introduce',
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = [
            'text'
        ]
        labels = {
            'text': 'Content'
        }

