<h1>Getting started on RHEL/Centos OS</h1>

This guide documents the process of installing NetBox on RHEL/Centos 7 with [nginx](https://www.nginx.com/) and [gunicorn](http://gunicorn.org/).

 sudo yum install postgresql-server python-psycopg2 postgresql-devel

  sudo postgresql-setup initdb
  sudo systemctl start postgresql

sudo systemctl enable postgresql

sudo yum install epel-release


yum install python python-devel python-pip git libxml2-devel libxslt-devel libffi-devel graphviz gcc openssl-devel

This will install all the missing packages for a successful pip install
yum groupinstall 'Development Tools'
pip install gunicorn


sudo su -
su - postgres
cd data/
vim  pg_hba.conf

change the indent on the localhost connections to password and save
exit postgres user
service postgresql reload

test connections


# Quickstart

Create a vagrant directory:

```
mkdir -p ~/vagrant
cd ~/vagrant

```
The vagrant is hosted on dropbox since vagrant charges for hosting the files.

Download from  and put into your ~/vagrant:
https://www.dropbox.com/s/frlh9ul4n0wna46/package.box?dl=0   


This install uses this default user and passwd for all the services:
* user: vagrant
* password: vagrant

When I say all the services this includes the ssh log-in, postgresql and the netbox
Gui log-in.

Do the following inside ~/vagrant:
vagrant box add netbox ~/vagrant/package.box
vagrant init netbox
vagrant up
vagrant ssh

 open up a browser and put 127.0.0.1:2223 and log-in!

# if you cannot ssh or bring up the GUI check the virtualbox settings:
* In the Virtualbox GUI click on your VM then settings.
* Go to the networking and click on "port forwarding".
* Make sure that ssh and nginx port are there. If not add them
* rule: [Name: SSH, Protocol: TCP, Host IP: blank, Host Port: 2222, Guest IP: blank, Guest Port: 22]
* rule: [Name: nginx, Protocol: TCP, Host IP: blank, Host Port: 2223, Guest IP: blank, Guest Port: 80]

You can change the Host port since that is the port your host is going to use but, keep the Guest port the same as above since those are the default.
