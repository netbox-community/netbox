## Getting Help

If you encounter any issues installing or using NetBox, try one of the
following resources to get assistance. Please **do not** open a GitHub issue
except to report bugs or request features.

### Mailing List

We have established a Google Groups Mailing List for issues and general
discussion. This is the best forum for obtaining assistance with NetBox
installation. You can find us [here](https://groups.google.com/forum/#!forum/netbox-discuss).

### Slack

For real-time discussion, you can join the #netbox Slack channel on [NetworkToCode](https://slack.networktocode.com/).

## Reporting Bugs

* First, ensure that you're running the [latest stable version](https://github.com/netbox-community/netbox/releases)
of NetBox. If you're running an older version, it's possible that the bug has
already been fixed.

* Next, check the GitHub [issues list](https://github.com/netbox-community/netbox/issues)
to see if the bug you've found has already been reported. If you think you may
be experiencing a reported issue that hasn't already been resolved, please
click "add a reaction" in the top right corner of the issue and add a thumbs
up (+1). You might also want to add a comment describing how it's affecting your
installation. This will allow us to prioritize bugs based on how many users are
affected.

* When submitting an issue, please be as descriptive as possible. Be sure to
provide all information request in the issue template, including:

    * The environment in which NetBox is running
    * The exact steps that can be taken to reproduce the issue
    * Expected and observed behavior
    * Any error messages generated
    * Screenshots (if applicable)

* Please avoid prepending any sort of tag (e.g. "[Bug]") to the issue title.
The issue will be reviewed by a maintainer after submission and the appropriate
labels will be applied for categorization.

* Keep in mind that we prioritize bugs based on their severity and how much
work is required to resolve them. It may take some time for someone to address
your issue.

* For more information on how bug reports are handled, please see our [issue
intake policy](https://github.com/netbox-community/netbox/wiki/Issue-Intake-Policy).

## Feature Requests

* First, check the GitHub [issues list](https://github.com/netbox-community/netbox/issues)
to see if the feature you're requesting is already listed. (Be sure to search
closed issues as well, since some feature requests have been rejected.) If the
feature you'd like to see has already been requested and is open, click "add a
reaction" in the top right corner of the issue and add a thumbs up (+1). This
ensures that the issue has a better chance of receiving attention. Also feel
free to add a comment with any additional justification for the feature.
(However, note that comments with no substance other than a "+1" will be
deleted. Please use GitHub's reactions feature to indicate your support.)

* Due to a large backlog of feature requests, we are not currently accepting
any proposals which substantially extend NetBox's functionality beyond its
current feature set. This includes the introduction of any new views or models
which have not already been proposed in an existing feature request.

* Before filing a new feature request, consider raising your idea on the
mailing list first. Feedback you receive there will help validate and shape the
proposed feature before filing a formal issue.

* Good feature requests are very narrowly defined. Be sure to thoroughly
describe the functionality and data model(s) being proposed. The more effort
you put into writing a feature request, the better its chance is of being
implemented. Overly broad feature requests will be closed.

* When submitting a feature request on GitHub, be sure to include all
information requested by the issue template, including:

    * A detailed description of the proposed functionality
    * A use case for the feature; who would use it and what value it would add
      to NetBox
    * A rough description of changes necessary to the database schema (if
      applicable)
    * Any third-party libraries or other resources which would be involved

* Please avoid prepending any sort of tag (e.g. "[Feature]") to the issue
title. The issue will be reviewed by a moderator after submission and the
appropriate labels will be applied for categorization.

* For more information on how feature requests are handled, please see our
[issue intake policy](https://github.com/netbox-community/netbox/wiki/Issue-Intake-Policy).

## Submitting Pull Requests

* Be sure to open an issue **before** starting work on a pull request, and
discuss your idea with the NetBox maintainers before beginning work. This will
help prevent wasting time on something that might we might not be able to
implement. When suggesting a new feature, also make sure it won't conflict with
any work that's already in progress.

* Any pull request which does _not_ relate to an accepted issue will be closed.

* All major new functionality must include relevant tests where applicable.

* When submitting a pull request, please be sure to work off of the `develop`
branch, rather than `master`. The `develop` branch is used for ongoing
development, while `master` is used for tagging stable releases.

* All code submissions should meet the following criteria (CI will enforce
these checks):

    * Python syntax is valid
    * All tests pass when run with `./manage.py test`
    * PEP 8 compliance is enforced, with the exception that lines may be
      greater than 80 characters in length

## Commenting

Only comment on an issue if you are sharing a relevant idea or constructive
feedback. **Do not** comment on an issue just to show your support (give the
top post a :+1: instead) or ask for an ETA. These comments will be deleted to
reduce noise in the discussion.

## Issue Lifecycle

New issues are handled according to our [issue intake policy](https://github.com/netbox-community/netbox/wiki/Issue-Intake-Policy).
Maintainers will assign label(s) and/or close new issues as the policy
dictates. This helps ensure a productive development environment and avoid
accumulating a large backlog of work.

The core maintainers group has chosen to make use of GitHub's [Stale bot](https://github.com/apps/stale)
to aid in issue management.

* Issues will be marked as stale after 14 days of no activity.
* Then after 7 more days of inactivity, the issue will be closed.
* Any issue bearing one of the following labels will be exempt from all Stale
  bot actions:
  * `status: accepted`
  * `status: gathering feedback`
  * `status: blocked`

It is natural that some new issues get more attention than others. Often this
is a metric of an issues's overall value to the project. In other cases in
which issues merely get lost in the shuffle, notifications from Stale bot can
bring renewed attention to potentially meaningful issues.

## Maintainer Guidance

* Maintainers are expected to contribute at least four hours per week to the
  project on average. This can be employer-sponsored or individual time, with
  the understanding that all contributions are submitted under the Apache 2.0
  license and that your employer may not make claim to any contributions.
  Contributions include code work, issue management, and community support. All
  development must be in accordance with our [development guidance](https://netbox.readthedocs.io/en/stable/development/).

* Maintainers are expected to attend (where feasible) our biweekly ~30-minute
  sync to review agenda items. This meeting provides opportunity to present and
  discuss pressing topics. Meetings are held as virtual audio/video conferences.

* Official channels for communication include:

    * GitHub issues/pull requests
    * The [netbox-discuss](https://groups.google.com/forum/#!forum/netbox-discuss) mailing list
    * The **#netbox** channel on [NetworkToCode Slack](https://networktocode.slack.com/)

* Maintainers with no substantial recorded activity in a 60-day period will be
  removed from the project.
