SEARCH_RESULT_ATTRS = """
{% for name, value in record.display_attrs.items %}
  <span class="badge bg-secondary"
      {% if value|length > 40 %} data-bs-toggle="tooltip" data-bs-placement="bottom" title="{{ value }}"{% endif %}
    >
    {{ name|bettertitle }}:
    {% with url=value.get_absolute_url %}
      {% if url %}<a href="{{ url }}">{% endif %}
      {% if value|length > 40 %}
        {{ value|truncatechars:"40" }}
      {% else %}
        {{ value }}
      {% endif %}
      {% if url %}</a>{% endif %}
    {% endwith %}
  </span>
{% endfor %}
"""
