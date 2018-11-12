# Extending Models

Below is a list of items to consider when adding a new field to a model:

### 1. Generate and run database migration

Django migrations are used to express changes to the database schema. In most cases, Django can generate these automatically, however very complex changes may require manual intervention. Always remember to specify a short but descriptive name when generating a new migration.

```
./manage.py makemigrations <app> -n <name>
./manage.py migrate
```

Where possible, try to merge related changes into a single migration. For example, if three new fields are being added to different models within an app, these can be expressed in the same migration. You can merge a new migration with an existing one by combining their `operations` lists.

!!! note
    Migrations can only be merged within a release. Once a new release has been published, its migrations cannot be altered.

### 2. Add validation logic to `clean()`

If the new field introduces additional validation requirements (beyond what's included with the field itself), implement them in the model's `clean()` method. Remember to call the model's original method using `super()` before or agter your custom validation as appropriate:

```
class Foo(models.Model):

    def clean(self):

        super(DeviceCSVForm, self).clean()

        # Custom validation goes here
        if self.bar is None:
            raise ValidationError()
```

### 3. Add CSV helpers

Add the name of the new field to `csv_headers` and included a CSV-friendly representation of its data in the model's `to_csv()` method. These will be used when exporting objects in CSV format.

### 4. Update relevant querysets

If you're adding a relational field (e.g. `ForeignKey`) and intend to include the data when retreiving a list of objects, be sure to include the field using `select_related()` or `prefetch_related()` as appropriate. This will optimize the view and avoid excessive database lookups.

### 5. Update API serializer

Extend the model's API serializer in `<app>.api.serializers` to include the new field. In most cases, it will not be necessary to also extend the nested serializer, which produces a minimal represenation of the model.

### 6. Add field to forms

Extend any forms to include the new field as appropriate. Common forms include:

* **Credit/edit** - Manipulating a single object
* **Bulk edit** - Performing a change on mnay objects at once
* **CSV import** - The form used when bulk importing objects in CSV format
* **Filter** - Displays the options available for filtering a list of objects (both UI and API)

### 7. Extend object filter set

If the new field should be filterable, add it to the `FilterSet` for the model. If the field should be searchable, remember to reference it in the FilterSet's `search()` method.

### 8. Add column to object table

If the new field will be included in the object list view, add a column to the model's table. For simple fields, adding the field name to `Meta.fields` will be sufficient. More complex fields may require explicitly declaring a new column.

### 9. Update the UI templates

Edit the object's view template to display the new field. There may also be a custom add/edit form template that needs to be updated.

### 10. Adjust API and model tests

Extend the model and/or API tests to verify that the new field and any accompanying validation logic perform as expected. This is especially important for relational fields.
