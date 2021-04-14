from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page

from .forms import PostForm, PostEditForm, AddCommentForm
from .models import Post, Group, Comment


@method_decorator(cache_page(60 * 15, key_prefix="main_page"), name='dispatch')
class MainPageView(View):
    def get(self, request, group_slug=None, template='index.html'):
        context = {}
        posts = Post.objects.select_related('author', 'group').all().order_by('-published_date')
        if group_slug is not None:
            posts = posts.filter(group__slug=group_slug)
            group = Group.objects.get(slug=group_slug)
            template = 'group.html'
            context['group'] = group
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page
        context['paginator'] = paginator
        return render(request, template, context)


class GroupList(View):
    def get(self, request):
        groups = Group.objects.filter(moderation=True)
        return render(request, 'group_list.html', {'groups': groups})


class ProfileView(View):
    def get(self, request, username):
        posts = Post.objects.select_related('author', 'group').filter(author__username=username).order_by('-published_date')
        if posts:
            paginator = Paginator(posts, 3)
            page_number = request.GET.get('page')
            page = paginator.get_page(page_number)
            return render(request, 'profile.html', {'page': page, 'paginator': paginator})
        else:
            return render(request, 'profile.html')


class PostAndCommentView(View):
    def get(self, request, username, post_slug):
        post = get_object_or_404(Post, author__username=username, slug=post_slug)
        comments = Comment.objects.filter(post=post)
        form = AddCommentForm()
        return render(request, 'post.html', {'post': post, 'comments': comments, 'form': form})

    def post(self, request, username, post_slug):
        form = AddCommentForm(request.POST)
        if form.is_valid():
            form = form.save()
            form.post = Post.objects.get(slug=post_slug)
            form.author = request.user
            form.save()
        return redirect(request.path)


@method_decorator(login_required, name='dispatch')
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
        else:
            return redirect(request.path)


@method_decorator(login_required, name='dispatch')
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


class DeleteCommentView(View):
    def post(self, request, comment_pk):
        comment = Comment.objects.get(pk=comment_pk)
        post = comment.post
        comment.delete()
        return redirect('post_view', username=post.author, post_slug=post.slug)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
