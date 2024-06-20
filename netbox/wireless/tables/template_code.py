WIRELESS_LINK_DISTANCE = """
{% load helpers %}
{% if record.distance %}{{ record.distance|floatformat:"-2" }} {{ record.distance_unit }}{% endif %}
"""
