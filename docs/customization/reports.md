# NetBox Reports

A NetBox report is a mechanism for validating the integrity of data within NetBox. Running a report allows the user to verify that the objects defined within NetBox meet certain arbitrary conditions. For example, you can write reports to check that:

* All top-of-rack switches have a console connection
* Every router has a loopback interface with an IP address assigned
* Each interface description conforms to a standard format
* Every site has a minimum set of VLANs defined
* All IP addresses have a parent prefix

...and so on. Reports are completely customizable, so there's practically no limit to what you can test for.

## Writing Reports

Reports must be saved as files in the [`REPORTS_ROOT`](../configuration/optional-settings.md#reports_root) path (which defaults to `netbox/reports/`). Each file created within this path is considered a separate module. Each module holds one or more reports (Python classes), each of which performs a certain function. The logic of each report is broken into discrete test methods, each of which applies a small portion of the logic comprising the overall test.

!!! warning
    The reports path includes a file named `__init__.py`, which registers the path as a Python module. Do not delete this file.

For example, we can create a module named `devices.py` to hold all of our reports which pertain to devices in NetBox. Within that module, we might define several reports. Each report is defined as a Python class inheriting from `extras.reports.Report`.

```
from extras.reports import Report

class DeviceConnectionsReport(Report):
    description = "Validate the minimum physical connections for each device"

class DeviceIPsReport(Report):
    description = "Check that every device has a primary IP address assigned"
```

Within each report class, we'll create a number of test methods to execute our report's logic. In DeviceConnectionsReport, for instance, we want to ensure that every live device has a console connection, an out-of-band management connection, and two power connections.

```
from dcim.choices import DeviceStatusChoices
from dcim.models import ConsolePort, Device, PowerPort
from extras.reports import Report


class DeviceConnectionsReport(Report):
    description = "Validate the minimum physical connections for each device"

    def test_console_connection(self):

        # Check that every console port for every active device has a connection defined.
        active = DeviceStatusChoices.STATUS_ACTIVE
        for console_port in ConsolePort.objects.prefetch_related('device').filter(device__status=active):
            if console_port.connected_endpoint is None:
                self.log_failure(
                    console_port.device,
                    "No console connection defined for {}".format(console_port.name)
                )
            elif not console_port.connection_status:
                self.log_warning(
                    console_port.device,
                    "Console connection for {} marked as planned".format(console_port.name)
                )
            else:
                self.log_success(console_port.device)

    def test_power_connections(self):

        # Check that every active device has at least two connected power supplies.
        for device in Device.objects.filter(status=DeviceStatusChoices.STATUS_ACTIVE):
            connected_ports = 0
            for power_port in PowerPort.objects.filter(device=device):
                if power_port.connected_endpoint is not None:
                    connected_ports += 1
                    if not power_port.path.is_active:
                        self.log_warning(
                            device,
                            "Power connection for {} marked as planned".format(power_port.name)
                        )
            if connected_ports < 2:
                self.log_failure(
                    device,
                    "{} connected power supplies found (2 needed)".format(connected_ports)
                )
            else:
                self.log_success(device)
```

As you can see, reports are completely customizable. Validation logic can be as simple or as complex as needed. Also note that the `description` attribute support markdown syntax. It will be rendered in the report list page.

!!! warning
    Reports should never alter data: If you find yourself using the `create()`, `save()`, `update()`, or `delete()` methods on objects within reports, stop and re-evaluate what you're trying to accomplish. Note that there are no safeguards against the accidental alteration or destruction of data.

The following methods are available to log results within a report:

* log(message)
* log_success(object, message=None)
* log_info(object, message)
* log_warning(object, message)
* log_failure(object, message)

The recording of one or more failure messages will automatically flag a report as failed. It is advised to log a success for each object that is evaluated so that the results will reflect how many objects are being reported on. (The inclusion of a log message is optional for successes.) Messages recorded with `log()` will appear in a report's results but are not associated with a particular object or status. Log messages also support using markdown syntax and will be rendered on the report result page.

To perform additional tasks, such as sending an email or calling a webhook, after a report has been run, extend the `post_run()` method. The status of the report is available as `self.failed` and the results object is `self.result`.

By default, reports within a module are unordered and 'randomly' displayed in the reports list page. If you want to order reports, you can defined the `report_order` variable at the end
of your module. The `report_order` variable is a tuple which contains each Report class in a specific order.

```
from extras.reports import Report

class DeviceConnectionsReport(Report)
    pass

class DeviceIPsReport(Report)
    pass

report_order = (DeviceIPsReport, DeviceConnectionsReport)
```

Once you have created a report, it will appear in the reports list. Initially, reports will have no results associated with them. To generate results, run the report.

## Running Reports

!!! note
    To run a report, a user must be assigned the `extras.run_report` permission. This is achieved by assigning the user (or group) a permission on the Report object and specifying the `run` action in the admin UI as shown below.

    ![Adding the run action to a permission](/media/admin_ui_run_permission.png)

### Via the Web UI

Reports can be run via the web UI by navigating to the report and clicking the "run report" button at top right. Once a report has been run, its associated results will be included in the report view.

### Via the API

To run a report via the API, simply issue a POST request to its `run` endpoint. Reports are identified by their module and class name.

```
    POST /api/extras/reports/<module>.<name>/run/
```

Our example report above would be called as:

```
    POST /api/extras/reports/devices.DeviceConnectionsReport/run/
```

### Via the CLI

Reports can be run on the CLI by invoking the management command:

```
python3 manage.py runreport <module>
```

where ``<module>`` is the name of the python file in the ``reports`` directory without the ``.py`` extension.  One or more report modules may be specified.
