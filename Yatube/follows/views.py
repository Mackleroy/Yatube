from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View

from follows.models import Follow
from posts.models import Post, Group
from posts.views import PaginatePage


class FollowsView(View, PaginatePage):
    def get(self, request, username):
        posts = Post.objects.select_related('author', 'group').filter(
            Q(author__following__user=request.user) |
            Q(group__following__user=request.user)
        ).order_by('-published_date').distinct()
        paginator, page = self.paginate(request, posts)
        return render(request, 'index.html',
                      {'page': page, 'paginator': paginator})


class FollowView(View):
    def post(self, request, username=None, group_slug=None):
        if group_slug is not None:
            Follow.objects.create(user=request.user,
                                  group=Group.objects.get(slug=group_slug))
            return redirect('group', group_slug)
        elif username is not None:
            Follow.objects.create(user=request.user,
                                  author=User.objects.get(username=username))
            return redirect('profile', username)


class UnfollowView(View):
    def post(self, request, username=None, group_slug=None):
        if group_slug is not None:
            Follow.objects.get(user=request.user,
                               group__slug=group_slug).delete()
            return redirect('group', group_slug)
        elif username is not None:
            Follow.objects.get(user=request.user,
                               author__username=username).delete()
            return redirect('profile', username)

