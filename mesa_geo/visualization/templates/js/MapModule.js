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
            L.imageOverlay(layer, layers.bounds).addTo(Lmap)
        })
        layers.vectors.forEach(function (layer) {
            L.geoJSON(layer).addTo(Lmap)
        })
        // if (layers.bounds.length !== 0) {
        //     Lmap.fitBounds(layers.bounds)
        // }
    }

    this.renderAgents = function (agents) {
        agentLayer.remove()
        agentLayer = L.geoJSON(agents, {
            onEachFeature: PopUpProperties,
            style: function (feature) {
                return {color: feature.properties.color};
            },
            pointToLayer: function (feature, latlang) {
                return L.circleMarker(latlang, {radius: feature.properties.radius, color: feature.properties.color});
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
    if (feature.properties) {
        for (const p in feature.properties) {
            popupContent += '<tr><td>' + p + '</td><td>' + feature.properties[p] + '</td></tr>'
        }
    }
    popupContent += '</table>'
    layer.bindPopup(popupContent)
}