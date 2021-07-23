# Adding Models

## 1. Define the model class

Models within each app are stored in either `models.py` or within a submodule under the `models/` directory. When creating a model, be sure to subclass the [appropriate base model](models.md) from `netbox.models`. This will typically be PrimaryModel or OrganizationalModel. Remember to add the model class to the `__all__` listing for the module.

Each model should define, at a minimum:

* A `__str__()` method returning a user-friendly string representation of the instance
* A `get_absolute_url()` method returning an instance's direct URL (using `reverse()`)
* A `Meta` class specifying a deterministic ordering (if ordered by fields other than the primary ID)

## 2. Define field choices

If the model has one or more fields with static choices, define those choices in `choices.py` by subclassing `utilities.choices.ChoiceSet`.

## 3. Generate database migrations

Once your model definition is complete, generate database migrations by running `manage.py -n $NAME --no-header`. Always specify a short unique name when generating migrations.

!!! info
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

## 6. Create the FilterSet

Each model should have a corresponding FilterSet class defined. This is used to filter UI and API queries. Subclass the appropriate class from `netbox.filtersets` that matches the model's parent class.

Every model FilterSet should define a `q` filter to support general search queries.

## 7. Create the table

Create a table class for the model in `tables.py` by subclassing `utilities.tables.BaseTable`. Under the table's `Meta` class, be sure to list both the fields and default columns.

## 8. Create the object template

Create the HTML template for the object view. (The other views each typically employ a generic template.) This template should extend `generic/object.html`.

## 9. Add the model to the navigation menu

For NetBox releases prior to v3.0, add the relevant link(s) to the navigation menu template. For later releases, add the relevant items in `netbox/netbox/navigation_menu.py`.

## 10. REST API components

Create the following for each model:

* Detailed (full) model serializer in `api/serializers.py`
* Nested serializer in `api/nested_serializers.py`
* API view in `api/views.py`
* Endpoint route in `api/urls.py`

## 11. GraphQL API components (v3.0+)

Create a Graphene object type for the model in `graphql/types.py` by subclassing the appropriate class from `netbox.graphql.types`.

Also extend the schema class defined in `graphql/schema.py` with the individual object and object list fields per the established convention.

## 12. Add tests

Add tests for the following:

* UI views
* API views
* Filter sets

## 13. Documentation

Create a new documentation page for the model in `docs/models/<app_label>/<model_name>.md`. Include this file under the "features" documentation where appropriate.

Also add your model to the index in `docs/development/models.md`.
