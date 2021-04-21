from django.urls import path

from follows import views

urlpatterns = [
    path('<str:username>/', views.FollowsView.as_view(),
         name='your_follows'),
    path('<str:username>/follow/', views.FollowView.as_view(), name='follow'),
    path('<str:username>/unfollow/', views.UnfollowView.as_view(),
         name='unfollow'),
    path('<str:group_slug>/group/follow/', views.FollowView.as_view(),
         name='follow_group'),
    path('<str:group_slug>/group/unfollow/', views.UnfollowView.as_view(),
         name='unfollow_group'),
]