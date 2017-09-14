var MapModule = function (view, zoom, map_width, map_height){
  // Create the tag:
  var map_tag = "<div style='width:" + map_width + "px; height:" + map_height + "px;border:1px dotted' id='mapid'></div>";
  // Append it to body:
  var div = $(map_tag)[0];
  $('#elements').append(div);

  // Create Leaflet map and Agent layers
  var mymap = L.map('mapid').setView(view, zoom);
  var AgentLayer = L.geoJSON().addTo(mymap);

  // create the tile layer with correct attribution
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 0, maxZoom: 14, attribution: osmAttrib});
  mymap.addLayer(osm);

  this.render = function(data) {

    function onEachFeature(feature, layer) {
      popupContent = "<table>"
      if (feature.properties){
        for (var p in feature.properties) {
            popupContent += '<tr><td>' + p + '</td><td>'+ feature.properties[p] + '</td></tr>';
        }
      }
      popupContent += '</table>';
      layer.bindPopup(popupContent)
    }

    AgentLayer.remove()
    AgentLayer = L.geoJSON(data[0], {
      onEachFeature: onEachFeature,
      style: function(feature) {
        switch (feature.properties.atype) {
            case 1: return {color: "#ff0000", opacity: 0.65, weight: 3};
            case 0: return {color: "#0000ff", opacity: 0.65, weight: 3};
        }
      }
    }).addTo(mymap);
  }

  this.reset = function() {
    mymap.remove()
    mymap = L.map('mapid').setView(view, zoom);
    mymap.addLayer(osm);
  }
};
