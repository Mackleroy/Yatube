from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View

from .forms import PostForm
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
        return render(request, 'create_post.html', {'form': form})

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
