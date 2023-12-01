# Signals

In addition to [Django's built-in signals](https://docs.djangoproject.com/en/stable/topics/signals/), NetBox defines some of its own, listed below.

## post_clean

This signal is sent by models which inherit from `CustomValidationMixin` at the end of their `clean()` method.

### Receivers

* `extras.signals.run_custom_validators()`

## core.job_start

This signal is sent whenever a [background job](../features/background-jobs.md) is started.

### Receivers

* `extras.signals.process_job_start_event_rules()`

## core.job_end

This signal is sent whenever a [background job](../features/background-jobs.md) is terminated.

### Receivers

* `extras.signals.process_job_end_event_rules()`

## core.pre_sync

This signal is sent when the [DataSource](../models/core/datasource.md) model's `sync()` method is called.

## core.post_sync

This signal is sent when a [DataSource](../models/core/datasource.md) finishes synchronizing.
