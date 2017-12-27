# Item Catalog Project

The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system.

## Getting Started

Run below to set up the database required for the application
  python models.py

Run below to start the application at http://localhost:8000/catalog
  python application.py

To view particular category, click items under category listing

To login 
http://localhost:8000/login

To logout 
http://localhost:8000/logout

To http://localhost:8000/signup
  username  Min 3 and Maximum 20 character among special character only underscore & hyphen are allowed . No spaces
  password  Min 3 and Maximum 20 character

* Login is required to create/edit/delete an item

### API JSON Endpoint
http://localhost:8000/catalog.json
* Login is required to access the above endpoint

### Prerequisites

Software requirement

```
Oracle Virtualbox
Vagrant
Flask==0.10.1
sqlite3
Flask-Login==0.2.11
Flask-SQLAlchemy==2.0
Jinja2==2.7.3
SQLAlchemy==0.9.7
decorator==3.4.0
itsdangerous==0.24
oauth2client==4.1.2
requests==2.18.4
httplib2==0.10.3
etc
```

### Installing

A step by step series of examples that tell you have to get a development env running is given at Udacity tutorial for Vagrant and Virtualbox installation

```
Check the udacity setup for projects
```


## Running the tests


## Deployment


## Built With

* [Flask](http://www.dropwizard.io/1.0.2/docs/) - The web framework used

## Contributing


## Versioning


## Authors

* **Gaurav Singh** - *Initial work* - [RestaurantMenuApp](https://github.com/gauravsinghaec/RestaurantMenuApp)

## License


## Acknowledgments

* Special thanks to Udacity Team
* Hat tip to anyone who's code was used
* Inspiration
