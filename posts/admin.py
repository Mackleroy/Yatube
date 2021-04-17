from django.contrib import admin

from .models import Post, Group, Comment, Follow


class ActionsAdmin(admin.ModelAdmin):
    def unpublish(self, request, queryset):
        queryset.update(moderation=False)

    unpublish.short_description = 'Снять с публикации'
    unpublish.allowed_permissions = ('change',)

    def publish(self, request, queryset):
        queryset.update(moderation=True)

    publish.short_description = 'Опубликавать'
    publish.allowed_permissions = ('change',)


class PostsInline(admin.StackedInline):
    model = Post
    extra = 1


@admin.register(Post)
class PostAdmin(ActionsAdmin):
    list_display = ('title', 'author', 'group', 'published_date', 'moderation')
    list_filter = ('author', 'group', 'published_date', 'moderation')
    search_fields = ('title', 'author', 'group')
    list_editable = ('moderation', 'author')
    actions = ['unpublish', 'publish']


@admin.register(Group)
class GroupAdmin(ActionsAdmin):
    list_display = ('title', 'creator', 'slug', 'template', 'moderation')
    list_filter = ('title', 'moderation')
    search_fields = ('title', )
    list_editable = ('moderation', 'creator')
    inlines = [PostsInline]
    actions = ['unpublish', 'publish']


@admin.register(Comment)
class CommentAdmin(ActionsAdmin):
    list_display = ('post', 'author', 'published_date', 'text')
    list_filter = ('post', 'author', 'published_date')
    search_fields = ('post', 'author', 'published_date', 'text')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'group')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
