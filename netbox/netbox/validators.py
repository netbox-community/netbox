"""
Composable model validator framework for NetBox.

Replaces monolithic clean() overrides with standalone, categorized validator
functions that can be:

1. Inspected by external tools (what constraints does Device have?)
2. Run selectively (skip cross-model checks during merge replay)
3. Composed (apply only validators relevant to changed fields)
4. Tested independently (each validator is a standalone function)

clean() methods delegate to these validators, so behavior is preserved
while gaining composability and introspection.
"""
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from django.core.exceptions import ValidationError

logger = logging.getLogger('netbox.validators')


class ValidatorCategory(str, Enum):
    FIELD = 'field'
    CROSS_FIELD = 'cross_field'
    CROSS_MODEL = 'cross_model'
    UNIQUENESS = 'uniqueness'
    NORMALIZATION = 'normalization'


@dataclass(frozen=True)
class ModelValidator:
    """
    A single named validation rule for a model.

    The validate callable receives an instance and should raise
    django.core.exceptions.ValidationError if the instance is invalid.
    """
    name: str
    model_label: str
    fields: frozenset = field(default_factory=frozenset)
    category: ValidatorCategory = ValidatorCategory.FIELD
    validate: Optional[Callable] = None
    queries_db: bool = False
    description: str = ''


class ValidatorRegistry:
    """
    Central registry of all model validation rules.

    Validators are grouped by model label and can be filtered by category,
    fields, and whether they query the database.

    Supports mixin sentinels: pseudo-labels like ``__mixin:CustomFieldsMixin__``
    that match any model whose MRO includes the registered mixin class. This
    lets a single registration cover every concrete model inheriting that mixin,
    without per-model wiring.
    """

    def __init__(self):
        self._validators: dict[str, list[ModelValidator]] = defaultdict(list)
        self._mixin_sentinels: dict[str, type] = {}

    def register(self, model_label: str, *validators: ModelValidator):
        for v in validators:
            self._validators[model_label].append(v)

    def register_mixin_sentinel(self, sentinel_label: str, mixin_class: type):
        """
        Associate a sentinel pseudo-label with an abstract mixin class.

        Any future call to ``get_validators(instance=...)`` will also return
        validators registered under this sentinel if the instance inherits
        from *mixin_class*.
        """
        self._mixin_sentinels[sentinel_label] = mixin_class

    def _sentinel_labels_for(self, instance) -> list[str]:
        """Return sentinel labels whose mixin class appears in instance's MRO."""
        mro = type(instance).__mro__
        return [label for label, cls in self._mixin_sentinels.items() if cls in mro]

    def get_validators(
        self,
        model_label: str,
        categories: Optional[set[ValidatorCategory]] = None,
        exclude_categories: Optional[set[ValidatorCategory]] = None,
        fields: Optional[set[str]] = None,
        instance=None,
    ) -> list[ModelValidator]:
        """Get validators for a model, optionally filtered.

        If *instance* is provided, also includes validators registered under
        any matching mixin sentinel labels.
        """
        result = list(self._validators.get(model_label, []))
        if instance is not None:
            for sentinel_label in self._sentinel_labels_for(instance):
                result.extend(self._validators.get(sentinel_label, []))
        if categories:
            result = [v for v in result if v.category in categories]
        if exclude_categories:
            result = [v for v in result if v.category not in exclude_categories]
        if fields:
            result = [v for v in result
                      if not v.fields or v.fields & fields]
        return result

    def validate(
        self,
        instance,
        categories: Optional[set[ValidatorCategory]] = None,
        exclude_categories: Optional[set[ValidatorCategory]] = None,
        fields: Optional[set[str]] = None,
    ):
        """
        Run validators for an instance, optionally filtering.
        Collects all errors and raises a single ValidationError.
        """
        label = f'{instance._meta.app_label}.{instance._meta.model_name}'
        validators = self.get_validators(
            label,
            categories=categories,
            exclude_categories=exclude_categories,
            fields=fields,
            instance=instance,
        )
        errors = {}
        for v in validators:
            try:
                if v.validate:
                    v.validate(instance)
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field_name, msgs in e.message_dict.items():
                        errors.setdefault(field_name, []).extend(
                            msgs if isinstance(msgs, list) else [msgs]
                        )
                elif hasattr(e, 'error_dict'):
                    for field_name, error_list in e.error_dict.items():
                        errors.setdefault(field_name, []).extend(error_list)
                else:
                    errors.setdefault('__all__', []).append(e.message)
        if errors:
            raise ValidationError(errors)

    def validate_for_merge(self, instance, changed_fields: set[str]):
        """
        Run only field-level and cross-field validators relevant to
        changed_fields. Skips cross-model and uniqueness checks that
        may fail on partial branch state.
        """
        return self.validate(
            instance,
            exclude_categories={
                ValidatorCategory.CROSS_MODEL,
                ValidatorCategory.UNIQUENESS,
            },
            fields=changed_fields,
        )

    def has_validators(self, model_label: str, instance=None) -> bool:
        if model_label in self._validators:
            return True
        if instance is not None:
            return any(
                sentinel in self._validators
                for sentinel in self._sentinel_labels_for(instance)
            )
        return False

    def registered_models(self) -> set[str]:
        return set(self._validators.keys())

    def registered_sentinels(self) -> dict[str, str]:
        """Return sentinel labels and their mixin class names."""
        return {label: cls.__name__ for label, cls in self._mixin_sentinels.items()}

    def cross_model_validators(self, model_label: str) -> list[ModelValidator]:
        """Get only the validators that query the database."""
        return [v for v in self._validators.get(model_label, [])
                if v.category in (ValidatorCategory.CROSS_MODEL,
                                  ValidatorCategory.UNIQUENESS)]

    def summary(self) -> dict:
        by_category = defaultdict(int)
        for validators in self._validators.values():
            for v in validators:
                by_category[v.category.value] += 1
        return {
            'models': len(self._validators),
            'total_validators': sum(len(v) for v in self._validators.values()),
            'by_category': dict(by_category),
            'by_model': {k: len(v) for k, v in sorted(self._validators.items())},
            'db_querying': sum(
                1 for vs in self._validators.values()
                for v in vs if v.queries_db
            ),
        }


# Global singleton
validator_registry = ValidatorRegistry()
