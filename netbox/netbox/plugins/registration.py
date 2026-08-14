import inspect
import logging

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from netbox.graphql.utils import get_model_label
from netbox.registry import registry

from .navigation import PluginMenu, PluginMenuButton, PluginMenuItem
from .templates import PluginTemplateExtension

logger = logging.getLogger(__name__)

__all__ = (
    'register_graphql_filter_extensions',
    'register_graphql_schema',
    'register_graphql_type_extensions',
    'register_jinja_filters',
    'register_menu',
    'register_menu_items',
    'register_serializer_resolver',
    'register_template_extensions',
    'register_user_preferences',
)


def register_jinja_filters(filters):
    """
    Register a dict of Jinja filter functions provided by a plugin. Each key is the
    filter name as it will appear in templates; the value is the callable implementing it.
    Plugin-registered filters have lower precedence than instance-level JINJA_FILTERS
    so that site admins can always override them in configuration.py.
    """
    if not isinstance(filters, dict):
        raise TypeError(_("jinja_filters must be a dict mapping filter names to callables"))
    for name, fn in filters.items():
        if not callable(fn):
            raise TypeError(_("Jinja filter '{name}' must be callable").format(name=name))
        if name in registry['plugins']['jinja_filters']:
            logger.warning(
                "Jinja filter '%s' registered by a plugin is being overridden by a later-loaded plugin",
                name,
            )
    registry['plugins']['jinja_filters'].update(filters)


def register_template_extensions(class_list):
    """
    Register a list of PluginTemplateExtension classes
    """
    for template_extension in class_list:
        # Validation
        if not inspect.isclass(template_extension):
            raise TypeError(
                _("PluginTemplateExtension class {template_extension} was passed as an instance!").format(
                    template_extension=template_extension
                )
            )
        if not issubclass(template_extension, PluginTemplateExtension):
            raise TypeError(
                _("{template_extension} is not a subclass of netbox.plugins.PluginTemplateExtension!").format(
                    template_extension=template_extension
                )
            )

        if template_extension.models:
            # Registration for specific models
            models = template_extension.models
        else:
            # Global registration (no specific models)
            models = [None]
        for model in models:
            registry['plugins']['template_extensions'][model].append(template_extension)


def register_menu(menu):
    if not isinstance(menu, PluginMenu):
        raise TypeError(_("{item} must be an instance of netbox.plugins.PluginMenuItem").format(item=menu))
    registry['plugins']['menus'].append(menu)


def register_menu_items(section_name, class_list):
    """
    Register a list of PluginMenuItem instances for a given menu section (e.g. plugin name)
    """
    # Validation
    for menu_link in class_list:
        if not isinstance(menu_link, PluginMenuItem):
            raise TypeError(_("{menu_link} must be an instance of netbox.plugins.PluginMenuItem").format(
                menu_link=menu_link
            ))
        for button in menu_link.buttons:
            if not isinstance(button, PluginMenuButton):
                raise TypeError(_("{button} must be an instance of netbox.plugins.PluginMenuButton").format(
                    button=button
                ))

    registry['plugins']['menu_items'][section_name] = class_list


def register_graphql_schema(graphql_schema):
    """
    Register a GraphQL schema class for inclusion in NetBox's GraphQL API.
    """
    registry['plugins']['graphql_schemas'].extend(graphql_schema)


def _register_graphql_extensions(class_list, store):
    """
    Validate GraphQL extension classes and record them in the registry, bucketed by the canonical labels declared
    in each class's `models` attribute. The whole list is validated before anything is recorded.
    """
    staged = []
    staged_pairs = set()
    for extension in class_list:
        if not inspect.isclass(extension):
            raise TypeError(
                _("GraphQL extension {extension} was passed as an instance!").format(extension=extension)
            )
        models = getattr(extension, 'models', None)
        if isinstance(models, str):
            raise TypeError(
                _("GraphQL extension {extension} must declare 'models' as a list of labels, not a string.").format(
                    extension=extension
                )
            )
        try:
            models = tuple(models or ())
        except TypeError:
            raise TypeError(
                _("GraphQL extension {extension} must declare 'models' as an iterable of model labels.").format(
                    extension=extension
                )
            ) from None
        if not models:
            raise TypeError(
                _("GraphQL extension {extension} must declare a non-empty 'models' attribute.").format(
                    extension=extension
                )
            )
        # Own __dict__ check so undecorated subclasses are rejected (Strawberry internal, pinned 0.323.2).
        definition = vars(extension).get('__strawberry_definition__')
        if definition is None:
            raise TypeError(
                _("GraphQL extension {extension} must be decorated with @strawberry.type.").format(
                    extension=extension
                )
            )
        if definition.is_input or definition.is_interface or hasattr(extension, '__strawberry_django_definition__'):
            raise TypeError(
                _("GraphQL extension {extension} must be a plain @strawberry.type, not an input, an interface, "
                  "or a strawberry_django type.").format(extension=extension)
            )
        if definition.interfaces:
            raise TypeError(
                _("GraphQL extension {extension} must not implement GraphQL interfaces.").format(
                    extension=extension
                )
            )
        if any(field.python_name == 'models' for field in definition.fields):
            raise TypeError(
                _("GraphQL extension {extension} must declare 'models' as an unannotated class attribute or "
                  "ClassVar, not as a GraphQL field.").format(extension=extension)
            )
        seen = set()
        canonical_labels = []
        for label in models:
            if not isinstance(label, str):
                raise TypeError(
                    _("GraphQL extension {extension} declares an invalid model label: {label!r}.").format(
                        extension=extension, label=label
                    )
                )
            try:
                model = apps.get_model(label)
            except (LookupError, ValueError):
                raise TypeError(
                    _("GraphQL extension {extension} targets unknown model '{label}'.").format(
                        extension=extension, label=label
                    )
                )
            canonical_label = get_model_label(model)
            if canonical_label in seen:
                raise TypeError(
                    _("GraphQL extension {extension} declares duplicate label '{label}'.").format(
                        extension=extension, label=canonical_label
                    )
                )
            seen.add(canonical_label)
            canonical_labels.append(canonical_label)
        if any(
            extension in registry['plugins'][store].get(label, ()) or (label, extension) in staged_pairs
            for label in canonical_labels
        ):
            raise TypeError(
                _("GraphQL extension {extension} is already registered.").format(extension=extension)
            )
        if assembled := [
            label for label in canonical_labels
            if (store, label) in registry['plugins']['graphql_extensions_assembled']
        ]:
            raise ImproperlyConfigured(
                f"GraphQL extension {extension} for '{', '.join(assembled)}' was registered after the "
                f"target GraphQL type was assembled. This usually means this or another plugin imported a core "
                f"GraphQL module during plugin initialization. Reference core GraphQL types through "
                f"strawberry.lazy() string annotations instead of importing them at module level."
            )
        staged.append((extension, canonical_labels))
        staged_pairs.update((label, extension) for label in canonical_labels)
    for extension, canonical_labels in staged:
        for canonical_label in canonical_labels:
            registry['plugins'][store][canonical_label].append(extension)


def register_graphql_type_extensions(class_list):
    """
    Register a list of GraphQL output-type mixin classes. Each class must be decorated with @strawberry.type and
    declare a `models` attribute listing the `app_label.model` labels of the core types it extends.
    """
    _register_graphql_extensions(class_list, 'graphql_type_extensions')


def register_graphql_filter_extensions(class_list):
    """
    Register a list of GraphQL filter mixin classes. Each class must be decorated with @strawberry.type and declare
    a `models` attribute listing the `app_label.model` labels of the core filters it extends.
    """
    _register_graphql_extensions(class_list, 'graphql_filter_extensions')


def register_user_preferences(plugin_name, preferences):
    """
    Register a list of user preferences defined by a plugin.
    """
    registry['plugins']['preferences'][plugin_name] = preferences


def register_serializer_resolver(app_label, resolver):
    """
    Register a callable that returns a DRF serializer class for a model in
    the given app, or None if the resolver does not handle the model. The
    resolver is consulted by utilities.api.get_serializer_for_model() before
    the default import-path lookup, but only for models belonging to
    `app_label`. Plugins (and internal apps) should only register resolvers
    for their own models.

    This is the supported extension point for plugins whose models are
    generated dynamically (and therefore have no importable serializer at
    the {app_label}.api.serializers.{Model}Serializer path) or that need
    to override serializer resolution for specific models.

    Resolver signature: resolver(model, prefix='') -> serializer class or None
    """
    if not callable(resolver):
        raise TypeError(_("Serializer resolver must be callable"))
    if app_label in registry['serializer_resolvers']:
        raise ValueError(
            _("A serializer resolver is already registered for app '{app_label}'").format(app_label=app_label)
        )
    registry['serializer_resolvers'][app_label] = resolver
