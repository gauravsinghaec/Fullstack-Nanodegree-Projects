# Linux Server Configiration Project

This project teaches you to secure and set up a Linux server. By the end of this project, you will have one of your web applications running live on a secure web server.
* Public IP: 13.126.222.78
* Port 2200
* URL to access project : http://13.126.222.78 OR http://13.126.222.78/catalog

## Getting Started
To complete this project, you'll need a Linux server instance. I have used Amazon Lightsail for this. 
Once you've done that, here are the steps to complete this project.

## Get your server.
* Start a new Ubuntu Linux server instance on Amazon Lightsail[check below link]. There are full details on setting up your Lightsail instance on the next page.
```
https://lightsail.aws.amazon.com/
```
* Follow the instructions provided to SSH into your server.

## Secure your server.
### Updating the server
```
sudo apt-get update 
sudo apt-get upgrade
```

### Create new user 'grader' and give 'grader' permissions
* Create a new user called grader
```
sudo adduser grader
```
![adduser](https://user-images.githubusercontent.com/15084301/34913937-f9f6bb60-f92e-11e7-84fa-3b42d8575c94.png)

* Give sudo access to grader
```
sudo nano /etc/sudoers.d/grader
```
![sudoerfile](https://user-images.githubusercontent.com/15084301/34913943-fb5f634e-f92e-11e7-9c9a-a2ff001586bc.png)

* Login as grader
```
sudo login grader
```
![sudoaccess](https://user-images.githubusercontent.com/15084301/34913942-fb269a32-f92e-11e7-8002-b870e3c6d501.png)


### Configuring SSH to a non-default port
```
SSH default port is 22. We want to configure it to non default port. 
Since we are using LightSail, we need to open the non default port through the web interface. 
If you don't do this step, you'll be locked out of the instance. 
Go to the networking tab on the management console. Then, the firewall option
```

![awssshport](https://user-images.githubusercontent.com/15084301/34914131-72fb6bd4-f932-11e7-8c74-3ec10babe22d.png)

* Go into your sshd config file and Change the following options. 

```
sudo nano /etc/ssh/sshd_config 

# What ports, IPs and protocols we listen for
# Port 22
Port 2200

# Authentication:
LoginGraceTime 120
#PermitRootLogin prohibit-password
PermitRootLogin no
StrictModes yes

# Change to no to disable tunnelled clear text passwords
PasswordAuthentication No
.
.
.
```

### Creating RSA key for key based authentication
* Swich back to local machine and create public private key pair locally for key based authentication.
```
LOCAL MACHINE:~$ ssh-keygen
```
![ssskeygen](https://user-images.githubusercontent.com/15084301/34914397-3f2c7cfc-f938-11e7-933d-638b3ef87970.png)

![authorisedkeyslocal](https://user-images.githubusercontent.com/15084301/34914396-3edb7b22-f938-11e7-9f9c-18bc4cd87c2f.png)

* Switch back to the Linux Machine where you were logged in as grader and create an authorized_keys file. This where you paste the public key that you generated on your local machine like below.
```

ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDN******************** 
************************************************************
************************************** Gaurav@Gaurav-Dell-PC

grader@publicIP:

mkdir .ssh
cd .ssh
sudo nano authorized_keys
```

![authorised_pubkey](https://user-images.githubusercontent.com/15084301/34913939-fa772aac-f92e-11e7-8925-0d1b4dcf9966.png)

* Login as grader using public key
```
ssh grader@13.126.222.78 -p 2200 -i ~/.ssh/AWSConfigPubPrivKey
```

![ssskeylogin](https://user-images.githubusercontent.com/15084301/34913941-faedc298-f92e-11e7-859a-923e8f23a22e.png)

## Prepare to deploy your project
### Firewall setup
```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2200/tcp
sudo ufw allow www 
sudo ufw allow 123/udp
```

![firewalsetup](https://user-images.githubusercontent.com/15084301/34913940-faaf6944-f92e-11e7-9fbc-5958e20c82e3.png)

### Configure the local timezone to UTC.
```
sudo dpkg-reconfigure tzdata
```
* Choose none of the above

![timezone1](https://user-images.githubusercontent.com/15084301/34913944-fbc2b5fc-f92e-11e7-872e-f4dc9d8e20e9.png)

* choose UTC

![timezone2](https://user-images.githubusercontent.com/15084301/34913945-fc2b8226-f92e-11e7-9896-aeb45a4e22d9.png)

### Install and configure Apache to serve a Python mod_wsgi application.
* Install Apache
```
sudo apt-get install apache2
```
* Apache, by default, serves its files from the /var/www/html directory and we will use var/www/ as our root directory.

* Now configure Apache to hand-off certain requests to an application handler - mod_wsgi.

```
1. Install mod_wsgi

sudo apt-get install libapache2-mod-wsgi
```
* We need to enable mod wsgi if it isn't enabled: 
```
sudo a2enmod wsgi
```

```
2. You then need to configure Apache to handle requests using the WSGI module. You’ll do this by editing the /etc/apache2/sites-enabled/000-default.conf file.Add the following line at the end of the <VirtualHost *:80> block.

sudo nano /etc/apache2/sites-enabled/000-default.conf 

<VirtualHost *:80>
  ServerName  YourPublicIP[13.126.222.78]
  #Location of the items-catalog WSGI file
  WSGIScriptAlias / /var/www/itemCatalog/vagrant/catalog/itemCatalog.wsgi
  #Allow Apache to serve the WSGI app from our catalog directory
  <Directory /var/www/itemCatalog/vagrant/catalog>
        Order allow,deny
        Allow from all
  </Directory>
  #Allow Apache to deploy static content
  <Directory /var/www/itemCatalog/vagrant/catalog/static>
        Order allow,deny
        Allow from all
  </Directory>
.
.
.
.
</VirtualHost>
```
* This /var/www/itemCatalog is the cloned github repo for item catalog project as part of fullstack nanodegree course from Udacity.

![apachedefaultconf](https://user-images.githubusercontent.com/15084301/34913938-fa3338a6-f92e-11e7-9f95-e9c23279fde3.png)

```
3. Web server configuration to serve the Item Catalog application as a WSGI app. 
Create file itemCatalog.wsgi in below path
sudo nano /var/www/itemCatalog/vagrant/catalog/itemCatalog.wsgi

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/itemCatalog/vagrant/catalog')

from application import app as application
application.secret_key='super_secret_key'
``` 

![wsgifile](https://user-images.githubusercontent.com/15084301/34913946-fc90ea12-f92e-11e7-9984-fede80784269.png)

### Install and configure PostgreSQL:
```
sudo apt-get install postgresql
```

![postgresqlinstall](https://user-images.githubusercontent.com/15084301/34913821-cdba44ce-f92c-11e7-9c59-b8885b1b5dcd.png)

* Connect as user 'postgres' and type psql to entert the postgres terminal [check the image for reference]
 
```
grader@PublicIP~$ sudo su postgres
postgres@PublicIP~$ psql
```
* Type below commands in postgres terminal
```
postgres=# CREATE USER catalog WITH PASSWORD 'catalog';
postgres=# ALTER USER catalog CREATEDB;
postgres=# CREATE DATABASE catalog WITH OWNER catalog;
```

![postgresql1](https://user-images.githubusercontent.com/15084301/34913817-cc65dd40-f92c-11e7-87e8-bf74528d1d05.png)

* Connect to the catalog database: \c catalog
```
catalog=# REVOKE ALL ON SCHEMA public FROM public;
catalog=# GRANT ALL ON SCHEMA public TO catalog;
```

![postgresql2](https://user-images.githubusercontent.com/15084301/34913819-ccfa4d22-f92c-11e7-89d2-e4d7c6599469.png)

* Exit postgres and postgres user
```
catalog=# \q
```
```
postgres@PublicIP~$ exit
grader@PublicIP~$
```

### Install git
```
sudo apt-get install git
```

## Deploy the Item Catalog project.
### Install Project Dependencies packages
```
sudo apt-get install python-pip python-flask python-sqlalchemy python-psycopg2
sudo pip install oauth2client requests httplib2 passlib flask-httpauth
```
### Clone and setup your Item Catalog project from the Github
* Clone the item catalog project into the apache directory.
```
cd /var/www
sudo git clone https://github.com/gauravsinghaec/Fullstack-Nanodegree-Projects.git  itemsCatalog
```

![gitclone](https://user-images.githubusercontent.com/15084301/34913815-cbfe95f4-f92c-11e7-9cfa-c56815ffcc6a.png)

* Update model.py to replace sqlite3 connection with postgresql
```
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
```
![model](https://user-images.githubusercontent.com/15084301/34913808-bba1e5a8-f92c-11e7-8219-03b3ab06e779.png)

* Update application.py too
```
replace sqlite3 connection with postgresql

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

update path to client_secret.json and fb_client_secret.json
```
![application1](https://user-images.githubusercontent.com/15084301/34913812-ca7bd3f4-f92c-11e7-8c60-7cbacee3e3a4.png)
![application2](https://user-images.githubusercontent.com/15084301/34913813-cad61026-f92c-11e7-8be0-18855dbf460f.png)
![application3](https://user-images.githubusercontent.com/15084301/34913814-cb5b0f7e-f92c-11e7-8a2c-086aaed08afb.png)

## Run the application using public IP of AWS instance
* Public IP: 13.126.222.78
* URL to access project : http://13.126.222.78/catalog

## Authors
* **Gaurav Singh** - *Initial work* - [ItemCatalog Project](https://github.com/gauravsinghaec/Fullstack-Nanodegree-Projects/tree/master/vagrant/catalog)
									  [RestaurantMenuApp](https://github.com/gauravsinghaec/RestaurantMenuApp)
                                      [Building-Basic-WikiPage](https://github.com/gauravsinghaec/Building-Basic-WikiPage)
                                      [Building-Basic-Blog](https://github.com/gauravsinghaec/Building-Basic-Blog)                                                                            

## License


## Acknowledgments

* Special thanks to Udacity Team

## Bibiliography
[Harushimo](https://github.com/harushimo/linux-server-configuration)
[Apache Documentation](https://httpd.apache.org/docs/2.2/configuring.html)
[WSGI](http://wsgi.readthedocs.io/en/latest/)
[WSGI-Intro](http://ivory.idyll.org/articles/wsgi-intro/what-is-wsgi.html)
[Configuring Linux Web Servers](https://in.udacity.com/course/configuring-linux-web-servers--ud299)
