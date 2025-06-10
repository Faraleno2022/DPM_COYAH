from django import template

register = template.Library()

@register.filter(name='sub')
def sub(value, arg):
    """Soustraction entre deux valeurs dans les templates."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
