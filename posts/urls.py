from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main_page'),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('delete_post/<slug:post_slug>/', views.DeletePostView.as_view(), name='delete_post'),
    path('delete_comment/<int:comment_pk>/', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('user_posts/<str:username>/', views.MainPageView.as_view(), name='user_posts'),
    path('<str:username>/follows/', views.FollowsView.as_view(), name='your_follows'),
    path('<str:username>/follow/', views.FollowView.as_view(), name='follow'),
    path('<str:username>/unfollow/', views.UnfollowView.as_view(), name='unfollow'),
    path('<str:group_slug>/group/follow/', views.FollowView.as_view(), name='follow_group'),
    path('<str:group_slug>/group/unfollow/', views.UnfollowView.as_view(), name='unfollow_group'),
    path('group_list/', views.GroupList.as_view(), name='group_list'),
    path('group/<slug:group_slug>/', views.GroupView.as_view(), name='group'),
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('<str:username>/<slug:post_slug>/', views.PostAndCommentView.as_view(), name='post_view'),
    path('<str:username>/<slug:post_slug>/edit/', views.PostEditView.as_view(), name='post_edit'),
    path('<str:username>/<slug:post_slug>/comment/', views.PostAndCommentView.as_view(), name='add_comment'),
]