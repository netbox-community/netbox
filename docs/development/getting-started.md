# Getting Started

## Setting up a Development Environment

Getting started with NetBox development is pretty straightforward, and should feel very familiar to anyone with Django development experience. There are a few things you'll need:

* A Linux system or environment
* A PostgreSQL server, which can be installed locally [per the documentation](../installation/1-postgresql.md)
* A Redis server, which can also be [installed locally](../installation/2-redis.md)
* A supported version of Python

### Fork the Repo

Assuming you'll be working on your own fork, your first step will be to fork the [official git repository](https://github.com/netbox-community/netbox). (If you're a maintainer who's going to be working directly with the official repo, skip this step.) You can then clone your GitHub fork locally for development:

```no-highlight
$ git clone https://github.com/youruseraccount/netbox.git
Cloning into 'netbox'...
remote: Enumerating objects: 231, done.
remote: Counting objects: 100% (231/231), done.
remote: Compressing objects: 100% (147/147), done.
remote: Total 56705 (delta 134), reused 145 (delta 84), pack-reused 56474
Receiving objects: 100% (56705/56705), 27.96 MiB | 34.92 MiB/s, done.
Resolving deltas: 100% (44177/44177), done.
$ ls netbox/
base_requirements.txt  contrib          docs         mkdocs.yml  NOTICE     requirements.txt  upgrade.sh
CHANGELOG.md           CONTRIBUTING.md  LICENSE.txt  netbox      README.md  scripts
```

The NetBox project utilizes three persistent git branches to track work:

* `master` - Serves as a snapshot of the current stable release
* `develop` - All development on the upcoming stable release occurs here
* `feature` - Tracks work on an upcoming major release

Typically, you'll base pull requests off of the `develop` branch, or off of `feature` if you're working on a new major release. **Never** merge pull requests into the `master` branch, which receives merged only from the `develop` branch.

For example, assume that the current NetBox release is v3.1.1. Work applied to the `develop` branch will appear in v3.1.2, and work done under the `feature` branch will be included in the next minor release (v3.2.0).

### Enable Pre-Commit Hooks

NetBox ships with a [git pre-commit hook](https://githooks.com/) script that automatically checks for style compliance and missing database migrations prior to committing changes. This helps avoid erroneous commits that result in CI test failures. You are encouraged to enable it by creating a link to `scripts/git-hooks/pre-commit`:

```no-highlight
$ cd .git/hooks/
$ ln -s ../../scripts/git-hooks/pre-commit
```

### Create a Python Virtual Environment

A [virtual environment](https://docs.python.org/3/tutorial/venv.html) (or "venv" for short) is like a container for a set of Python packages. These allow you to build environments suited to specific projects without interfering with system packages or other projects. When installed per the documentation, NetBox uses a virtual environment in production.

Create a virtual environment using the `venv` Python module:

```no-highlight
$ mkdir ~/.venv
$ python3 -m venv ~/.venv/netbox
```

This will create a directory named `.venv/netbox/` in your home directory, which houses a virtual copy of the Python executable and its related libraries and tooling. When running NetBox for development, it will be run using the Python binary at `~/.venv/netbox/bin/python`.

!!! info "Where to Create Your Virtual Environments"
    Keeping virtual environments in `~/.venv/` is a common convention but entirely optional: Virtual environments can be created almost wherever you please.

Once created, activate the virtual environment:

```no-highlight
$ source ~/.venv/netbox/bin/activate
(netbox) $ 
```

Notice that the console prompt changes to indicate the active environment. This updates the necessary system environment variables to ensure that any Python scripts are run within the virtual environment.

### Install Dependencies

With the virtual environment activated, install the project's required Python packages using the `pip` module:

```no-highlight
(netbox) $ python -m pip install -r requirements.txt
Collecting Django==3.1 (from -r requirements.txt (line 1))
  Cache entry deserialization failed, entry ignored
  Using cached https://files.pythonhosted.org/packages/2b/5a/4bd5624546912082a1bd2709d0edc0685f5c7827a278d806a20cf6adea28/Django-3.1-py3-none-any.whl
...
```

### Configure NetBox

Within the `netbox/netbox/` directory, copy `configuration.example.py` to `configuration.py` and update the following parameters:

* `ALLOWED_HOSTS`: This can be set to `['*']` for development purposes
* `DATABASE`: PostgreSQL database connection parameters
* `REDIS`: Redis configuration, if different from the defaults
* `SECRET_KEY`: Set to a random string (use `generate_secret_key.py` in the parent directory to generate a suitable key)
* `DEBUG`: Set to `True`
* `DEVELOPER`: Set to `True` (this enables the creation of new database migrations)

### Start the Development Server

Django provides a lightweight, auto-updating HTTP/WSGI server for development use. It is started with the `runserver` management command:

```no-highlight
$ python netbox/manage.py runserver
Performing system checks...

System check identified no issues (0 silenced).
November 18, 2020 - 15:52:31
Django version 3.1, using settings 'netbox.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

This ensures that your development environment is now complete and operational. Any changes you make to the code base will be automatically adapted by the development server.

!!! info "IDE Integration"
    Some IDEs, such as PyCharm, will integrate with Django's development server and allow you to run it directly within the IDE. This is strongly encouraged as it makes for a much more convenient development environment.

## Populating Demo Data

Once you have your development environment up and running, it might be helpful to populate some "dummy" data to make interacting with the UI and APIs more convenient. Check out the [netbox-demo-data](https://github.com/netbox-community/netbox-demo-data) repo on GitHub, which houses a collection of sample data that can be easily imported to any new NetBox deployment. (This sample data is used to populate the public demo instance at <https://demo.netbox.dev>.)

The demo data is provided in JSON format and loaded into an empty database using Django's `loaddata` management command. Consult the demo data repo's `README` file for complete instructions on populating the data.

## Running Tests

Prior to committing any substantial changes to the code base, be sure to run NetBox's test suite to catch any potential errors. Tests are run using the `test` management command. Remember to ensure the Python virtual environment is active before running this command.

```no-highlight
$ python netbox/manage.py test
```

In cases where you haven't made any changes to the database (which is most of the time), you can append the `--keepdb` argument to this command to reuse the test database between runs. This cuts down on the time it takes to run the test suite since the database doesn't have to be rebuilt each time. (Note that this argument will cause errors if you've modified any model fields since the previous test run.)

```no-highlight
$ python netbox/manage.py test --keepdb
```

You can also limit the command to running only a specific subset of tests. For example, to run only IPAM and DCIM view tests:

```no-highlight
$ python netbox/manage.py test dcim.tests.test_views ipam.tests.test_views
```

## Submitting Pull Requests

Once you're happy with your work and have verified that all tests pass, commit your changes and push it upstream to your fork. Always provide descriptive (but not excessively verbose) commit messages. When working on a specific issue, be sure to prefix your commit message with the word "Fixes" or "Closes" and the issue number (with a hash mark). This tells GitHub to automatically close the referenced issue once the commit has been merged.

```no-highlight
$ git commit -m "Closes #1234: Add IPv5 support"
$ git push origin
```

Once your fork has the new commit, submit a [pull request](https://github.com/netbox-community/netbox/compare) to the NetBox repo to propose the changes. Be sure to provide a detailed accounting of the changes being made and the reasons for doing so.

Once submitted, a maintainer will review your pull request and either merge it or request changes. If changes are needed, you can make them via new commits to your fork: The pull request will update automatically.

!!! note "Remember to Open an Issue First"
    Remember, pull requests are permitted only for **accepted** issues. If an issue you want to work on hasn't been approved by a maintainer yet, it's best to avoid risking your time and effort on a change that might not be accepted. (The one exception to this is trivial changes to the documentation or other non-critical resources.)
