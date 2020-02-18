from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from utilities.fields import NaturalOrderingField


class Command(BaseCommand):
    help = "Recalculate natural ordering values for the specified models"

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label.ModelName', nargs='*',
            help='One or more specific models (each prefixed with its app_label) to renaturalize',
        )

    def _get_models(self, names):
        """
        Compile a list of models to be renaturalized. If no names are specified, all models which have one or more
        NaturalOrderingFields will be included.
        """
        models = []

        if names:
            # Collect all NaturalOrderingFields present on the specified models
            for name in names:
                try:
                    app_label, model_name = name.split('.')
                except ValueError:
                    raise CommandError(
                        "Invalid format: {}. Models must be specified in the form app_label.ModelName.".format(name)
                    )
                try:
                    app_config = apps.get_app_config(app_label)
                except LookupError as e:
                    raise CommandError(str(e))
                try:
                    model = app_config.get_model(model_name)
                except LookupError:
                    raise CommandError("Unknown model: {}.{}".format(app_label, model_name))
                fields = [
                    field for field in model._meta.concrete_fields if type(field) is NaturalOrderingField
                ]
                if not fields:
                    raise CommandError(
                        "Invalid model: {}.{} does not employ natural ordering".format(app_label, model_name)
                    )
                models.append(
                    (model, fields)
                )

        else:
            # Find *all* models with NaturalOrderingFields
            for app_config in apps.get_app_configs():
                for model in app_config.models.values():
                    fields = [
                        field for field in model._meta.concrete_fields if type(field) is NaturalOrderingField
                    ]
                    if fields:
                        models.append(
                            (model, fields)
                        )

        return models

    def handle(self, *args, **options):

        models = self._get_models(args)

        if options['verbosity']:
            self.stdout.write("Renaturalizing {} models.".format(len(models)))

        for model, fields in models:
            for field in fields:
                target_field = field.target_field
                naturalize = field.naturalize_function
                count = 0

                # Print the model and field name
                if options['verbosity']:
                    self.stdout.write(
                        "{}.{} ({})... ".format(model._meta.label, field.target_field, field.name),
                        ending='\n' if options['verbosity'] >= 2 else ''
                    )
                    self.stdout.flush()

                # Find all unique values for the field
                queryset = model.objects.values_list(target_field, flat=True).order_by(target_field).distinct()
                for value in queryset:
                    naturalized_value = naturalize(value, max_length=field.max_length)

                    if options['verbosity'] >= 2:
                        self.stdout.write("  {} -> {}".format(value, naturalized_value), ending='')
                        self.stdout.flush()

                    # Update each unique field value in bulk
                    changed = model.objects.filter(name=value).update(**{field.name: naturalized_value})

                    if options['verbosity'] >= 2:
                        self.stdout.write(" ({})".format(changed))
                    count += changed

                # Print the total count of alterations for the field
                if options['verbosity'] >= 2:
                    self.stdout.write(self.style.SUCCESS("{} {} updated ({} unique values)".format(
                        count, model._meta.verbose_name_plural, queryset.count()
                    )))
                elif options['verbosity']:
                    self.stdout.write(self.style.SUCCESS(str(count)))

        if options['verbosity']:
            self.stdout.write(self.style.SUCCESS("Done."))
