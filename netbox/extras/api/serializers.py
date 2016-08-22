from rest_framework import serializers

from extras.models import CF_TYPE_SELECT, CustomFieldChoice, Graph


class CustomFieldsSerializer(serializers.Serializer):
    """
    Extends a ModelSerializer to render any CustomFields and their values associated with an object.
    """
    custom_fields = serializers.SerializerMethodField()

    def get_custom_fields(self, obj):
        fields = {cf.name: None for cf in self.context['view'].custom_fields}
        for cfv in obj.custom_field_values.all():
            if cfv.field.type == CF_TYPE_SELECT:
                fields[cfv.field.name] = CustomFieldChoiceSerializer(instance=cfv.value).data
            else:
                fields[cfv.field.name] = cfv.value
        return fields


class CustomFieldChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomFieldChoice
        fields = ['id', 'value']


class GraphSerializer(serializers.ModelSerializer):
    embed_url = serializers.SerializerMethodField()
    embed_link = serializers.SerializerMethodField()

    class Meta:
        model = Graph
        fields = ['name', 'embed_url', 'embed_link']

    def get_embed_url(self, obj):
        return obj.embed_url(self.context['graphed_object'])

    def get_embed_link(self, obj):
        return obj.embed_link(self.context['graphed_object'])
