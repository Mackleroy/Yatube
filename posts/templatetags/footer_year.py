import datetime

from django import template

register = template.Library()


@register.simple_tag()
def year():
    current_year = datetime.datetime.today().year
    return current_year
