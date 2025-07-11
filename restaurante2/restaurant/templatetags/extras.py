from django import template

register = template.Library()

@register.filter
def floatdiv(value, arg):
    try:
        return int(round(float(value) / float(arg)))
    except:
        return 0
