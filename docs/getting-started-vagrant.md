<h1>Getting Started with Vagrant using Virtualbox</h1>

This guide assumes that the latest versions of [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtualbox](https://www.virtualbox.org/wiki/Downloads) are already installed in your host.

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
