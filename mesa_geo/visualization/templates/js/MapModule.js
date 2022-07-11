const MapModule = function (view, zoom, map_width, map_height) {
    // Create the map tag
    const map_tag = document.createElement("div");
    map_tag.style.width = map_width + "px";
    map_tag.style.height = map_height + "px";
    map_tag.style.border = "1px dotted";
    map_tag.id = "mapid"

    // Append it to #elements
    const elements = document.getElementById("elements");
    elements.appendChild(map_tag);

    // Create Leaflet map and Agent layers
    const Lmap = L.map('mapid', {zoomSnap: 0.1}).setView(view, zoom)
    let agentLayer = L.geoJSON().addTo(Lmap)

    // create the OSM tile layer with correct attribution
    const osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    const osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
    const osm = new L.TileLayer(osmUrl, {minZoom: 0, maxZoom: 18, attribution: osmAttrib})
    Lmap.addLayer(osm)

    this.renderLayers = function (layers) {
        layers.rasters.forEach(function (layer) {
            L.imageOverlay(layer, layers.total_bounds).addTo(Lmap)
        })
        layers.vectors.forEach(function (layer) {
            L.geoJSON(layer).addTo(Lmap)
        })
        // if (layers.total_bounds.length !== 0) {
        //     Lmap.fitBounds(layers.total_bounds)
        // }
    }

    this.renderAgents = function (agents) {
        agentLayer.remove()
        agentLayer = L.geoJSON(agents, {
            onEachFeature: PopUpProperties,
            style: function (feature) {
                return feature.properties.style
            },
            pointToLayer: function (feature, latlang) {
                return L.circleMarker(latlang, feature.properties.pointToLayer);
            }
        }).addTo(Lmap)
    }

    this.render = function (data) {
        this.renderLayers(data.layers)
        this.renderAgents(data.agents)
    }

    this.reset = function () {
        agentLayer.remove()
    }
}


function PopUpProperties(feature, layer) {
    let popupContent = '<table>'
    if (feature.properties.popupProperties) {
        for (const p in feature.properties.popupProperties) {
            popupContent += '<tr><td>' + p + '</td><td>' + feature.properties.popupProperties[p] + '</td></tr>'
        }
    }
    popupContent += '</table>'
    layer.bindPopup(popupContent)
}