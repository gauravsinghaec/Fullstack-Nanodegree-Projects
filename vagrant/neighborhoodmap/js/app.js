// These are the neighborhood locations that will be shown to the user.
// Normally we'd have these in a database instead.
var intialLocationsFromServer =  [{
               title: 'Amer Fort, Jaipur', 
               location: {lat: 26.996471, lng: 75.876472}
               },
               {
               title: 'Jodhpur, Rajasthan', 
               location: {lat: 26.263863, lng: 73.008957}                  
               },
               {
               title: 'Pushkar, Rajasthan', 
               location: {lat: 26.489679, lng: 74.550941}                  
               },
               {
               title: 'Jaipur, Rajasthan', 
               location: {lat: 26.922070, lng: 75.778885}
               },
               {
               title: 'Jaisalmer, Rajasthan', 
               location: {lat: 26.911661, lng: 70.922928}                  
               },
               {
               title: 'Ajmer, Rajasthan', 
               location: {lat: 26.449896, lng: 74.639915}                  
               },
               {
               title: 'Udaipur, Rajasthan', 
               location: {lat: 24.571270, lng: 73.691544}                 
               },               
               {
               title: 'Pokharan, Rajasthan', 
               location: {lat: 26.920542, lng: 71.916550}                  
               },
               {
               title: 'Pali, Rajasthan', 
               location: {lat: 25.771315, lng: 73.323685}                  
               }               
            ];

var Place = function(data){
				this.title = data.title,
         	this.position = data.location
};

var ViewModel = function(){
            var self = this;

            this.locationList = ko.observableArray([]);

            this.filterInputText = ko.observable('');
            
            intialLocationsFromServer.forEach(function(place){
               self.locationList.push(new Place(place));
            });
				

            this.filterLocationList = function(data,event){
                 filter = $('#filter-text').val().toUpperCase();
                 self.filterWithinLocationList(filter);
                 return true;
            };

            self.filterWithinLocationList = function (inputText){
              for (var i = 0; i < self.markers.length; i++) {
                var refText=self.markers[i].title.toUpperCase();
                if (refText.indexOf(inputText) != -1) {
                  self.markers[i].setMap(map);
                } else {
                  self.markers[i].setMap(null);
                }
              }
              self.locationList([]);
               intialLocationsFromServer.forEach(function(place){
                  var refText=place.title.toUpperCase();
                  if (refText.indexOf(inputText) != -1) {
                     self.locationList.push(new Place(place));
                  }                                    
               });              
            };

            this.selectThisLocation = function(){
               // self.currentLocation(this);
               // $('#filter-text').val(this.title);
               self.filterInputText(this.title);
               self.searchWithinLocationList(this);
            };

            // This function hides all markers outside the polygon,
            // and shows only the ones within it. This is so that the
            // user can specify an exact area of search.
            self.searchWithinLocationList = function(place){
              for (var i = 0; i < self.markers.length; i++) {
                if (place.title == self.markers[i].title) {
                  self.markers[i].setAnimation(google.maps.Animation.BOUNCE);
                  populateInfoWindow(self.markers[i], self.largeInfowindow);
                } else {
                  self.markers[i].setAnimation(null);
               }
              }
            };
            // This function populates the infowindow when the marker is clicked. We'll only allow
            // one infowindow which will open at the marker that is clicked, and populate based
            // on that markers position.

            var populateInfoWindow = function(marker, infowindow) {
               // Check to make sure the infowindow is not already opened on this marker.
               if (infowindow.marker != marker) {

                  if(infowindow.marker)
                     {
                        infowindow.marker.setAnimation(null);
                     }
                  marker.setAnimation(google.maps.Animation.BOUNCE);
                  infowindow.marker = marker;
                  infowindow.setContent('<div>' + marker.title + '</div>');
                  infowindow.open(map, marker);
                  // Make sure the marker property is cleared if the infowindow is closed.
                  infowindow.addListener('closeclick',function(){
                     infowindow.marker = null;
                     marker.setAnimation(null);
                     self.filterInputText('');
                  });

                  ajaxCallForWikiData(marker, infowindow);

               }
            };            

            var ajaxCallForWikiData = function(marker, infowindow) {
                  var $wikidiv =$('<div class="wiki"><h4>Relevant Wikipedia Links</h4></div>');       
                  var $wikiElem = $('<ul id="wikipedia-links"></ul>');    
                  var $address = marker.title;
                  var wikiurl = "https://en.wikipedia.org/w/api.php?action=opensearch&search="+$address + '&format=json&callback=wikiCallback';
                    //? action=query&titles=Main%20Page&prop=revisions&rvprop=content&format=json";
                  //console.log(wikiurl);
                  var $wikilink ;           
                  var $wikilinkdata;                  
                  //Adding a Timer and executing an annonymous fallback function to set the failed wiki text element 
                  //if the response is not received
                  var wikiRequestTimeout = setTimeout(function(){
                    $wikiElem.text("Failed to get wikipedia resources");
                  },8000);
                    

                  $.ajax({
                  url: wikiurl,
                  dataType: "jsonp",      
                  success: function(response){
                            var addresswikilist = response[1];
                            $wikidiv.append($wikiElem);
                            for (var i=0;i<addresswikilist.length;i++)    {
                                $wikilinkdata = addresswikilist[i];
                                $wikilink  = 'http://en.wikipedia.org/wiki/'+ $wikilinkdata ;
                                var $wikiElemItem = '<li><a target ="_blank" href="'+$wikilink+ '">' +$wikilinkdata+ '</a>'+'</li>';
                                $wikiElem.append($wikiElemItem);  
                            }
                            //clearing the timer once wiki responce is received and element is added in the section
                            clearTimeout(wikiRequestTimeout);
                        }
                  }).done(function(response) {
                     console.log( "AJAX wiki call success" )
                     infowindow.setContent('<div>' + marker.title + '</div>'+$('<div />').append($wikidiv).html());
                  }).fail(function() {
                     infowindow.setContent('<div>' + marker.title + '</div>' +
                      '<div>No Wiki Link Found</div>');
                  });               
            }

            // Create a new blank array for all the listing markers.
            self.markers = [];

            // Constructor creates a new map - only center and zoom are required.
            var map = new google.maps.Map(document.getElementById('map'), {
             center: {lat: 26.996471, lng: 75.876472},
             zoom: 10
            });

            self.largeInfowindow = new google.maps.InfoWindow();
            var bounds = new google.maps.LatLngBounds();

            // The following group uses the location array to create an array of markers on initialize.
            for (var i = 0; i < this.locationList().length; i++) {
             // Get the position from the location array.
             var position = self.locationList()[i].position;
             var title = self.locationList()[i].title;
             // Create a marker per location, and put into markers array.
             var marker = new google.maps.Marker({
               map: map,
               position: position,
               title: title,
               animation: google.maps.Animation.DROP,
               id: i
             });
             // Push the marker to our array of markers.
             self.markers.push(marker);
             // Create an onclick event to open an infowindow at each marker.
             marker.addListener('click', function() {
               populateInfoWindow(this, self.largeInfowindow);
             });
             bounds.extend(self.markers[i].position);
            }
            // Extend the boundaries of the map for each marker
            map.fitBounds(bounds);

};

ko.applyBindings(new ViewModel());