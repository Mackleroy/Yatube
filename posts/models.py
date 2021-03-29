from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    title = models.CharField("Заголовок", max_length=70)
    creator = models.ForeignKey(User, verbose_name="Создатель", on_delete=models.CASCADE, max_length=70, null=True)
    slug = models.SlugField("url", max_length=30)
    description = models.TextField("Описание", max_length=500)
    template = models.CharField("Шаблон", max_length=100, default='group.html')
    moderation = models.BooleanField('Модерация', default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE, max_length=70, null=True)
    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст", max_length=5000)
    published_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    moderation = models.BooleanField("Модерация", default=True)
    slug = models.SlugField("url", max_length=30)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
