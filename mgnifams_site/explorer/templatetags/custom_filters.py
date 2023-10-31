# explorer/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='format_id')
def format_id(value):
    formatted_value = str(value).zfill(12)
    return "MGYP" + formatted_value
