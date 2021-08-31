from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page

from follows.models import Follow
from .forms import PostForm, PostEditForm, AddCommentForm
from .models import Post, Group, Comment


class PaginatePage:
    """ Subclass for pagination of queryset"""
    def paginate(self, request, queryset):
        paginator = Paginator(queryset, 3)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        return paginator, page


@method_decorator(cache_page(60 * 3, key_prefix="main_page"), name='dispatch')
class MainPageView(View, PaginatePage):
    """Output of main page with all existing posts"""
    def get(self, request):
        posts = Post.objects.select_related('author', 'group').all().order_by(
            '-published_date')
        paginator, page = self.paginate(request, posts)
        return render(request, 'index.html',
                      {'page': page, 'paginator': paginator})


class GroupList(View):
    """Output of all existing and moderated groups"""
    def get(self, request):
        return render(request, 'group_list.html',
                      {'groups': Group.objects.filter(moderation=True)})


class GroupView(View, PaginatePage):
    """Posts output of exact group"""
    def get(self, request, group_slug):
        group = Group.objects.select_related('creator').get(slug=group_slug)
        posts = group.posts.select_related('author', 'group').all().order_by(
            '-published_date')
        paginator, page = self.paginate(request, posts)
        return render(request, 'group.html', {
            'group': group,
            'page': page,
            'paginator': paginator,
            'following': Follow.objects.filter(
                user=None if request.user.is_anonymous else request.user,
                group=group).exists()
        })


class ProfileView(View, PaginatePage):
    """Users profile with posts if they exist"""
    def get(self, request, username):
        try:
            posts = Post.objects.select_related('author', 'group').filter(
                author__username=username).order_by(
                '-published_date')
            author = posts.first().author
            paginator, page = self.paginate(request, posts)
            return render(request, 'profile.html', {
                'page': page,
                'paginator': paginator,
                'author': author,
                'following': Follow.objects.filter(
                    user=None if request.user.is_anonymous else request.user,
                    author=author).exists()
            })
        except AttributeError:
            author = User.objects.get(username=username)
            return render(request, 'profile.html', {
                'author': author,
                'following': Follow.objects.filter(
                    user=None if request.user.is_anonymous else request.user,
                    author=author).exists()
            })


class PostAndCommentView(View):
    """Individual post page with comments"""
    def get(self, request, username, post_slug):
        post = get_object_or_404(Post, author__username=username,
                                 slug=post_slug)
        return render(request, 'post.html', {
            'post': post,
            'comments': post.comments.all(),
            'form': AddCommentForm(),
            'author': post.author,
            'following': Follow.objects.filter(
                user=None if request.user.is_anonymous else request.user,
                author=post.author).exists()
        })

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
    """Post creation page"""
    def get(self, request):
        return render(request, 'create_edit_post.html', {
            'form': PostForm(),
            'title': 'Создание записи',
            'button': 'Создать'
            })

    def post(self, request):
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            form = form.save()
            form.author = request.user
            form.save()
            return redirect('/')
        else:
            return render(request, 'create_edit_post.html', {
                'form': form,
                'title': 'Создание записи',
                'button': 'Создать'
                })


@method_decorator(login_required, name='dispatch')
class PostEditView(View):
    """Edit post page"""
    def get(self, request, username, post_slug):
        post = Post.objects.get(slug=post_slug)
        if request.user.username == post.author.username:
            return render(request, 'create_edit_post.html',
                          {'form': PostEditForm(instance=post),
                           'post_slug': post_slug,
                           'title': 'Редактирование записи',
                           'button': 'Обновить'
                           })
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
            return render(request, 'create_edit_post.html', {
                'form': form,
                'post_slug': post_slug,
                'title': 'Редактирование записи',
                'button': 'Обновить'
            })


class DeletePostView(View):
    """Delete post page"""
    def post(self, request, post_slug):
        post = Post.objects.get(slug=post_slug)
        if request.user == post.author:
            post.delete()
        return redirect('profile', username=request.user.username)


class DeleteCommentView(View):
    """Delete post page"""
    def post(self, request, comment_pk):
        comment = Comment.objects.get(pk=comment_pk)
        if request.user == comment.author:
            comment.delete()
        return redirect('post_view', username=comment.post.author.username,
                        post_slug=comment.post.slug)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
