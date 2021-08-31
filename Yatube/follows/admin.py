from django.contrib import admin

from follows.models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Class for proper look and work with Follow model"""
    list_display = ('user', 'author', 'group')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
