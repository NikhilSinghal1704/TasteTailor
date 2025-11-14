from django import template

register = template.Library()

@register.filter
def is_list(value):
    """Check if a value is a list or tuple"""
    return isinstance(value, (list, tuple))

@register.filter
def split(value, sep):
    return value.split(sep)
