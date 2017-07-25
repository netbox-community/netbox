# Migration

Remove Python 2 packages

```no-highlight
# apt-get remove --purge -y python-dev python-pip
```

Install Python 3 packages

```no-highlight
# apt-get install -y python3 python3-dev python3-pip
```

Install Python Packages

```no-highlight
# cd /opt/netbox
# pip3 install -r requirements.txt
```

Gunicorn Update

```no-highlight
# pip uninstall gunicorn
# pip3 install gunicorn
```

Re-install LDAP Module (optional if using LDAP for auth)

```no-highlight
sudo pip3 install django-auth-ldap
```
