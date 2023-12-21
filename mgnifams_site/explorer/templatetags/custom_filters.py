# explorer/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='format_id')
def format_id(value):
    mgnifam_name = str(value).split('_')[0]
    return mgnifam_name

@register.filter(name='family_size')
def get_family_size(value):
    split_part = str(value).split('_')[1]
    size = split_part.split('-')[0]

    return size