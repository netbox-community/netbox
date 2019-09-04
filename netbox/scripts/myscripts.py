from dcim.models import Site
from extras.scripts import Script, BooleanVar, IntegerVar, ObjectVar, StringVar


class NoInputScript(Script):
    description = "This script does not require any input"

    def run(self, data):

        self.log_debug("This a debug message.")
        self.log_info("This an info message.")
        self.log_success("This a success message.")
        self.log_warning("This a warning message.")
        self.log_failure("This a failure message.")


class DemoScript(Script):
    name = "Script Demo"
    description = "A quick demonstration of the available field types"

    my_string1 = StringVar(
        description="Input a string between 3 and 10 characters",
        min_length=3,
        max_length=10
    )
    my_string2 = StringVar(
        description="This field enforces a regex: three letters followed by three numbers",
        regex=r'[a-z]{3}\d{3}'
    )
    my_number = IntegerVar(
        description="Pick a number between 1 and 255 (inclusive)",
        min_value=1,
        max_value=255
    )
    my_boolean = BooleanVar(
        description="Use the checkbox to toggle true/false"
    )
    my_object = ObjectVar(
        description="Select a NetBox site",
        queryset=Site.objects.all()
    )

    def run(self, data):

        self.log_info("Your string was {}".format(data['my_string1']))
        self.log_info("Your second string was {}".format(data['my_string2']))
        self.log_info("Your number was {}".format(data['my_number']))
        if data['my_boolean']:
            self.log_info("You ticked the checkbox")
        else:
            self.log_info("You did not tick the checkbox")
        self.log_info("You chose the sites {}".format(data['my_object']))

        return "Here's some output"
