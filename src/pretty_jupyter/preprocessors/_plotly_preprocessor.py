from nbconvert.preprocessors import Preprocessor

from pretty_jupyter._plotly import figure_to_html
from pretty_jupyter.constants import PLOTLY_MIMETYPE


class PlotlyPreprocessor(Preprocessor):
    """
    Makes plotly figures interactive in the html output.

    When a notebook is executed outside of JupyterLab (e.g. ``jupyter nbconvert --execute``) or with
    recent plotly versions, ``fig.show()`` only stores the ``application/vnd.plotly.v1+json`` mime
    type, possibly next to a static image. nbconvert can't render that mime type, so the html showed
    the static image (or nothing). This preprocessor adds an interactive ``text/html``
    representation, which has priority over images. Outputs that already have html are left alone.
    """

    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type != "code":
            return cell, resources

        for output_index, output in enumerate(cell.get("outputs", [])):
            data = output.get("data", {})
            if PLOTLY_MIMETYPE not in data or "text/html" in data:
                continue
            figure = data[PLOTLY_MIMETYPE]
            if not isinstance(figure, dict):
                continue
            # deterministic ids keep repeated exports byte-identical
            div_id = f"pj-plotly-{index}-{output_index}"
            data["text/html"] = figure_to_html(figure, div_id)

        return cell, resources
