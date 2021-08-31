from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Post creation form"""
    class Meta:
        model = Post
        fields = ('group', 'title', 'text', 'image', 'slug')


class PostEditForm(forms.ModelForm):
    """Post edit form"""
    class Meta:
        model = Post
        fields = ('group', 'title', 'text', 'image')


class AddCommentForm(forms.ModelForm):
    """Comment add form"""
    class Meta:
        model = Comment
        fields = ('text',)
