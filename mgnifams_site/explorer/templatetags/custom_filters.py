# explorer/templatetags/custom_filters.py

from django import template

register = template.Library()


@register.filter
def format_mgnifam_name(raw_name):
    """
    Formats the mgnifam name by appending zeros in front to make it 10 characters,
    and then adds 'MGYF' as a prefix.
    """
    if raw_name is None:
        return ''
    formatted_name = str(raw_name).zfill(10)
    return 'MGYF' + formatted_name
