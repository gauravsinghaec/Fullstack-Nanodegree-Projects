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
```


```
sudo apt-get upgrade
```

### Create new user 'grader' and give 'grader' permissions
```
sudo adduser grader
```





### Configuring SSH to a non-default port
```
SSH default port is 22. We want to configure it to non default port. Since we are using LightSail, we need to open the non default port through the web interface. If you don't do this step, you'll be locked out of the instance. Go to the networking tab on the management console. Then, the firewall option
```


Go into your sshd config file and Change the following options. 
* sudo nano /etc/ssh/sshd_config 

```
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






## Prepare to deploy your project
### Firewall setup

### Configure the local timezone to UTC.
```
sudo dpkg-reconfigure tzdata
```

* Choose none of the above

* choose UTC


### Install and configure Apache to serve a Python mod_wsgi application.
```
sudo apt-get install apache2
```

* Apache, by default, serves its files from the /var/www/html directory and we will use var/www/ as our root directory.

* Now configure Apache to hand-off certain requests to an application handler - mod_wsgi.

```
1. Install mod_wsgi

sudo apt-get install libapache2-mod-wsgi
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



* 3. Web server configuration to serve the Item Catalog application as a WSGI app. 
* Create file itemCatalog.wsgi in below path
```
sudo nano /var/www/itemCatalog/vagrant/catalog/itemCatalog.wsgi

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/itemCatalog/vagrant/catalog')

from application import app as application
application.secret_key='super_secret_key'
``` 


### Install and configure PostgreSQL:
```
sudo apt-get install postgresql
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
* Clone the item catalog project



* Update model.py to replace sqlite3 connection with postgresql





* Update application.py too
```
replace sqlite3 connection with postgresql
update path to client_secret.json and fb_client_secret.json
```




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

