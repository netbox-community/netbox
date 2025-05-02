# Translations

NetBox coordinates all translation work using the [Transifex](https://explore.transifex.com/netbox-community/netbox/) platform. Signing up for a Transifex account is free.

All language translations in NetBox are generated from the source file found at `netbox/translations/en/LC_MESSAGES/django.po`. This file contains the original English strings with empty mappings, and is generated as part of NetBox's release process. Transifex updates source strings from this file on a recurring basis, so new translation strings will appear in the platform automatically as it is updated in the code base.

Reviewers log into Transifex and navigate to their designated language(s) to translate strings. The initial translation for most strings will be machine-generated via the AWS Translate service. Human reviewers are responsible for reviewing these translations and making corrections where necessary.

## Updating Translation Sources

To update the English `.po` file from which all translations are derived, use the `makemessages` management command (ignoring the `project-static/` directory):

```nohighlight
./manage.py makemessages -l en -i "project-static/*"
```

Then, commit the change and push to the `main` branch on GitHub. Any new strings will appear for translation on Transifex automatically.

!!! note
    It is typically not necessary to update source strings manually, as this is done nightly by a [GitHub action](https://github.com/netbox-community/netbox/blob/main/.github/workflows/update-translation-strings.yml).

## Updating Translated Strings

Typically, translated strings need to be updated only as part of the NetBox [release process](./release-checklist.md).

Check the Transifex dashboard for languages that are not marked _ready for use_, being sure to click _Show all languages_ if it appears at the bottom of the list. Use machine translation to round out any not-ready languages. It's not necessary to review the machine translation immediately as the translation teams will handle that aspect; the goal at this stage is to get translations included in the Transifex pull request.

To download translated strings automatically, you'll need to:

1. Install the [Transifex CLI client](https://github.com/transifex/cli)
2. Generate a [Transifex API token](https://app.transifex.com/user/settings/api/)

Once you have the client set up, run the following command from the project root (e.g. `/opt/netbox/`):

```no-highlight
TX_TOKEN=$TOKEN tx pull --force
```

This will download all portable (`.po`) translation files from Transifex, updating them locally as needed. (The `--force` argument instructs the client to disregard the timestamps of local translation files.)

Once retrieved, the updated strings need to be compiled into new `.mo` files so they can be used by the application. Run Django's [`compilemessages`](https://docs.djangoproject.com/en/stable/ref/django-admin/#django-admin-compilemessages) management command to compile them:

```no-highlight
./manage.py compilemessages
```

Once any new `.mo` files have been generated, they need to be committed and pushed back up to GitHub. (Again, this is typically done as part of publishing a new NetBox release.)

!!! tip
    Run `git status` to check that both `*.mo` & `*.po` files have been updated as expected.

## Proposing New Languages

If you'd like to add support for a new language to NetBox, the first step is to [submit a GitHub issue](https://github.com/netbox-community/netbox/issues/new?assignees=&labels=type%3A+translation&projects=&template=translation.yaml) to capture the proposal. While we'd like to add as many languages as possible, we do need to limit the rate at which new languages are added. New languages will be selected according to community interest and the number of volunteers who sign up as translators.

Once a proposed language has been approved, a NetBox maintainer will:

* Add it to the Transifex platform
* Designate one or more reviewers
* Create the initial machine-generated translations for review
* Add it to the list of supported languages
