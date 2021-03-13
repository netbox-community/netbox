from django import template

register = template.Library()

TERMS_DANGER = ("delete", "deleted", "remove", "removed")
TERMS_WARNING = ("changed", "updated", "change", "update")
TERMS_SUCCESS = ("created", "added", "create", "add")


@register.simple_tag
def get_status(text: str) -> str:
    lower = text.lower()

    if lower in TERMS_DANGER:
        return "danger"
    elif lower in TERMS_WARNING:
        return "warning"
    elif lower in TERMS_SUCCESS:
        return "success"
    else:
        return "info"
