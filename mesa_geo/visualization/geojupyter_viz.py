import warnings

import matplotlib.pyplot as plt
import mesa.visualization.components.matplotlib_components as components_matplotlib
import solara
import xyzservices.providers as xyz
from mesa.visualization import solara_viz as jv
from solara.alias import rv

import mesa_geo.visualization.leaflet_viz as leaflet_viz

# Avoid interactive backend
plt.switch_backend("agg")


# TODO: Turn this function into a Solara component once the current_step.value
# dependency is passed to measure()
"""
Geo-Mesa Visualization Module
=============================
Card: Helper Function that initiates the Solara Card for Browser
GeoJupyterViz: Main Function users employ to create visualization
"""


def Card(
    model,
    measures,
    agent_portrayal,
    map_drawer,
    center_default,
    zoom,
    scroll_wheel_zoom,
    current_step,
    color,
    layout_type,
):
    """


    Parameters
    ----------
    model : Mesa Model Object
        A pointer to the Mesa Model object this allows the visual to get get
        model information, such as scheduler and space.
    measures : List
        Plots associated with model typically from datacollector that represent
        critical information collected from the model.
    agent_portrayal : Dictionary
        Contains details of how visualization should plot key elements of the
        such as agent color etc
    map_drawer : Method
        Function that generates map from GIS data of model
    center_default : List
        Latitude and Longitude of where center of map should be located
    zoom : Int
        Zoom level at which to initialize the map
    scroll_wheel_zoom: Boolean
        True of False on whether user can zoom on map with mouse scroll wheel
        default is True
    current_step : Int
        Number on which step is the model
    color : String
        Background color for visual
    layout_type : String
        Type of layout Map or Measure

    Returns
    -------
    main : Solara object
        Visualization of model

    """

    with rv.Card(
        style_=f"background-color: {color}; width: 100%; height: 100%"
    ) as main:
        if "Map" in layout_type:
            rv.CardTitle(children=["Map"])
            leaflet_viz.map(model, map_drawer, zoom, center_default, scroll_wheel_zoom)

        if "Measure" in layout_type:
            rv.CardTitle(children=["Measure"])
            measure = measures[layout_type["Measure"]]
            if callable(measure):
                # Is a custom object
                measure(model)
            else:
                components_matplotlib.PlotMatplotlib(
                    model, measure, dependencies=[current_step.value]
                )
    return main


@solara.component
def GeoJupyterViz(
    model_class,
    model_params,
    measures=None,
    name=None,
    agent_portrayal=None,
    play_interval=150,
    # parameters for leaflet_viz
    view=None,
    zoom=None,
    scroll_wheel_zoom=True,
    tiles=xyz.OpenStreetMap.Mapnik,
    center_point=None,  # Due to projection challenges in calculation allow user to specify center point
):
    """


    Parameters
    ----------
    model_class : Mesa Model Object
        A pointer to the Mesa Model object this allows the visual to get get
        model information, such as scheduler and space.
    model_params : Dictionary
        Parameters of model with key being the parameter as a string and values being the options
    measures : List, optional
        Plots associated with model typically from datacollector that represent
        critical information collected from the model. The default is None.
    name : String, optional
        Name of simulation to appear on visual. The default is None.
    agent_portrayal : Dictionary, optional
        Dictionary of how the agent showed appear. The default is None.
    play_interval : INT, optional
        Rendering interval of model. The default is 150.
    # parameters for leaflet_viz
    view : List, optional
        Bounds of map to be displayed; must be set with zoom. The default is None.
    zoom : Int, optional
        Zoom level of map on leaflet
    scroll_wheel_zoom : Boolean, optional
        True of False for whether or not to enable scroll wheel. The default is True.
        Recommend False when using jupyter due to multiple scroll wheel options
    tiles : Data source for GIS data, optional
        Data Source for GIS map data. The default is xyz.OpenStreetMap.Mapnik.
    # Due to projection challenges in calculation allow user to specify
    center_point : List, optional
        Option to pass in center coordinates of map The default is None.. The default is None.


    Returns
    -------
        Provides information to Card to render model

    """

    warnings.warn(
        "`GeoJupyterViz` is deprecated and will be removed in a future release. Use Mesa's SolaraViz and Mesa-Geo's `make_geospace_leaflet` instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    if name is None:
        name = model_class.__name__

    current_step = solara.use_reactive(0)

    # 1. Set up model parameters
    user_params, fixed_params = jv.split_model_params(model_params)
    model_parameters, set_model_parameters = solara.use_state(
        {**fixed_params, **{k: v.get("value") for k, v in user_params.items()}}
    )

    # 2. Set up Model
    def make_model():
        model = model_class(**model_parameters)
        current_step.value = 0
        return model

    reset_counter = solara.use_reactive(0)
    model = solara.use_memo(
        make_model, dependencies=[*list(model_parameters.values()), reset_counter.value]
    )

    def handle_change_model_params(name: str, value: any):
        set_model_parameters({**model_parameters, name: value})

    # 3. Set up UI
    with solara.AppBar():
        solara.AppBarTitle(name)

    # 4. Set Up Map
    # render layout, pass through map build parameters
    map_drawer = leaflet_viz.MapModule(
        portrayal_method=agent_portrayal,
        view=view,
        zoom=zoom,
        tiles=tiles,
        scroll_wheel_zoom=scroll_wheel_zoom,
    )
    layers = map_drawer.render(model)

    # determine center point
    if center_point:
        center_default = center_point
    else:
        bounds = layers["layers"]["total_bounds"]
        center_default = [
            (bounds[0][0] + bounds[1][0]) / 2,
            (bounds[0][1] + bounds[1][1]) / 2,
        ]

    # Build base data structure for layout
    layout_types = [{"Map": "default"}]

    if measures:
        layout_types += [{"Measure": elem} for elem in range(len(measures))]

    grid_layout_initial = jv.make_initial_grid_layout(layout_types=layout_types)
    grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)

    with solara.Sidebar():
        with solara.Card("Controls", margin=1, elevation=2):
            jv.UserInputs(user_params, on_change=handle_change_model_params)
            jv.ModelController(model, play_interval, current_step, reset_counter)
        with solara.Card("Progress", margin=1, elevation=2):
            solara.Markdown(md_text=f"####Step - {current_step}")

    items = [
        Card(
            model,
            measures,
            agent_portrayal,
            map_drawer,
            center_default,
            zoom,
            scroll_wheel_zoom,
            current_step,
            color="white",
            layout_type=layout_types[i],
        )
        for i in range(len(layout_types))
    ]

    solara.GridDraggable(
        items=items,
        grid_layout=grid_layout,
        resizable=True,
        draggable=True,
        on_grid_layout=set_grid_layout,
    )
