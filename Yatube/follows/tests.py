from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from follows.models import Follow
from posts.models import Group, Post


class FollowUnfollowTest(TestCase):
    """Test auth/not auth user can subscribe/unsubscribe and see followed posts"""
    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.author = User.objects.create_user(username='author_username',
                                               password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.group = Group.objects.create(title='test_group',
                                          slug='test_group_slug')

    def test_auth_user_can_follow_or_unfollow_author(self):
        response_profile = self.client.get(
            reverse('profile', args=[self.author.username]))
        self.assertContains(response_profile, 'Подписаться')

        self.client.post(reverse('follow', args=[self.author.username]))
        response_profile2 = self.client.get(
            reverse('profile', args=[self.author.username]))
        self.assertContains(response_profile2, 'Отписаться')

        self.client.post(reverse('unfollow', args=[self.author.username]))
        response_profile2 = self.client.get(
            reverse('profile', args=[self.author.username]))
        self.assertContains(response_profile2, 'Подписаться')

    def test_auth_user_can_follow_or_unfollow_group(self):
        response_profile = self.client.get(
            reverse('group', args=[self.group.slug]))
        self.assertContains(response_profile, 'Подписаться')

        self.client.post(reverse('follow_group', args=[self.group.slug]))
        response_profile2 = self.client.get(
            reverse('group', args=[self.group.slug]))
        self.assertContains(response_profile2, 'Отписаться')

        self.client.post(reverse('unfollow_group', args=[self.group.slug]))
        response_profile2 = self.client.get(
            reverse('group', args=[self.group.slug]))
        self.assertContains(response_profile2, 'Подписаться')

    def test_not_auth_user_can_not_follow_or_unfollow(self):
        self.client.logout()
        response = self.client.get(
            reverse('profile', args=[self.author.username]))
        self.assertNotContains(response, 'Подписаться' or 'Отписаться')

    def test_new_post_can_see_only_followers(self):
        Follow.objects.create(user=self.user, author=self.author)
        Post.objects.create(author=self.author, text='test', title='new_title',
                            slug='slug')
        response = self.client.get(
            reverse('your_follows', args=[self.user.username]))
        self.assertContains(response, 'test' and 'new_title')

        not_follower = Client()
        user2 = User.objects.create_user(username='not_follower',
                                         password=self.password)
        not_follower.login(username='not_follower', password=self.password)
        response = not_follower.get(
            reverse('your_follows', args=[user2.username]))
        self.assertNotContains(response, 'test' and 'new_title')
