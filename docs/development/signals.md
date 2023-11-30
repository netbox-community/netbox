# Signals

In addition to [Django's built-in signals](https://docs.djangoproject.com/en/stable/topics/signals/), NetBox defines some of its own, listed below.

## post_clean

This signal is sent by models which inherit from `CustomValidationMixin` at the end of their `clean()` method.

### Receivers

* `extras.signals.run_custom_validators()`

## core.job_start

* `extras..signals.process_job_start_event_rules()`

## core.job_end

* `extras..signals.process_job_end_event_rules()`

## core.pre_sync

## core.post_sync
