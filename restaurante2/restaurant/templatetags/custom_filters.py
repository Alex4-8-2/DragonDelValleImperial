from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})