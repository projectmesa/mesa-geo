var MapModule = function (view, zoom, map_width, map_height) {
  // Create the map tag:
  var map_tag = "<div style='width:" + map_width + "px; height:" + map_height + "px;border:1px dotted' id='mapid'></div>"
  // Append it to body:
  var div = $(map_tag)[0]
  $('#elements').append(div)

  // Create Leaflet map and Agent layers
  var Lmap = L.map('mapid').setView(view, zoom)
  var AgentLayer = L.geoJSON().addTo(Lmap)


  // create the OSM tile layer with correct attribution
  var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
  var osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
  var osm = new L.TileLayer(osmUrl, {minZoom: 0, maxZoom: 18, attribution: osmAttrib})
  Lmap.addLayer(osm)

  this.render = function (data) {
    function PopUpProperties (feature, layer) {
      var popupContent = '<table>'
      if (feature.properties) {
        for (var p in feature.properties) {
          popupContent += '<tr><td>' + p + '</td><td>' + feature.properties[p] + '</td></tr>'
        }
      }
      popupContent += '</table>'
      layer.bindPopup(popupContent)
    }

    AgentLayer.remove()
    console.log(data)
    AgentLayer = L.geoJSON(data, {
      onEachFeature: PopUpProperties,
      style: function (feature) {
        return {color: feature.properties.color}
      }
    }).addTo(Lmap)
  }

  this.reset = function () {
    Lmap.remove()
    Lmap = L.map('mapid').setView(view, zoom)
    Lmap.addLayer(osm)
  }
}
