# NetBox Reports

!!! warning
    Reports are deprecated beginning with NetBox v4.0, and their functionality has been merged with [custom scripts](./custom-scripts.md). While backward compatibility has been maintained, users are advised to convert legacy reports into custom scripts soon, as support for legacy reports will be removed in a future release.

## Converting Reports to Scripts

### Step 1: Update Class Definition

Change the parent class from `Report` to `Script`:

```python title="Old code"
from extras.reports import Report

class MyReport(Report):
```

```python title="New code"
from extras.scripts import Script

class MyReport(Script):
```

### Step 2: Update Logging Calls

Reports and scripts both provide logging methods, however their signatures differ. All script logging methods accept a message as the first parameter, and accept an object as an optional second parameter.

Additionally, the Report class' generic `log()` method is **not** available on Script. Users are advised to replace calls of this method with `log_info()`.

Use the table below as a reference when updating these methods.

| Report (old)                  | Script (New)                |
|-------------------------------|-----------------------------|
| `log(message)`                | `log_info(message)`         |
| `log_debug(obj, message)`[^1] | `log_debug(message, obj)`   |
| `log_info(obj, message)`      | `log_info(message, obj)`    |
| `log_success(obj, message)`   | `log_success(message, obj)` |
| `log_warning(obj, message)`   | `log_warning(message, obj)` |
| `log_failure(obj, message)`   | `log_failure(message, obj)` |

[^1]: `log_debug()` was added to the Report class in v4.0 to avoid confusion with the same method on Script

```python title="Old code"
self.log_failure(
    console_port.device,
    f"No console connection defined for {console_port.name}"
)
```

```python title="New code"
self.log_failure(
    f"No console connection defined for {console_port.name}",
    obj=console_port.device,
)
```

### Other Notes

Existing reports will be converted to scripts automatically upon upgrading to NetBox v4.0, and previous job history will be retained. However, users are advised to convert legacy reports into custom scripts at the earliest opportunity, as support for legacy reports will be removed in a future release.

The `pre_run()` and `post_run()` Report methods have been carried over to Script. These are called automatically by Script's `run()` method. (Note that if you opt to override this method, you are responsible for calling `pre_run()` and `post_run()` where applicable.)

The `is_valid()` method on Report is no longer needed and has been removed.
