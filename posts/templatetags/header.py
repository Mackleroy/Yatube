from posts.models import Group
from django import template

register = template.Library()


@register.simple_tag()
def header():
    groups = Group.objects.filter(moderation=True)
    return groups
