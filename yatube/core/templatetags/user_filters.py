from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Add class attribute to html tag."""
    return field.as_widget(attrs={'class': css})
