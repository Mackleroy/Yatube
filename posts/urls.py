from django.urls import path

from . import views

urlpatterns = [
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('user_posts/<str:username>/', views.MainPageView.as_view(), name='user_posts'),
    path('group_list/', views.GroupList.as_view(), name='group_list'),
    path('group/<slug:group_slug>/', views.MainPageView.as_view(), name='group'),
    path('', views.MainPageView.as_view(), name='main_page'),
]