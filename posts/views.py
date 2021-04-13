from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import PostForm, PostEditForm
from .models import Post, Group


class MainPageView(View):
    def get(self, request, group_slug=None, template='index.html'):
        context = {}
        posts = Post.objects.all().order_by('-published_date')
        if group_slug is not None:
            posts = posts.filter(group__slug=group_slug)
            group = Group.objects.get(slug=group_slug)
            template = 'group.html'
            context['group'] = group
        first_post = posts.first()
        paginator = Paginator(posts.exclude(id=first_post.id), 3)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        context['paginator'] = paginator
        context['post'] = first_post
        return render(request, template, context)


class CreatePostView(View):
    def get(self, request):
        form = PostForm
        return render(request, 'create_edit_post.html', {'form': form, 'title': 'Создание записи', 'button': 'Создать'})

    def post(self, request):
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            form = form.save()
            form.author = request.user
            form.save()
            return redirect('/')
        # else:
        #     return redirect(request.path)


class GroupList(View):
    def get(self, request):
        return render(request, 'group_list.html')


class ProfileView(View):
    def get(self, request, username):
        posts = Post.objects.filter(author__username=username).order_by('-published_date')
        if posts:
            first_post = posts.first()
            paginator = Paginator(posts.exclude(id=first_post.id), 3)
            page_number = request.GET.get('page')
            page = paginator.get_page(page_number)
            return render(request, 'profile.html', {'post': first_post, 'page': page, 'paginator': paginator})
        else:
            return render(request, 'profile.html')


class PostView(View):
    def get(self, request, username, post_slug):
        post = get_object_or_404(Post, author__username=username, slug=post_slug)
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
        form = PostEditForm(request.POST, files=request.FILES or None)
        post = Post.objects.get(slug=post_slug)
        if form.is_valid():
            post.group = form.cleaned_data['group']
            post.title = form.cleaned_data['title']
            post.text = form.cleaned_data['text']
            post.image = form.cleaned_data['image']
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


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
