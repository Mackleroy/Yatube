from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import PostForm, PostEditForm
from .models import Post, Group


class MainPageView(View):
    def get(self, request, group_slug=None, username=None, template='index.html'):
        context = {}
        posts = Post.objects.all().order_by('-published_date')
        if group_slug is not None:
            posts = posts.filter(group__slug=group_slug)
            group = Group.objects.get(slug=group_slug)
            context['group'] = group
        if username is not None:
            user = User.objects.get(username=username)
            posts = posts.filter(author_id=user)
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        return render(request, template, {'page': page, 'paginator': paginator})


class CreatePostView(View):
    def get(self, request):
        form = PostForm
        return render(request, 'create_edit_post.html', {'form': form, 'title': 'Создание записи', 'button': 'Создать'})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            form = form.save()
            form.author = request.user
            form.save()
            return redirect('/')


class GroupList(View):
    def get(self, request):
        return render(request, 'group_list.html')


class ProfileView(View):
    def get(self, request, username):
        posts = Post.objects.filter(author__username=username).order_by('-published_date')
        if posts:
            last_post = posts.first()
            paginator = Paginator(posts, 3)
            page_number = request.GET.get('page')
            page = paginator.get_page(page_number)
            return render(request, 'profile.html', {'post': last_post, 'page': page, 'paginator': paginator})
        else:
            return render(request, 'profile.html')


class PostView(View):
    def get(self, request, username, post_slug):
        post = Post.objects.get(author__username=username, slug=post_slug)
        return render(request, 'post.html', {'post': post})


class PostEditView(View):
    def get(self, request, username, post_slug):
        post = Post.objects.get(slug=post_slug)
        form = PostEditForm(instance=post)
        if request.user.username == post.author.username:
            return render(request, 'create_edit_post.html', {'form': form,
                                                             'post_slug': post_slug,
                                                             'title': 'Редактирование записи',
                                                             'button': 'Обновить'}
                          )
        else:
            return redirect('post_view', username=username, post_slug=post_slug)

    def post(self, request, username, post_slug):
        form = PostEditForm(request.POST)
        post = Post.objects.get(slug=post_slug)
        if form.is_valid():
            post.group = form.cleaned_data['group']
            post.title = form.cleaned_data['title']
            post.text = form.cleaned_data['text']
            post.save()
            return redirect('/')
        else:
            return redirect(request.path)


class DeletePostView(View):
    def get(self, request, post_slug):
        post = Post.objects.get(slug=post_slug)
        if request.user.username == post.author.username:
            post.delete()
        return redirect('profile', username=request.user.username)
