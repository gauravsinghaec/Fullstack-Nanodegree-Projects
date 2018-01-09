# Neighborhood Map Project

You will develop a single page application featuring a map of your neighborhood or a neighborhood you would like to visit. You will then add additional functionality to this map including highlighted locations, third-party data about those locations and various ways to browse the content.

## Getting Started
* Root directory contains "src" , "dist" directories and gulp files.
* Go to "src" directory
* Open index.html to see the Neighborhood Map application
```
open index.html  any browser.
```
## Using Wiki as Thirt Party API 
```
We will obtain wiki data using AJAX call and show it in infowindow.
```

## Instructions for building and running the project using Gulp tool
Dependencies
```
    "gulp": "^3.9.1",
    "gulp-autoprefixer": "^4.0.0",
    "gulp-concat": "^2.6.1",
    "gulp-eslint": "^4.0.0",
    "gulp-order": "^1.1.1",
    "gulp-sass": "^3.1.0",
    "gulp-uglify": "^3.0.0"
    "browser-sync": "^2.18.13",    
    "gulp-jasmine-phantom": "^3.0.0",    
```

* Install above dependencies using 'npm install' command from root directory.
```
--> npm install <plugin-to-install>
```
* node_modules directory will be created with all the dependencies.
* All source files are inside "src" directory.
* Update gulpfile.js if need as per your directory structure.
* Create "dist" directory with empty "css" and "js" directory. 
* Run below to execute gulp task "dist" to create production files from root directory.
```
--> gulp dist
```
* Edit index.html to remove javascript files "jQuery.js" ,"knockout.js" and "app.js" from index.html 
* and replace with one "js/all.js" . 
* Go to "dist" directory
* Open index.html to see the Neighborhood Map application
```
open index.html  any browser.
```


## Authors
* **Gaurav Singh** - *Initial work* - [ItemCatalog Project](https://github.com/gauravsinghaec/Fullstack-Nanodegree-Projects/tree/master/vagrant/catalog)
									  [RestaurantMenuApp](https://github.com/gauravsinghaec/RestaurantMenuApp)

## License


## Acknowledgments

* Special thanks to Udacity Team
* Hat tip to anyone who's code was used
* Inspiration
