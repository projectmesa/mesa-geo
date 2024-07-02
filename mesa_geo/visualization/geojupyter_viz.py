import sys

import matplotlib.pyplot as plt
import mesa.experimental.components.matplotlib as components_matplotlib
import solara
import xyzservices.providers as xyz
from mesa.experimental import jupyter_viz as jv
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
    current_step,
    color,
    layout_type,
):
    with rv.Card(
        style_=f"background-color: {color}; width: 100%; height: 100%"
    ) as main:
        if "Map" in layout_type:
            rv.CardTitle(children=["Map"])
            leaflet_viz.map(model, map_drawer, zoom, center_default)

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
    tiles=xyz.OpenStreetMap.Mapnik,
    center_point=None,  # Due to projection challenges in calculation allow user to specify center point
):
    """Initialize a component to visualize a model.
    Args:
        model_class: class of the model to instantiate
        model_params: parameters for initializing the model
        measures: list of callables or data attributes to plot
        name: name for display
        agent_portrayal: options for rendering agents (dictionary)
        space_drawer: method to render the agent space for
            the model; default implementation is the `SpaceMatplotlib` component;
            simulations with no space to visualize should
            specify `space_drawer=False`
        play_interval: play interval (default: 150)
        center_point: list of center coords
    """
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
    )
    layers = map_drawer.render(model)

    # determine center point
    if center_point:
        center_default = center_point
    else:
        bounds = layers["layers"]["total_bounds"]
        center_default = list((bounds[2:] + bounds[:2]) / 2)

    def render_in_jupyter():
        # TODO: Build API to allow users to set rows and columns
        # call in property of model layers geospace line; use 1 column to prevent map overlap

        with solara.Row(
            justify="space-between", style={"flex-grow": "1"}
        ) and solara.GridFixed(columns=2):
            jv.UserInputs(user_params, on_change=handle_change_model_params)
            jv.ModelController(model, play_interval, current_step, reset_counter)
            solara.Markdown(md_text=f"###Step - {current_step}")

        # Builds Solara component of map
        leaflet_viz.map_jupyter(model, map_drawer, zoom, center_default)

        # Place measurement in separate row
        with solara.Row(
            justify="space-between",
            style={"flex-grow": "1"},
        ):
            # 5. Plots
            for measure in measures:
                if callable(measure):
                    # Is a custom object
                    measure(model)
                else:
                    components_matplotlib.PlotMatplotlib(
                        model, measure, dependencies=[current_step.value]
                    )

    def render_in_browser():
        # determine center point
        if center_point:
            center_default = center_point
        else:
            bounds = layers["layers"]["total_bounds"]
            center_default = list((bounds[2:] + bounds[:2]) / 2)

        # if space drawer is disabled, do not include it
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

    if ("ipykernel" in sys.argv[0]) or ("colab_kernel_launcher.py" in sys.argv[0]):
        # When in Jupyter or Google Colab
        render_in_jupyter()
    else:
        render_in_browser()
