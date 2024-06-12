WIRELESS_LINK_LENGTH = """
{% load helpers %}
{% if record.length %}{{ record.length|floatformat:"-2" }} {{ record.length_unit }}{% endif %}
"""
