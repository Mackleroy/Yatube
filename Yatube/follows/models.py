from django.contrib.auth.models import User
from django.db import models

from posts.models import Group


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name="Автор",
                             on_delete=models.CASCADE, blank=True,
                             null=True, related_name='follower', )
    group = models.ForeignKey(Group, verbose_name="Группа",
                              on_delete=models.CASCADE, blank=True,
                              null=True, related_name='following')
    author = models.ForeignKey(User, verbose_name="Автор",
                               on_delete=models.CASCADE, max_length=70,
                               null=True, related_name='following')

    def __str__(self):
        try:
            return self.group.title
        except AttributeError:
            return self.author.username

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'