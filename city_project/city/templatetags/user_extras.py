from django import template
from ..utils import is_admin as _is_admin

register = template.Library()

@register.filter
def is_admin(user):
    return _is_admin(user)
