from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
# used to display labels for radio button with images
def getValue(value):
    # removing  /

    value = value.split("/")[-1]

    # removing .
    value = value.split(".")[0]

    return value.capitalize()

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)