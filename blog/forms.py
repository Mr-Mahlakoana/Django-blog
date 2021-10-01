from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment, Profile,Post
from django.forms import ModelForm

class CommentForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Add : Comment'
            }))

    class Meta:
        model = Comment
        fields = ['body',]

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,widget=forms.Textarea)


class CustomUserCreationForm(UserCreationForm):
    
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class UserForm(ModelForm):
    	class Meta:
		    model = User
		    fields = ['username', 'email']

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = '__all__'
		exclude = ['user']

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
