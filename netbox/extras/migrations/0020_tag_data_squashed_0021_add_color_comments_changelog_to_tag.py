from django.db import migrations, models

import utilities.fields


def copy_tags(apps, schema_editor):
    """
    Copy data from taggit_tag to extras_tag
    """
    TaggitTag = apps.get_model('taggit', 'Tag')
    ExtrasTag = apps.get_model('extras', 'Tag')

    tags_values = TaggitTag.objects.all().values('id', 'name', 'slug')
    tags = [ExtrasTag(**tag) for tag in tags_values]
    ExtrasTag.objects.bulk_create(tags)


def copy_taggeditems(apps, schema_editor):
    """
    Copy data from taggit_taggeditem to extras_taggeditem
    """
    TaggitTaggedItem = apps.get_model('taggit', 'TaggedItem')
    ExtrasTaggedItem = apps.get_model('extras', 'TaggedItem')

    tagged_items_values = TaggitTaggedItem.objects.all().values('id', 'object_id', 'content_type_id', 'tag_id')
    tagged_items = [ExtrasTaggedItem(**tagged_item) for tagged_item in tagged_items_values]
    ExtrasTaggedItem.objects.bulk_create(tagged_items)


def delete_taggit_taggeditems(apps, schema_editor):
    """
    Delete all TaggedItem instances from taggit_taggeditem
    """
    TaggitTaggedItem = apps.get_model('taggit', 'TaggedItem')
    TaggitTaggedItem.objects.all().delete()


def delete_taggit_tags(apps, schema_editor):
    """
    Delete all Tag instances from taggit_tag
    """
    TaggitTag = apps.get_model('taggit', 'Tag')
    TaggitTag.objects.all().delete()


class Migration(migrations.Migration):

    replaces = [('extras', '0020_tag_data'), ('extras', '0021_add_color_comments_changelog_to_tag')]

    dependencies = [
        ('extras', '0019_tag_taggeditem'),
        ('virtualization', '0009_custom_tag_models'),
        ('tenancy', '0006_custom_tag_models'),
        ('secrets', '0006_custom_tag_models'),
        ('dcim', '0070_custom_tag_models'),
        ('ipam', '0025_custom_tag_models'),
        ('circuits', '0015_custom_tag_models'),
    ]

    operations = [
        migrations.RunPython(
            code=copy_tags,
        ),
        migrations.RunPython(
            code=copy_taggeditems,
        ),
        migrations.RunPython(
            code=delete_taggit_taggeditems,
        ),
        migrations.RunPython(
            code=delete_taggit_tags,
        ),
        migrations.AddField(
            model_name='tag',
            name='color',
            field=utilities.fields.ColorField(default='9e9e9e', max_length=6),
        ),
        migrations.AddField(
            model_name='tag',
            name='comments',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='tag',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
