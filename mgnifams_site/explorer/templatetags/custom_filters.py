# explorer/templatetags/custom_filters.py

from django import template

from explorer.utils import format_family_name

register = template.Library()


@register.filter
def format_mgnifam_name(raw_name):
    return format_family_name(raw_name)
