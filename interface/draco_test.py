import draco as drc
import pandas as pd
from vega_datasets import data as vega_data
import altair as alt
from IPython.display import display, Markdown
import json
import numpy as np
from draco.renderer import AltairRenderer
# alt.renderers.enable("png")
from itertools import permutations
import pdb

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
    spec: list[str], draco: drc.Draco, df: pd.DataFrame, num: int = 20, labeler=lambda i: f"CHART {i+1}"
) -> dict[str, tuple[list[str], dict]]:
    # Dictionary to store the generated recommendations, keyed by chart name

    renderer = AltairRenderer()
    chart_specs = {}
    chart_vega_specs = {}
    for i, model in enumerate(draco.complete_spec(spec, num)):
        # print(i)
        chart_name = labeler(i)
        spec = drc.answer_set_to_dict(model.answer_set)
        chart_specs[chart_name] = drc.dict_to_facts(spec), spec
        # print(chart_name)
        # print(f"COST: {model.cost}")
        chart = renderer.render(spec=spec, data=df)
        if not ( isinstance(chart, alt.FacetChart) or isinstance(chart, alt.LayerChart)):
            chart_vega_specs[chart_name] = {'chart': chart.to_json(), 'cost': model.cost[0]}

        # # Adjust column-faceted chart size

        # print(chart.to_json())
        # display(chart)

    return chart_vega_specs

def rec_from_generated_spec(
    marks: list[str],
    fields: list[str],
    encoding_channels: list[str],
    draco: drc.Draco,
    input_spec_base: list[str],
    data: pd.DataFrame,
    num: int = 10, config=None
) -> dict[str, dict]:
    if config is None:
        num_encodings = len(fields)
        # make different arrangement of fields elements
        perms_fields = list(permutations(fields))
        input_specs = []
        id=0
        for fields in perms_fields:

            force_attributes = []

            for index, item in enumerate(fields):
                connect_root = f'entity(encoding,m0,e{index}).'
                force_attributes.append(connect_root)
                specify_field = f'attribute((encoding,field),e{index},{item}).'
                force_attributes.append(specify_field)
            id=id+1
            spec =(
                    (str(id) ,'only-mark'),
                    input_spec_base
                    # +
                    # [
                    #     f"attribute((mark,type),m0,{mark})."
                    # ]
                    +

                    force_attributes +

                    [
                        # ":- {attribute((encoding,field),_,_)} =" + str(num_encodings) + ".",
                        ":- {attribute((encoding,field),_,_)} < 1."
                    ]
                )
            input_specs.append(spec)


        recs = {}
        for cfg, spec in input_specs:
            labeler = lambda i: f"CHART {i + 1} ({' | '.join(cfg)})"
            try:
                new_recs = recommend_charts(spec=spec, draco=draco, df=data, num=num, labeler=labeler)
                recs.update(new_recs)
            except:
                print('Altair went wrong')
                pass

    else:
        input_specs = validate_chart(config, input_spec_base)

        recs = {}
        for cfg, spec in input_specs:
            labeler = lambda i: f"CHART {i + 1} ({' | '.join(cfg)})"
            recs= recs | recommend_charts(spec=spec, draco=draco, df=data, num=num, labeler=labeler)

    # sort recs by cost
    recs = dict(sorted(recs.items(), key=lambda item: item[1]['cost']))
    # remove the cost from the dictionary
    for key in recs:
        recs[key] = recs[key]['chart']

    return recs


def validate_chart(config, input_spec_base):
    if not config:  # If config is empty, return an empty list
        return []

    con = config[0]  # Use the first configuration in the list
    mark = con['mark']
    encoding = con['encoding']
    i=0
    input_spec = []
    # Extract fields, aggregates, and channels from the encoding dictionary
    for channel, attr_info in encoding.items():
        field = attr_info.get('field')
        aggregate = attr_info.get('aggregate')

        # Ensure channel is not None

        if  i==0:
            # Generate the base input specification
            input_spec = [
                (mark, field, channel) if field is not None else (mark, channel),
                input_spec_base + [
                    f"attribute((mark,type),m0,{mark}).",
                    f"entity(encoding,m0,e{i}).",
                    f"attribute((encoding,channel),e{i},{channel}).",
                ]
            ]

            # Append additional attribute for field if it's not None
            if field is not None:
                input_spec[1].append(f"attribute((encoding,field),e{i},{field}).")

            # Append additional attribute for aggregate if it's not None
            if aggregate is not None:
                input_spec[1].append(f"attribute((encoding,aggregate),e{i},{aggregate}).")
            i=i+1

        elif  i>0:

            input_spec[1].append(f"entity(encoding,m0,e{i}).")
            input_spec[1].append(f"attribute((encoding,channel),e{i},{channel}).")
            if field is not None:
                input_spec[1].append(f"attribute((encoding,field),e{i},{field}).")
            if aggregate is not None:
                input_spec[1].append(f"attribute((encoding,aggregate),e{i},{aggregate}).")
            i=i+1


    # Append filtering rules
    input_spec[1].extend([
                    ":- {entity(mark,_,_)} != 1.",
                    # ":- {attribute((encoding,field),_,_)} <" + str(num_encodings) + "."]
                    ":- {attribute((encoding,field),_,_)} < 1."
                ])

    return [input_spec]




def start_draco(fields,datasetname='birdstrikes',config=None):
    # Loading data to be explored
    d = drc.Draco()
    if datasetname == 'movies':
        df: pd.DataFrame = vega_data.movies()
        # df = df.drop(columns = 'Worldwide_Gross')
    elif datasetname=='seattle':
        df: pd.DataFrame = vega_data.seattle_weather()
    elif datasetname=='performance':
        df = pd.read_csv('distribution_map.csv')
    else:
        df: pd.DataFrame = vega_data.birdstrikes()
        df = df.sample(n=500, random_state=1)
    # print(df.head(10))
    df.columns = [col.replace('__', '_').lower() for col in df.columns]
    df.columns = [col.replace('$', 'a') for col in df.columns]
    data_schema = drc.schema_from_dataframe(df)
    # pprint(data_schema)
    data_schema_facts = drc.dict_to_facts(data_schema)
    # print(df.columns)
    # pprint(data_schema_facts)

    input_spec_base = data_schema_facts + [
        "entity(view,root,v0).",
        "entity(mark,v0,m0).",
    ]
    # initial_recommendations = recommend_charts(spec=input_spec_base, draco=d, df=df)

    recommendations = rec_from_generated_spec(
    marks=['bar', 'point', 'circle', 'line', 'tick'],
    fields=fields,
    # encoding_channels=["x", "y", "color"],
    # encoding_channels=["color", "shape", "size"],
    encoding_channels=["x", "y", "color", "shape", "size"],
    draco=d,
    input_spec_base=input_spec_base,
    data=df,
    config=config
    )
    return recommendations

def get_draco_recommendations(attributes,datasetname='birdstrikes',config=None):

    ret = [f.replace('__', '_').lower() for f in attributes]
    field_names_renamed = [f.replace('$', 'a') for f in ret]
    #remove none fields
    field_names_final = [f for f in field_names_renamed if f != 'none']
    #
    # try:
    #     recommendations=start_draco(fields=field_names_renamed,datasetname=datasetname,config=config)
    #     if len(recommendations) == 0:
    #         # depending on size of fields , we tak 1 less than length of fields
    #            if len(field_names_renamed) > 1:
    #                  print('Draco recommendations are empty, retrying with one field')
    #                  recommendations = start_draco(fields=np.random.shuffle(field_names_renamed)[:1], datasetname=datasetname, config=config)
    #
    # except :
    #
    #     print('Draco recommendations failed, retrying with 2 field')
    #     recommendations=start_draco(fields=field_names_renamed[:1],datasetname=datasetname,config=config)
    # #recommendations in a dictionary if more that 6 items return first 6

    recommendations=start_draco(fields=field_names_final,datasetname=datasetname,config=config)
    if len(recommendations) == 0:
            print('Draco recommendations are empty, retrying with one less field')
            recommendations = start_draco(fields= [f for f in field_names_renamed[:2] if f != 'none'], datasetname=datasetname, config=config)

    if len(recommendations) > 6:
        return dict(list(recommendations.items())[:6])
    print(' Dracorecommendations:', len(recommendations))
    return recommendations

# Joining the data `schema` dict with the view specification dict
if __name__ == '__main__':
    fields_birdstrikes = ['airport_name', 'flight_date', 'origin_state']
    fields_seattle=["weather", "temp_min", "date"]
    fields_movies = ["major_genre", "us_gross", "source"]
    fields_performance = ['Fields', 'Probability']
    # recommendations=start_draco(fields=fields_movies, datasetname='movies')
    recommendations=start_draco(fields=fields_birdstrikes, datasetname='birdstrikes')
    #recommendations=start_draco(fields=fields_performance, datasetname='performance')

    # recommendations=start_draco(fields=fields_seattle, datasetname='seattle')
    # print(len(recommendations))
    # Loop through the dictionary and print recommendations
    # for chart_key, _ in recommendations.items():
    #     # (_,chart)=(recommendations[chart_key])
    #     chart = recommendations[chart_key]
    #     print(f"Recommendation for {chart_key}:")
    #     print(f"**Draco Specification of {chart_key}**")
    #     # localpprint(chart)
    #     print(chart)
    #     print("\n")
    print('Total recommendations:', len(recommendations))


