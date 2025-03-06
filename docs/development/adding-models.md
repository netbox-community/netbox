# Adding Models

## 1. Define the model class

Models within each app are stored in either `models.py` or within a submodule under the `models/` directory. When creating a model, be sure to subclass the [appropriate base model](models.md) from `netbox.models`. This will typically be NetBoxModel or OrganizationalModel. Remember to add the model class to the `__all__` listing for the module.

Each model should define, at a minimum:

* A `Meta` class specifying a deterministic ordering (if ordered by fields other than the primary ID)
* A `__str__()` method returning a user-friendly string representation of the instance
* A `get_absolute_url()` method if necessary; a standard version of the method is defined in the `NetBoxFeatureSet` base class, but you will need to provide your own (returning an instance's direct URL using `reverse()`) if not subclassing that base class

## 2. Define field choices

If the model has one or more fields with static choices, define those choices in `choices.py` by subclassing `utilities.choices.ChoiceSet`.

## 3. Generate database migrations

Once your model definition is complete, generate database migrations by running `manage.py makemigrations -n $NAME --no-header`. Always specify a short unique name when generating migrations.

!!! info "Configuration Required"
    Set `DEVELOPER = True` in your NetBox configuration to enable the creation of new migrations.

## 4. Add all standard views

Most models will need view classes created in `views.py` to serve the following operations:

* List view
* Detail view
* Edit view
* Delete view
* Bulk import
* Bulk edit
* Bulk delete

## 5. Add URL paths

Add the relevant URL path for each view created in the previous step to `urls.py`.

## 6. Add relevant forms

Depending on the type of model being added, you may need to define several types of form classes. These include:

* A base model form (for creating/editing individual objects)
* A bulk edit form
* A bulk import form (for CSV-based import)
* A filterset form (for filtering the object list view)

## 7. Create the FilterSet

Each model should have a corresponding FilterSet class defined. This is used to filter UI and API queries. Subclass the appropriate class from `netbox.filtersets` that matches the model's parent class.

## 8. Create the table class

Create a table class for the model in `tables.py` by subclassing `utilities.tables.BaseTable`. Under the table's `Meta` class, be sure to list both the fields and default columns.

## 9. Create a SearchIndex subclass

If this model will be included in global search results, create a subclass of `netbox.search.SearchIndex` for it and specify the fields to be indexed.

## 10. Create the object template

Create the HTML template for the object view. (The other views each typically employ a generic template.) This template should extend `generic/object.html`.

## 11. Add the model to the navigation menu

Add the relevant navigation menu items in `netbox/netbox/navigation/menu.py`.

## 12. REST API components

Create the following for each model:

* Detailed (full) model serializer in `api/serializers.py`
* API view in `api/views.py`
* Endpoint route in `api/urls.py`

## 13. GraphQL API components

Create a GraphQL object type for the model in `graphql/types.py` by subclassing the appropriate class from `netbox.graphql.types`.

**Note:** GraphQL unit tests may fail citing null values on a non-nullable field if related objects are prefetched. You may need to fix this by setting the type annotation to be `= strawberry_django.field(select_related=["policy"])` or similar.

Also extend the schema class defined in `graphql/schema.py` with the individual object and object list fields per the established convention.

## 14. Add tests

Add tests for the following:

* UI views
* API views
* Filter sets

## 15. Documentation

Create a new documentation page for the model in `docs/models/<app_label>/<model_name>.md`. Include this file under the "features" documentation where appropriate.

Also add your model to the index in `docs/development/models.md`.
