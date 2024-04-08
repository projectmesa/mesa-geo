import sys
import threading

import matplotlib.pyplot as plt
import reacton.ipywidgets as widgets
import solara
import xyzservices.providers as xyz
from solara.alias import rv

import mesa_geo.geoexperimental.components.matplotlib as components_matplotlib
import mesa_geo.geoexperimental.leaflet_viz as leaflet_viz
from mesa_geo.geoexperimental.UserParam import Slider

# TODO FIX for MESA GEO

# Avoid interactive backend
plt.switch_backend("agg")


# TODO: Turn this function into a Solara component once the current_step.value
# dependency is passed to measure()
"""
Geo-Mesa Visualization Module
=============================

Card: Helper Function that initiates the Solara Card for Browser
JupyterViz: Main Function users employ to create visualization

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
def JupyterViz(
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
    user_params, fixed_params = split_model_params(model_params)
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
            UserInputs(user_params, on_change=handle_change_model_params)
            ModelController(model, play_interval, current_step, reset_counter)
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

        grid_layout_initial = make_initial_grid_layout(layout_types=layout_types)
        grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)

        with solara.Sidebar():
            with solara.Card("Controls", margin=1, elevation=2):
                UserInputs(user_params, on_change=handle_change_model_params)
                ModelController(model, play_interval, current_step, reset_counter)
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


@solara.component
def ModelController(model, play_interval, current_step, reset_counter):
    playing = solara.use_reactive(False)
    thread = solara.use_reactive(None)
    # We track the previous step to detect if user resets the model via
    # clicking the reset button or changing the parameters. If previous_step >
    # current_step, it means a model reset happens while the simulation is
    # still playing.
    previous_step = solara.use_reactive(0)

    def on_value_play(change):
        if previous_step.value > current_step.value and current_step.value == 0:
            # We add extra checks for current_step.value == 0, just to be sure.
            # We automatically stop the playing if a model is reset.
            playing.value = False
        elif model.running:
            do_step()
        else:
            playing.value = False

    def do_step():
        model.step()
        previous_step.value = current_step.value
        current_step.value = model._steps

    def do_play():
        model.running = True
        while model.running:
            do_step()

    def threaded_do_play():
        if thread is not None and thread.is_alive():
            return
        thread.value = threading.Thread(target=do_play)
        thread.start()

    def do_pause():
        if (thread is None) or (not thread.is_alive()):
            return
        model.running = False
        thread.join()

    def do_reset():
        reset_counter.value += 1

    def do_set_playing(value):
        if current_step.value == 0:
            # This means the model has been recreated, and the step resets to
            # 0. We want to avoid triggering the playing.value = False in the
            # on_value_play function.
            previous_step.value = current_step.value
        playing.set(value)

    with solara.Row():
        solara.Button(label="Step", color="primary", on_click=do_step)
        # This style is necessary so that the play widget has almost the same
        # height as typical Solara buttons.
        solara.Style(
            """
        .widget-play {
            height: 30px;
        }
        """
        )
        widgets.Play(
            value=0,
            interval=play_interval,
            repeat=True,
            show_repeat=False,
            on_value=on_value_play,
            playing=playing.value,
            on_playing=do_set_playing,
        )
        solara.Button(label="Reset", color="primary", on_click=do_reset)
        # threaded_do_play is not used for now because it
        # doesn't work in Google colab. We use
        # ipywidgets.Play until it is fixed. The threading
        # version is definite a much better implementation,
        # if it works.
        # solara.Button(label="▶", color="primary", on_click=viz.threaded_do_play)
        # solara.Button(label="⏸︎", color="primary", on_click=viz.do_pause)
        # solara.Button(label="Reset", color="primary", on_click=do_reset)


def split_model_params(model_params):
    model_params_input = {}
    model_params_fixed = {}
    for k, v in model_params.items():
        if check_param_is_fixed(v):
            model_params_fixed[k] = v
        else:
            model_params_input[k] = v
    return model_params_input, model_params_fixed


def check_param_is_fixed(param):
    if isinstance(param, Slider):
        return False
    if not isinstance(param, dict):
        return True
    if "type" not in param:
        return True


@solara.component
def UserInputs(user_params, on_change=None):
    """Initialize user inputs for configurable model parameters.
    Currently supports :class:`solara.SliderInt`, :class:`solara.SliderFloat`,
    :class:`solara.Select`, and :class:`solara.Checkbox`.

    Props:
        user_params: dictionary with options for the input, including label,
        min and max values, and other fields specific to the input type.
        on_change: function to be called with (name, value) when the value of an input changes.
    """

    for name, options in user_params.items():

        def change_handler(value, name=name):
            on_change(name, value)

        if isinstance(options, Slider):
            slider_class = (
                solara.SliderFloat if options.is_float_slider else solara.SliderInt
            )
            slider_class(
                options.label,
                value=options.value,
                on_value=change_handler,
                min=options.min,
                max=options.max,
                step=options.step,
            )
            continue

        # label for the input is "label" from options or name
        label = options.get("label", name)
        input_type = options.get("type")
        if input_type == "SliderInt":
            solara.SliderInt(
                label,
                value=options.get("value"),
                on_value=change_handler,
                min=options.get("min"),
                max=options.get("max"),
                step=options.get("step"),
            )
        elif input_type == "SliderFloat":
            solara.SliderFloat(
                label,
                value=options.get("value"),
                on_value=change_handler,
                min=options.get("min"),
                max=options.get("max"),
                step=options.get("step"),
            )
        elif input_type == "Select":
            solara.Select(
                label,
                value=options.get("value"),
                on_value=change_handler,
                values=options.get("values"),
            )
        elif input_type == "Checkbox":
            solara.Checkbox(
                label=label,
                on_value=change_handler,
                value=options.get("value"),
            )
        else:
            raise ValueError(f"{input_type} is not a supported input type")


def make_text(renderer):
    def function(model):
        solara.Markdown(renderer(model))

    return function


def make_initial_grid_layout(layout_types):
    return [
        {
            "i": i,
            "w": 6,
            "h": 10,
            "moved": False,
            "x": 6 * (i % 2),
            "y": 16 * (i - i % 2),
        }
        for i in range(len(layout_types))
    ]
