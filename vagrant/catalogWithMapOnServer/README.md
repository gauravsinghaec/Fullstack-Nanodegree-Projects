# Item Catalog Project with Neighborhood Map

This is the complete Fullstack 2 Nanodegree project. I have combined the
catalog and neighborhood map project.

## Getting Started

Copy the neighbohood-map static files(js and css) and index.html into
catalog project static and template folders.
[I changed index.html to map.html]

Update app.js of neighbohood-map to include AJAX call to read locations
data from /location.json endpoint
```
var locationURL = '/location.json';
$.ajax({
	type: "GET",
	url: locationURL,
	headers: {
      'Content-Type': 'application/json',
  	}
}).done(function(response) {
	
	var intialLocationsFromServer = response['Places'];
	
	var Place = function(){..........};

	var ViewModel = function(){.........};

	ko.applyBindings(new ViewModel());

}).fail(function(response) {
		console.log(response)
});	

```

Update map.html of neighbohood-map to update static files path
comment ko.applyBindings(new ViewModel()) line in html as ViewModel won't be available until ajax call in app.js above is completed.
[ko.applyBindings(new ViewModel()) is included in app.js, ash shown above]
```
e.g
<head>
	.
	.
    <link rel="stylesheet" type="text/css" href="{{url_for('static', filename='css/app.css')}}">
</head>
<body>
    <div class="main">
    .
    .
    </div>
    <script type="text/javascript" src="{{url_for('static', filename='js/lib/jQuery.js')}}"></script>        
    <script type="text/javascript" src="{{url_for('static', filename='js/lib/knockout-3.2.0.js')}}"></script>

    <script type="text/javascript">    
        var map, largeInfowindow;        
        function initMap(){
            // Constructor creates a new map - only center and zoom are required.
            map = new google.maps.Map(document.getElementById('map'),
            {
                center: {lat: 26.996471, lng: 75.876472},
                zoom: 10
            });
            largeInfowindow = new google.maps.InfoWindow();
        
            //To Activate Knockout through app.js
            // ko.applyBindings(new ViewModel());
        }
        function googleError(){
            document.getElementById('map-error').textContent = 'Error in Map!';
        }            
    </script>    
    <script type="text/javascript" src="{{url_for('static', filename='js/app.js')}}"></script>        
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBtsirN68OAeo4fv8o0iEOZ5dJlEAHLUxA&callback=initMap" onerror="googleError()">
    </script>     
</body>
```

Update model.py to include Location table 
```
class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    lattitude = Column(String(10), nullable=False)
    longitude = Column(String(10), nullable=False)

    @property
    def serializeLocations(self):
        #returns object data in serialized format
        return {
            "title": self.title,
            "location" :{"lat": self.lattitude,"lng":self.longitude},
        }

```

Add two new endpoints in application.py
```
@app.route('/location.json')
def locationJSON():
    locations = session.query(Location).all()
    listLocations=[]
    j=0
    for i in locations:
        if i.serializeLocations !=[]:
            listLocations.append(i.serializeLocations)
        j=j+1
    response = jsonify(Places=listLocations)
    return response    

@app.route('/map')
def locationMap():
    return render_template('map.html')
```

Load locations data in location table (check metadat in loadLocationData.sql)
```
Run the insert query in catalog DB
```

Run below to set up the database required for the application
```
python models.py
```

Run below to start the application at http://localhost:8000/catalog
```
python application.py
```


Use below URL to login 
```
http://localhost:8000/login
```

Use below URL to logout 
```
http://localhost:8000/logout
```

Use below URL to register
```
http://localhost:8000/signup
```
* username  Min 3 and Maximum 20 character among special character only underscore & hyphen are allowed . No spaces
* password  Min 3 and Maximum 20 character


### API JSON Endpoint
http://localhost:8000/locations.json
* Login is required to access the above endpoint

### Prerequisites
* Item Catalog, Neighborhood Map, Linux Server Configuration projects

## Authors

* **Gaurav Singh** - *Initial work* - [1-ItemCatalog Project /](https://github.com/gauravsinghaec/Fullstack-Nanodegree-Projects/tree/master/vagrant/catalog)
									  [2-RestaurantMenuApp /](https://github.com/gauravsinghaec/RestaurantMenuApp)
                                      [3-Building-Basic-WikiPage /](https://github.com/gauravsinghaec/Building-Basic-WikiPage)
                                      [4-Building-Basic-Blog](https://github.com/gauravsinghaec/Building-Basic-Blog) 
                                      [5-AWS Linux Server Configuration](https://github.com/gauravsinghaec/Fullstack-Nanodegree-Projects/tree/master/vagrant/linuxserverconfiguration)                                                                           

## Acknowledgments

* Special thanks to Udacity Team
* Hat tip to anyone who's code was used
* Inspiration
