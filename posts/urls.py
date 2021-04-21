from django.urls import path

from . import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main_page'),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('delete_post/<slug:post_slug>/', views.DeletePostView.as_view(),
         name='delete_post'),
    path('delete_comment/<int:comment_pk>/', views.DeleteCommentView.as_view(),
         name='delete_comment'),
    path('group_list/', views.GroupList.as_view(), name='group_list'),
    path('group/<slug:group_slug>/', views.GroupView.as_view(), name='group'),
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('<str:username>/<slug:post_slug>/', views.PostAndCommentView.as_view(),
         name='post_view'),
    path('<str:username>/<slug:post_slug>/edit/', views.PostEditView.as_view(),
         name='post_edit'),
    path('<str:username>/<slug:post_slug>/comment/',
         views.PostAndCommentView.as_view(), name='add_comment'),
]
