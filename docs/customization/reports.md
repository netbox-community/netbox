# NetBox Reports

!!! warning
    Reports are deprecated and merged with [custom scripts](./custom-scripts.md) as of NetBox 4.0.  You should convert any legacy reports to use Script as described below

## Converting Reports to Scripts

### Step 1: Change Class Definition

First change the import and class definition to use Script.  For example:

```
from extras.reports import Report

class DeviceConnectionsReport(Report):
```
change to:

```
from extras.scripts import Script

class DeviceConnectionsReport(Script):
```

### Step 2: Change Logging Calls

The logging methods require the object and message in the logging call to be swapped.  For example:


```
    self.log_failure(
        console_port.device,
        "No console connection defined for {}".format(console_port.name)
    )
```

should be changed to:

```
    self.log_failure(
        "No console connection defined for {}".format(console_port.name),
        console_port.device,
    )
```

This applies to all log_ functions:

* log_success(object, message) -> log_success(message, object)
* log_info(object, message) -> log_info(message, object)
* log_warning(object, message) -> log_warning(message, object)
* log_failure(object, message) -> log_failure(message, object)

### Optional Run Method

Scripts have a default run method that will automatically run all the `test_` methods as well as the pre_run and post_run functions.  You can also define a run method and call `run_tests()` to call all the `test_` functions:

```
    def run(self, data, commit):
        self.run_tests()

```
Any functionality needed for pre or post run can just be put into the the run method before or after the call to run_tests.
