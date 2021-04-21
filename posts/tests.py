import os
from os.path import exists

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, Comment


class TestManyUrlsToCheck:
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.title = 'Тестовый заголовок'
        self.text = 'Текст тестового поста'
        self.slug = 'test_slug'
        self.urls_to_check = {'post_view': [self.username, self.slug],
                              'profile': [self.username],
                              'main_page': []
                              }
        cache.clear()

    def tearDown(self):
        self.user.delete()


class PostTests(TestManyUrlsToCheck, TestCase):
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


class UserPublishPost(TestManyUrlsToCheck, TestCase):
    def test_auth_user_can_post(self):
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 200)

    def test_not_auth_user_cant_post(self):
        self.client.logout()
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
        self.client.post(reverse('post_edit', args=[self.username, self.slug]),
                         data={
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

    def test_post_invalid_data(self):
        response = self.client.post(reverse('create_post'), data={
            'title': 'title_new',
            'text': 'text_new',
            'author': self.user,
            'slug': 'wrong*%#slug'
        })
        self.assertTemplateUsed(response, 'create_edit_post.html')


class RegistrationTests(TestCase):
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
        response_profile = self.client.get(
            reverse('profile', args=[self.username]))
        self.assertEqual(response_profile.status_code, 200)
        self.assertContains(response_profile, self.username)


class ErrorsTest(TestCase):
    def test_404(self):
        response = self.client.get(reverse('post_view',
                                           args=['not_existing_user',
                                                 'not_existing_post_slug']))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')


class ImagesTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.slug = 'test_slug'
        self.group_slug = 'test_group_slug'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.group = Group.objects.create(title='test_group',
                                          slug=self.group_slug)
        self.post = Post.objects.create(author=self.user, group=self.group,
                                        text='test', title='test',
                                        slug=self.slug)
        self.urls_to_check = {'post_view': [self.username, self.slug],
                              'profile': [self.username],
                              'group': [self.group_slug],
                              'main_page': []}
        cache.clear()

    def tearDown(self) -> None:
        if exists('media/posts/test_img.jpg'):
            os.remove('media/posts/test_img.jpg')

    def test_image_exists(self):
        with open('media/test/test_img.jpg', 'rb') as img:
            self.client.post(
                reverse('post_edit', args=[self.username, self.slug]),
                data={
                    'author': self.user,
                    'group': self.group.id,
                    'text': 'test',
                    'title': 'new_title',
                    'slug': self.slug,
                    'image': img,
                })

        for url, args in self.urls_to_check.items():
            try:
                response = self.client.get(reverse(url, args=args))
                self.assertContains(response, '<img')
            except AssertionError as ae:
                ae.args += (f'Ошибка в url: {url}',)
                raise

    def test_invalid_file_to_image_field(self):
        with open('media/test/test.txt', 'rb') as img:
            response = self.client.post(
                reverse('post_edit', args=[self.username, self.slug]), data={
                    'author': self.user,
                    'group': self.group.id,
                    'text': 'test',
                    'title': 'new_title',
                    'slug': self.slug,
                    'image': img,
                })
        self.assertTemplateUsed(response, 'create_edit_post.html')


class CacheTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='difficult_password')
        cache.clear()
        for i in range(5):
            Post.objects.create(title=f'Title{i}', text=f'Text{i}',
                                slug=f'slug_{i}', author=self.user)

    def test_visit_main_page(self):
        with self.assertNumQueries(2):
            response = self.client.get(reverse('main_page'))
            self.assertEqual(response.status_code, 200)
            response = self.client.get(reverse('main_page'))
            self.assertEqual(response.status_code, 200)

    def test_delay_new_post(self):
        self.client.get(reverse('main_page'))
        post = Post.objects.create(title=f'Title_delay', text=f'Text_delay',
                                   slug=f'slug_delay', author=self.user)
        response = self.client.get(reverse('main_page'))
        self.assertNotContains(response, post.title and post.text)


class CommentsTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.post = Post.objects.create(author=self.user, text='test',
                                        title='new_title', slug='slug')

    def test_not_auth_user_can_not_comment(self):
        self.client.logout()
        response = self.client.get(
            reverse('post_view', args=[self.user.username, self.post.slug]))
        self.assertNotContains(response, 'Добавить комментарий' and 'Отправить')

    def test_auth_user_can_comment(self):
        response = self.client.post(
            reverse('post_view', args=[self.user.username, self.post.slug]),
            data={
                'post': self.post,
                'author': self.user,
                'text': 'Test_comment'
            })
        self.assertEqual(response.status_code, 302)
        response_check = self.client.get(
            reverse('post_view', args=[self.user.username, self.post.slug]))
        self.assertContains(response_check, 'Test_comment')

    def test_user_can_delete_his_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.user,
                                         text='text')
        self.client.post(reverse('delete_comment', args=[comment]))
        self.assertEqual(Comment.objects.all().count(), 0)


class GroupListTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.group = Group.objects.create(title='test_group1',
                                          slug='test_group_slug1')
        self.group = Group.objects.create(title='test_group2',
                                          slug='test_group_slug2')

    def test_group_list(self):
        response = self.client.get(reverse('group_list'))
        self.assertContains(response,
                            'test_group1' and 'test_group_slug1' and
                            'test_group2' and 'test_group_slug2')


class DeletePostTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.author = User.objects.create_user(username='author',
                                               password=self.password)
        self.your_post = Post.objects.create(author=self.user, text='test',
                                             title='new_title', slug='slug')
        self.not_your_post = Post.objects.create(author=self.author,
                                                 text='test2',
                                                 title='new_title2',
                                                 slug='slug2')

    def test_user_can_delete_his_post(self):
        self.client.post(reverse('delete_post', args=[self.your_post.slug]))
        self.assertEqual(Post.objects.all().count(), 1)

    def test_user_can_not_delete_not_his_post(self):
        self.client.post(reverse('delete_post', args=[self.not_your_post.slug]))
        self.assertEqual(Post.objects.all().count(), 2)


class Profile(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.username = 'testuser'
        self.password = 'difficult_password'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_profile_with_posts(self):
        Post.objects.create(author=self.user, text='test', title='new_title',
                            slug='slug')
        response = self.client.get(
            reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)

    def test_profile_without_posts(self):
        response = self.client.get(
            reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
