import datetime as dt
import os
from os.path import exists

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse


from posts.models import Post, Group


class TestClient:
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.title = 'Тестовый заголовок'
        self.text = 'Текст тестового поста'
        self.slug = 'test_slug'
        self.urls_to_check = {'post_view': [self.username, self.slug], 'profile': [self.username],
                              'main_page': []
                              }
        cache.clear()

    def tearDown(self):
        self.user.delete()


class PostTests(TestClient, TestCase):
    def test_publication_on_all_pages(self):
        self.client.login(username=self.username, password=self.password)
        self.client.post(reverse('create_post'), data={
            'title': self.title,
            'text': self.text,
            'slug': self.slug
        })
        for url, args in self.urls_to_check.items():
            try:
                response = self.client.get(reverse(url, args=args))
                self.assertContains(response, self.title and self.text)
            except AssertionError as ae:
                ae.args += (f'Ошибка в url: {url}',)
                raise


class UserPublishPost(TestClient, TestCase):
    def test_auth_user_can_post(self):
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 200)

    def test_not_auth_user_cant_post(self):
        self.client.get(reverse('logout'))
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 302)

    def test_auth_user_can_edit_and_all_pages_change(self):
        title_new = 'Тестовый новый заголовок'
        text_new = 'Новый текст тестового поста'
        Post.objects.create(author=self.user,
                            title=self.title,
                            text=self.text,
                            slug=self.slug)
        self.client.get(reverse('post_edit', args=[self.username, self.slug]))
        self.client.post(reverse('post_edit', args=[self.username, self.slug]), data={
            'title': title_new,
            'text': text_new
        })
        for url, args in self.urls_to_check.items():
            try:
                response = self.client.get(reverse(url, args=args))
                self.assertContains(response, title_new and text_new)
            except AssertionError as ae:
                ae.args += (f'Ошибка в url: {url}',)
                raise


class RegistrationAndProfilePageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'

    def test_registration_and_profile_page(self):
        response_reg = self.client.post(reverse('signup'), data={
            'username': self.username,
            'password1': self.password,
            'password2': self.password
        })
        self.assertEqual(response_reg.status_code, 302)
        self.assertEqual(response_reg.url, '/auth/login/')
        self.client.login(username=self.username, password=self.password)
        response_profile = self.client.get('/{0}/'.format(self.username))
        self.assertEqual(response_profile.status_code, 200)
        self.assertContains(response_profile, self.username)


class ErrorsTest(TestCase):
    def test_404(self):
        response = self.client.get(reverse('post_view', args=['not_existing_user', 'not_existing_post_slug']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')


class ImagesTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.slug = 'test_slug'
        self.group_slug = 'test_group_slug'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.group = Group.objects.create(title='test_group', slug=self.group_slug)
        self.post = Post.objects.create(author=self.user, group=self.group, text='test', title='test', slug=self.slug)
        self.urls_to_check = {'post_view': [self.username, self.slug],
                              'profile': [self.username],
                              'group': [self.group_slug],
                              'main_page': []}

    def tearDown(self) -> None:
        if exists('media/posts/test_img.jpg'):
            os.remove('media/posts/test_img.jpg')

    def test_image_exists(self):
        with open('media/test/test_img.jpg', 'rb') as img:
            self.client.post(reverse('post_edit', args=[self.username, self.slug]), data={
                'author': self.user,
                'group': self.group.id,
                'text': 'test',
                'title': 'new_title',
                'slug': self.slug,
                'image': img,
            })
        cache.clear()
        for url, args in self.urls_to_check.items():
            try:
                response = self.client.get(reverse(url, args=args))
                self.assertContains(response, '<img')
            except AssertionError as ae:
                ae.args += (f'Ошибка в url: {url}',)
                raise

    def test_invalid_file_to_image_field(self):
        with open('media/test/test.txt', 'rb') as img:
            response = self.client.post(reverse('post_edit', args=[self.username, self.slug]), data={
                'author': self.user,
                'group': self.group.id,
                'text': 'test',
                'title': 'new_title',
                'slug': self.slug,
                'image': img,
            })
        self.assertEqual(response.url, '/testuser/test_slug/edit/')


class CacheTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='difficult_password')
        cache.clear()
        for i in range(5):
            Post.objects.create(title=f'Title{i}', text=f'Text{i}', slug=f'slug_{i}', author=self.user)

    def tearDown(self) -> None:
        cache.delete('main_page')

    def test_visit_main_page(self):
        start_time1 = dt.datetime.now()
        self.client.get(reverse('main_page'))
        duration1 = dt.datetime.now() - start_time1

        start_time2 = dt.datetime.now()
        self.client.get(reverse('main_page'))
        duration2 = dt.datetime.now() - start_time2
        self.assertTrue(duration1/2 > duration2)

    def test_delay_new_post(self):
        self.client.get(reverse('main_page'))
        i = '_delay'
        post = Post.objects.create(title=f'Title{i}', text=f'Text{i}', slug=f'slug_{i}', author=self.user)
        response = self.client.get(reverse('main_page'))
        self.assertNotContains(response, post.title and post.text)

