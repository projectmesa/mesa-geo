const MapModule = function (view, zoom, map_width, map_height, tiles, scale_options) {
    // Create the map tag
    const map_tag = document.createElement("div");
    map_tag.style.width = map_width + "px";
    map_tag.style.height = map_height + "px";
    map_tag.style.border = "1px dotted";
    map_tag.id = "mapid"
    const customView = (view !== null && zoom !== null)

    // Append it to #elements
    const elements = document.getElementById("elements");
    elements.appendChild(map_tag);

    // Create Leaflet map and Agent layers
    const Lmap = L.map('mapid', {zoomSnap: 0.1})
    if (customView) {
        Lmap.setView(view, zoom)
    }
    if (scale_options !== null) {
        L.control.scale(scale_options).addTo(Lmap)
    }
    let agentLayer = L.geoJSON().addTo(Lmap)

    // create tile layer
    if (tiles !== null) {
        if (tiles.kind === "raster_web_tile") {
            L.tileLayer(tiles.url, tiles.options).addTo(Lmap)
        } else if (tiles.kind === "wms_web_tile") {
            L.tileLayer.wms(tiles.url, tiles.options).addTo(Lmap)
        } else {
            throw new Error("Unknown tile type: " + tiles.kind)
        }
    }

    let mapLayers = []
    let hasFitBounds = false
    this.renderLayers = function (layers) {
        mapLayers.forEach(layer => {layer.remove()})
        mapLayers = []

        layers.rasters.forEach(function (layer) {
            const rasterLayer = L.imageOverlay(layer, layers.total_bounds).addTo(Lmap)
            mapLayers.push(rasterLayer)
        })
        layers.vectors.forEach(function (layer) {
            const vectorLayer = L.geoJSON(layer).addTo(Lmap)
            mapLayers.push(vectorLayer)
        })
        if (!hasFitBounds && !customView && layers.total_bounds.length !== 0) {
            Lmap.fitBounds(layers.total_bounds)
            hasFitBounds = true
        }
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
        mapLayers.forEach(layer => {layer.remove()})
        mapLayers = []
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