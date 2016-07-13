# Contributing to NetBox

Thank you for your interest in contributing to NetBox! This document contains some quick pointers on reporting bugs and
requesting new features.

## Reporting Issues

* First, ensure that you've installed the latest stable version of NetBox. If you're running an older version, it's
possible that the bug has already been fixed.

* Check the [issues list](https://github.com/digitalocean/netbox/issues) to see if the bug you've found has already been
reported. If you think you may be experiencing a reported issue, please add a quick comment to it with a "+1" and a
quick description of how it's affecting your installation.

* If you're unsure whether the behavior you're seeing is expected, you can join #netbox on irc.freenode.net and ask
before going through the trouble of submitting an issue report.

* When submitting an issue, please be as descriptive as possible. Be sure to describe:

    * The environment in which NetBox is running
    * The exact steps that can be taken to reproduce the issue (if applicable)
    * Any error messages returned

* Keep in mind that we prioritize bugs based on their severity and how much work is required to resolve them. It may
take some time for someone to address your issue. If it's been longer than a week with no updates, please ping us on
IRC.

## Feature Requests

* First, check the [issues list](https://github.com/digitalocean/netbox/issues) to see if the feature you're requesting
has already been requested (and possibly rejected). If it has, click "add a reaction" in the top right corner of the
issue and add a thumbs up (+1). This ensures that the issue has a better chance of making it onto the roadmap. Also feel
free to add a comment with any additional justification for the feature.

* While discussion of new features is welcome, it's important to limit the scope of NetBox's feature set to avoid
feature creep. For example, the following features would be firmly out of scope for NetBox:

    * Ticket management
    * Network state monitoring
    * Acting as a DNS server
    * Acting as an authentication server

* If you're not sure whether the feature you want is a good fit for NetBox, please ask in #netbox on irc.freenode.net.
Even if it's not quite right for NetBox, we may be able to point you to a tool better suited for the job.

* When submitting a feature request, be sure to include the following:

    * A brief description of the functionality
    * A use case for the feature; who would use it and what value it would add to NetBox
    * A rough description of any changes necessary to the database schema (if applicable)
    * Any third-party libraries or other resources which would be involved

## Submitting Pull Requests

* Be sure to open an issue before starting work on a pull request, and discuss your idea with the NetBox maintainers
before beginning work​. This will help prevent wasting time on something that might we might not be able to implement.
When suggesting a new feature, also make sure it won't conflict with any work that's already in progress.

* When submitting a pull request, please be sure to work off of branch `develop`, rather than branch `master`.
In NetBox, the `develop` branch is used for ongoing development, while `master` is used for tagging new
stable releases.

* All code submissions should meet the following criteria (CI will enforce these checks):

    * Python syntax is valid
    * All tests pass when run with `./manage.py test netbox/`
    * PEP 8 compliance is enforced, with the exception that lines may be greater than 80 characters in length
