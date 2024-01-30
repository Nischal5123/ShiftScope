import draco as drc
import pandas as pd
from vega_datasets import data as vega_data
import altair as alt
from IPython.display import display, Markdown
import json
import numpy as np
from draco.renderer import AltairRenderer
alt.renderers.enable("png")

# Handles serialization of common numpy datatypes
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def md(markdown: str):
    display(Markdown(markdown))


def pprint(obj):
    md(f"```json\n{json.dumps(obj, indent=2, cls=NpEncoder)}\n```")

def localpprint(obj):
        print(json.dumps(obj, indent=2, cls=NpEncoder))

def recommend_charts(
    spec: list[str], draco: drc.Draco, df: pd.DataFrame, num: int = 5, labeler=lambda i: f"CHART {i+1}"
) -> dict[str, tuple[list[str], dict]]:
    # Dictionary to store the generated recommendations, keyed by chart name

    renderer = AltairRenderer()
    chart_specs = {}
    for i, model in enumerate(draco.complete_spec(spec, num)):
        chart_name = labeler(i)
        spec = drc.answer_set_to_dict(model.answer_set)
        chart_specs[chart_name] = drc.dict_to_facts(spec), spec

        print(chart_name)
        print(f"COST: {model.cost}")
        chart = renderer.render(spec=spec, data=df)
        # Adjust column-faceted chart size
        if (
            isinstance(chart, alt.FacetChart)
            and chart.facet.column is not alt.Undefined
        ):
            chart = chart.configure_view(continuousWidth=130, continuousHeight=130)
        display(chart)

    return chart_specs
def rec_from_generated_spec(
    marks: list[str],
    fields: list[str],
    encoding_channels: list[str],
    draco: drc.Draco,
    input_spec_base: list[str],
    data: pd.DataFrame,
    num: int = 1,
) -> dict[str, dict]:
    input_specs = [
        (
            (mark, field, enc_ch),
            input_spec_base
            + [
                f"attribute((mark,type),m0,{mark}).",
                "entity(encoding,m0,e0).",
                f"attribute((encoding,field),e0,{field}).",
                f"attribute((encoding,channel),e0,{enc_ch}).",
                # filter out designs with less than 3 encodings
                ":- {entity(encoding,_,_)} < 2.",
                # exclude multi-layer designs
                # ":- {entity(mark,_,_)} != 1.",
            ],
        )
        for mark in marks
        for field in fields
        for enc_ch in encoding_channels
    ]
    recs = {}
    for cfg, spec in input_specs:
        labeler = lambda i: f"CHART {i + 1} ({' | '.join(cfg)})"
        recs = recs | recommend_charts(spec=spec, draco=draco, df=data, num=num, labeler=labeler)

    return recs
def start_draco(fields,datasetname='birdstrikes'):
    # Loading data to be explored
    d = drc.Draco()
    if datasetname=='seattle':
        df: pd.DataFrame = vega_data.seattle_weather()
    # data = {
    #     'Column1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    #     'Column2': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    #     'Column3': [11.1, 22.2, 33.3, 44.4, 55.5, 66.6, 77.7, 88.8, 99.9, 100.0],
    #     'Column4': [True, False, True, False, True, False, True, False, True, False],
    #     'Column5': ['Apple', 'Banana', 'Cherry', 'Date', 'Fig', 'Grape', 'Kiwi', 'Lemon', 'Mango', 'Orange']
    # }
    #
    else:
        df: pd.DataFrame = vega_data.birdstrikes()
        df.columns = [col.replace('__', '_').lower() for col in df.columns]
        df.columns = [col.replace('$', 'a') for col in df.columns]
    data_schema = drc.schema_from_dataframe(df)
    pprint(data_schema)
    data_schema_facts = drc.dict_to_facts(data_schema)
    print(data_schema_facts)
    input_spec_base = data_schema_facts
    recommendations = rec_from_generated_spec(
    marks=["point", "bar", "line", "rect"],
    fields=fields,
    encoding_channels=["color", "shape", "size"],
    draco=d,
    input_spec_base=input_spec_base,
    data=df
    )
    return recommendations

# Joining the data `schema` dict with the view specification dict

if __name__ == '__main__':
    fields_birkstrikes = ["number_rows", "flight_date"]
    fields_seattle=["weather", "temp_min"]
    recommendations=start_draco( fields=fields_birkstrikes)
    # Loop through the dictionary and print recommendations
    for chart_key, _ in recommendations.items():
        (_,chart)=(recommendations[chart_key])

        print(f"Recommendation for {chart_key}:")
        print(f"**Draco Specification of {chart_key}**")
        localpprint(chart)
        print("\n")



