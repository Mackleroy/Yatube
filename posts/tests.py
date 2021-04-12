from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post


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
        self.urls_to_check = {'post_view': [self.username, self.slug], 'profile': [self.username], 'main_page': []}

    def tearDown(self):
        self.user.delete()


class PostTests(TestClient, TestCase):
    def test_publication_on_all_pages(self):
        title = 'Тестовый заголовок'
        text = 'Текст тестового поста'
        slug = 'test_slug'
        self.client.login(username=self.username, password=self.password)
        self.client.post(reverse('create_post'), data={
            'title': title,
            'text': text,
            'slug': slug
        })

        for url, value in self.urls_to_check.items():
            response = self.client.get(reverse(url, args=value))
            self.assertContains(response, title and text)


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
        for url, value in self.urls_to_check.items():
            response = self.client.get(reverse(url, args=value))
            self.assertContains(response, title_new and text_new)


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
