## Getting Help

If you encounter any issues installing or using NetBox, try one of the following resources to get assistance. Please
**do not** open an issue on GitHub except to report bugs or request features.

### Freenode IRC

Join the #netbox channel on [Freenode IRC](https://freenode.net/). You can connect to Freenode at irc.freenode.net using
an IRC client, or you can use their [webchat client](https://webchat.freenode.net/).

### Reddit

We have established [/r/netbox](https://www.reddit.com/r/netbox) on Reddit for NetBox issues and general discussion.
Reddit registration is free and does not require providing an email address (although it is encouraged).

## Reporting Bugs

* First, ensure that you've installed the [latest stable version](https://github.com/digitalocean/netbox/releases) of
NetBox. If you're running an older version, it's possible that the bug has already been fixed.

* Next, check the GitHub [issues list](https://github.com/digitalocean/netbox/issues) to see if the bug you've found has
already been reported. If you think you may be experiencing a reported issue that hasn't already been resolved, please
click "add a reaction" in the top right corner of the issue and add a thumbs up (+1). You might also want to add a
comment describing how it's affecting your installation. This will allow us to prioritize bugs based on how many users
are affected.

* If you haven't found an existing issue that describes your suspected bug, please inquire about it on IRC or Reddit.
**Do not** file an issue until you have received confirmation that it is in fact a bug. Invalid issues are very
distracting and slow the pace at which NetBox is developed.

* When submitting an issue, please be as descriptive as possible. Be sure to include:

    * The environment in which NetBox is running
    * The exact steps that can be taken to reproduce the issue (if applicable)
    * Any error messages returned
    * Screenshots (if applicable)

* Keep in mind that we prioritize bugs based on their severity and how much work is required to resolve them. It may
take some time for someone to address your issue.

## Feature Requests

* First, check the GitHub [issues list](https://github.com/digitalocean/netbox/issues) to see if the feature you're
requesting is already listed. (Be sure to search closed issues as well, since some feature requests are rejected.) If
the feature you'd like to see has already been requested, click "add a reaction" in the top right corner of the issue
and add a thumbs up (+1). This ensures that the issue has a better chance of making it onto the roadmap. Also feel free
to add a comment with any additional justification for the feature.

* While suggestions for new features are welcome, it's important to limit the scope of NetBox's feature set to avoid
feature creep. For example, the following features would be firmly out of scope for NetBox:

    * Ticket management
    * Network state monitoring
    * Acting as a DNS server
    * Acting as an authentication server

* Before filing a new feature request, propose it on IRC or Reddit first. Feedback you receive there will help validate
and shape the proposed feature before filing a formal issue.

* Good feature requests are very narrowly defined. Be sure to enumerate specific functionality and data schema. The more
effort you put into writing a feature request, the better its chances are of being implemented. Overly broad feature
requests will be closed.

* When submitting a feature request on GitHub, be sure to include the following:

    * A detailed description of the proposed functionality
    * A use case for the feature; who would use it and what value it would add to NetBox
    * A rough description of any changes necessary to the database schema
    * Any third-party libraries or other resources which would be involved

## Submitting Pull Requests

* Be sure to open an issue before starting work on a pull request, and discuss your idea with the NetBox maintainers
before beginning work​. This will help prevent wasting time on something that might we might not be able to implement.
When suggesting a new feature, also make sure it won't conflict with any work that's already in progress.

* When submitting a pull request, please be sure to work off of the `develop` branch, rather than `master`. In NetBox,
the `develop` branch is used for ongoing development, while `master` is used for tagging new stable releases.

* All code submissions should meet the following criteria (CI will enforce these checks):

    * Python syntax is valid
    * All tests pass when run with `./manage.py test netbox/`
    * PEP 8 compliance is enforced, with the exception that lines may be greater than 80 characters in length
