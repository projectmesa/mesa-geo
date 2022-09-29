import warnings

import mesa


class ModularServer(mesa.visualization.ModularServer):
    def __init__(
        self,
        model_cls,
        visualization_elements,
        name="Mesa Model",
        model_params=None,
        port=None,
    ):
        super().__init__(model_cls, visualization_elements, name, model_params, port)

    def launch(self, port=None, open_browser=True):
        warnings.warn(
            "Importing ModularServer from mesa_geo is deprecated, and will be removed in a future release. "
            "Import from mesa instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().launch(port, open_browser)
