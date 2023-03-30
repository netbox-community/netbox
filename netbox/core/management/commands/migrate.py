# noinspection PyUnresolvedReferences
from django.core.management.commands.migrate import Command
from django.db import models

from utilities.migration import custom_deconstruct

models.Field.deconstruct = custom_deconstruct
