# Extending Models

Below is a list of tasks to consider when adding a new field to a core model.

## 1. Generate and run database migrations

Django migrations are used to express changes to the database schema. In most cases, Django can generate these automatically, however very complex changes may require manual intervention. Always remember to specify a short but descriptive name when generating a new migration.

```
./manage.py makemigrations <app> -n <name>
./manage.py migrate
```

Where possible, try to merge related changes into a single migration. For example, if three new fields are being added to different models within an app, these can be expressed in the same migration. You can merge a new migration with an existing one by combining their `operations` lists.

!!! note
    Migrations can only be merged within a release. Once a new release has been published, its migrations cannot be altered (other than for the purpose of correcting a bug).

## 2. Add validation logic to `clean()`

If the new field introduces additional validation requirements (beyond what's included with the field itself), implement them in the model's `clean()` method. Remember to call the model's original method using `super()` before or after your custom validation as appropriate:

```
class Foo(models.Model):

    def clean(self):

        super().clean()

        # Custom validation goes here
        if self.bar is None:
            raise ValidationError()
```

## 3. Update relevant querysets

If you're adding a relational field (e.g. `ForeignKey`) and intend to include the data when retrieving a list of objects, be sure to include the field using `prefetch_related()` as appropriate. This will optimize the view and avoid extraneous database queries.

## 4. Update API serializer

Extend the model's API serializer in `<app>.api.serializers` to include the new field. In most cases, it will not be necessary to also extend the nested serializer, which produces a minimal representation of the model.

## 5. Add field to forms

Extend any forms to include the new field as appropriate. Common forms include:

* **Credit/edit** - Manipulating a single object
* **Bulk edit** - Performing a change on many objects at once
* **CSV import** - The form used when bulk importing objects in CSV format
* **Filter** - Displays the options available for filtering a list of objects (both UI and API)

## 6. Extend object filter set

If the new field should be filterable, add it to the `FilterSet` for the model. If the field should be searchable, remember to reference it in the FilterSet's `search()` method.

## 7. Add column to object table

If the new field will be included in the object list view, add a column to the model's table. For simple fields, adding the field name to `Meta.fields` will be sufficient. More complex fields may require declaring a custom column.

## 8. Update the UI templates

Edit the object's view template to display the new field. There may also be a custom add/edit form template that needs to be updated.

## 9. Create/extend test cases

Create or extend the relevant test cases to verify that the new field and any accompanying validation logic perform as expected. This is especially important for relational fields. NetBox incorporates various test suites, including:

* API serializer/view tests
* Filter tests
* Form tests
* Model tests
* View tests

Be diligent to ensure all of the relevant test suites are adapted or extended as necessary to test any new functionality.

## 10. Update the model's documentation

Each model has a dedicated page in the documentation, at `models/<app>/<model>.md`. Update this file to include any relevant information about the new field.
