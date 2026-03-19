from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    """Ayirish: {{ value|subtract:arg }}"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def goal_diff(row, _=None):
    """Goal difference hisoblash."""
    try:
        return row['goals_for'] - row['goals_against']
    except (KeyError, TypeError):
        return 0
