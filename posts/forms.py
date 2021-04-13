from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'title', 'text', 'image', 'slug')


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'title', 'text', 'image')
