from django.contrib import admin

from .models import Post, Group, Comment


class ActionsAdmin(admin.ModelAdmin):
    """Adding functionality to publish and unpublish objects """
    def unpublish(self, request, queryset):
        queryset.update(moderation=False)

    unpublish.short_description = 'Снять с публикации'
    unpublish.allowed_permissions = ('change',)

    def publish(self, request, queryset):
        queryset.update(moderation=True)

    publish.short_description = 'Опубликавать'
    publish.allowed_permissions = ('change',)


class PostsInline(admin.StackedInline):
    """Add 1 more post for easy creation"""
    model = Post
    extra = 1


@admin.register(Post)
class PostAdmin(ActionsAdmin):
    """Class for proper look and work with Post model"""
    list_display = ('title', 'author', 'group', 'published_date', 'moderation')
    list_filter = ('author', 'group', 'published_date', 'moderation')
    search_fields = ('title', 'author', 'group')
    list_editable = ('moderation', 'author')
    actions = ['unpublish', 'publish']


@admin.register(Group)
class GroupAdmin(ActionsAdmin):
    """Class for proper look and work with Group model"""
    list_display = ('title', 'creator', 'slug', 'template', 'moderation')
    list_filter = ('title', 'moderation')
    search_fields = ('title', )
    list_editable = ('moderation', 'creator')
    inlines = [PostsInline]
    actions = ['unpublish', 'publish']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Class for proper look and work with Comment model"""
    list_display = ('post', 'author', 'text', 'published_date')
    list_filter = ('post', 'author', 'published_date')
    search_fields = ('user', 'author')