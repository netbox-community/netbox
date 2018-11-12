# Migration

!!! warning
    Beginning with v2.5, NetBox will no longer support Python 2. It is strongly recommended that you upgrade to Python 3 as soon as possible.

## Ubuntu

Remove the Python2 version of gunicorn:

```no-highlight
# pip uninstall -y gunicorn
```

Install Python3 and pip3, Python's package management tool:

```no-highlight
# apt-get update
# apt-get install -y python3 python3-dev python3-setuptools
# easy_install3 pip
```

Install the Python3 packages required by NetBox:

```no-highlight
# pip3 install -r requirements.txt
```

Replace gunicorn with the Python3 version:

```no-highlight
# pip3 install gunicorn
```

If using LDAP authentication, install the `django-auth-ldap` package:

```no-highlight
# pip3 install django-auth-ldap
```

## CentOS/RHEL

Remove the Python2 version of gunicorn:

```no-highlight
# pip uninstall -y gunicorn
```

Ensure EPEL is installed:

```no-highlight
# yum install -y epel-release
```

Install Python3 and pip3, Python's package management tool:

```no-highlight
# yum install -y python36 python36-devel python36-setuptools
# python3.6 -m ensurepip --default-pip
```

Install the Python3 packages required by NetBox:

```no-highlight
# pip3 install -r requirements.txt
```

Replace gunicorn with the Python3 version:

```no-highlight
# pip3 install gunicorn
```

If using LDAP authentication, install the `django-auth-ldap` package:

```no-highlight
# pip3 install django-auth-ldap
```
