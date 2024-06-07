import draco as drc
import pandas as pd
from vega_datasets import data as vega_data
import altair as alt
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


# def md(markdown: str):
#     display(Markdown(markdown))


# def pprint(obj):
#     md(f"```json\n{json.dumps(obj, indent=2, cls=NpEncoder)}\n```")

def parse_spec(spec):
    ########### data type ############
    data_types = {
        "aircraft_airline_operator": "nominal",
        "aircraft_make_model": "nominal",
        "airport_name": "nominal",
        "cost_other": "quantitative",
        "cost_repair": "quantitative",
        "cost_total_a": "quantitative",
        "effect_amount_of_damage": "nominal",
        "flight_date": "temporal",
        "origin_state": "nominal",
        "speed_ias_in_knots": "quantitative",
        "when_phase_of_flight": "nominal",
        "when_time_of_day": "nominal",
        "wildlife_size": "nominal",
        "wildlife_species": "nominal",
    }
    ###################################
    for channel, encoding in spec["encoding"].items():
        # if "color" in channel:
        field_name = encoding.get("field", None)
        if field_name == None:
            continue
        # print(field_name)
        encoding["type"] = data_types[field_name]
    return json.dumps(spec)

def localpprint(obj):
        print(json.dumps(obj, indent=2, cls=NpEncoder))

def recommend_charts(
    spec: list[str], draco: drc.Draco, df: pd.DataFrame, num: int = 5, labeler=lambda i: f"CHART {i+1}"
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
            chart = parse_spec(json.loads(chart.to_json()))
            chart_vega_specs[chart_name] = {'chart': chart, 'cost': model.cost[0]}

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
    num: int = 50, config=None
) -> dict[str, dict]:
    attribute_mapping = {
        "airport_name": 0,
        "aircraft_make_model": 1,
        "effect_amount_of_damage": 2,
        "flight_date": 3,
        "aircraft_airline_operator": 4,
        "origin_state": 5,
        "when_phase_of_flight": 6,
        "wildlife_size": 7,
        "wildlife_species": 8,
        "when_time_of_day": 9,
        "cost_other": 10,
        "cost_repair": 11,
        "cost_total_a": 12,
        "speed_ias_in_knots": 13
    }
    if config is None:
        num_encodings = len(fields)
        # make different arrangement of fields elements
        perms_fields = list(permutations(fields))
        input_specs = []
        id=0
        for fields in perms_fields: # this should not matter but doesnt hurt to precompute

            force_attributes = []

            for index, item in enumerate(fields):
                connect_root = f'entity(encoding,m0,e{attribute_mapping[item]}).'
                force_attributes.append(connect_root)
                specify_field = f'attribute((encoding,field),e{attribute_mapping[item]},{item}).'
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
                        ":- {attribute((encoding,aggregate),_,_)} < 1."
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
    attribute_mapping = {
        "airport_name": 0,
        "aircraft_make_model": 1,
        "effect_amount_of_damage": 2,
        "flight_date": 3,
        "aircraft_airline_operator": 4,
        "origin_state": 5,
        "when_phase_of_flight": 6,
        "wildlife_size": 7,
        "wildlife_species": 8,
        "when_time_of_day": 9,
        "cost_other": 10,
        "cost_repair": 11,
        "cost_total_a": 12,
        "speed_ias_in_knots": 13
    }

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
            if field is not None:
                input_spec = [
                    (mark, field, channel),
                    input_spec_base + [
                        f"attribute((mark,type),m0,{mark}).",
                        f"entity(encoding,m0,e{attribute_mapping[field]}).",
                        f"attribute((encoding,channel),e{attribute_mapping[field]},{channel}).",
                    ]
                ]

                input_spec[1].append(f"attribute((encoding,field),e{attribute_mapping[field]},{field}).")
                # Append additional attribute for aggregate if it's not None
                if aggregate is not None:
                    input_spec[1].append(f"attribute((encoding,aggregate),e{attribute_mapping[field]},{aggregate}).")
                i = i + 1
            else:

                input_spec = [
                    (mark, channel),
                    input_spec_base + [
                        f"attribute((mark,type),m0,{mark}).",
                        f"entity(encoding,m0,e{i}).",
                        f"attribute((encoding,channel),e{i},{channel}).",
                    ]
                ]


        elif  i>0:

            if field is not None:
                index_value = attribute_mapping[field]
            else:
                index_value = i

            input_spec[1].append(f"entity(encoding,m0,e{index_value}).")
            input_spec[1].append(f"attribute((encoding,channel),e{index_value},{channel}).")
            if field is not None:
                input_spec[1].append(f"attribute((encoding,field),e{index_value},{field}).")
            if aggregate is not None:
                input_spec[1].append(f"attribute((encoding,aggregate),e{index_value},{aggregate}).")
            i=i+1


    # Append filtering rules
    input_spec[1].extend([
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
    encoding_channels=["x", "y", "color", "shape", "size"],
    draco=d,
    input_spec_base=input_spec_base,
    data=df,
    config=config
    )
    return recommendations


def load_precomputed_recommendations(file_path):
    try:
        with open(file_path, 'r') as f:
            recommendations_dict = json.load(f)
        return recommendations_dict
    except FileNotFoundError:
        return {}


def load_dataset(file_path):
    with open(file_path, 'r') as f:
        dataset_dict = json.load(f)
    return dataset_dict


def get_draco_recommendations(attributes, datasetname='birdstrikes', config=None, data_schema_file_path='staticdata/birdstrikes_dataset_schema.json'):
    ret = [f.replace('__', '_').lower() for f in attributes]
    field_names_renamed = [f.replace('$', 'a') for f in ret]
    field_names_final = [f for f in field_names_renamed if f != 'none']

    if config is None:
        # Attempt to load precomputed recommendations
        recommendations_dict = load_precomputed_recommendations('precomputed_recommendations.json')
        key = '+'.join(np.sort(field_names_final))
        reco = recommendations_dict.get(key, {})
        dataset_schema = load_dataset(data_schema_file_path)
        #for all reco's add the dataset schema
        for key in reco:
            reco[key]['datasets'] = dataset_schema
            reco[key]=json.dumps(reco[key])
        return reco

    else:
        # Always start Draco if config is provided
        recommendations = start_draco(fields=field_names_final, datasetname=datasetname, config=config)
        if len(recommendations) == 0:
            print('Draco recommendations are empty, retrying with one less field')
            recommendations = start_draco(fields=[f for f in field_names_final[:2] if f != 'none'],
                                          datasetname=datasetname, config=config)

        if len(recommendations) > 2:
            return dict(list(recommendations.items())[:1])

        return recommendations




def test_get_draco_recommendations(attributes, datasetname='birdstrikes', config=None):
    ret = [f.replace('__', '_').lower() for f in attributes]
    field_names_renamed = [f.replace('$', 'a') for f in ret]
    field_names_final = [f for f in field_names_renamed if f != 'none']
        # If not found in precomputed, generate recommendations
    recommendations = start_draco(fields=field_names_final, datasetname=datasetname, config=config)
    if len(recommendations) == 0:
        print('Draco recommendations are empty, retrying with one less field')
        recommendations = start_draco(fields=[f for f in field_names_final[:2] if f != 'none'], datasetname=datasetname,
                                      config=config)

    if len(recommendations) > 1:
        recos= dict(list(recommendations.items())[:1])
        reco = remove_datapart(recos)
        return dict(list(reco.items())[:1])


def remove_datapart(recommendations):
    dataset_part = None
    chart_recom = {}
    for chart_key, chart_json in recommendations.items():
        chart = json.loads(chart_json)
        if 'datasets' in chart:
            dataset_part = chart.pop('datasets')  # Remove and store the 'datasets' part
        chart_recom[chart_key] = chart  # Add the modified chart back to the result dictionary

    # # Save the dataset part to a file
    # if dataset_part:
    #     with open('birdstrikes_dataset_schema.json', 'w') as f:
    #         json.dump(dataset_part, f)

    return chart_recom


def remove_datapart(recommendations):
    dataset_part = None
    chart_recom = {}
    for chart_key, chart_json in recommendations.items():
        chart = json.loads(chart_json)
        if 'datasets' in chart:
            dataset_part = chart.pop('datasets')  # Remove and store the 'datasets' part
        chart_recom[chart_key] = chart  # Add the modified chart back to the result dictionary

    # # Save the dataset part to a file
    # if dataset_part:
    #     with open('birdstrikes_dataset_schema.json', 'w') as f:
    #         json.dump(dataset_part, f)

    return chart_recom

def remove_irrelevant_reccomendations(interested_attributes, recommendations, max_constrained=True):
    fieldnames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
                  'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
                  'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
                  'speed_ias_in_knots']
    chart_recom = []
    chart_all = []
    matched_field = []
    for chart_key, _ in recommendations.items():
        chart = recommendations[chart_key]
        chart_all.append(chart)
        encodings = chart.get('encoding', {})
        match = 0
        mark= chart.get('mark', {})
        mark=mark.get('type',{})

        if  max_constrained:
            for field in fieldnames:
                if field in str(encodings):
                    match += 1
                    matched_field.append(field)
            if match == len(interested_attributes):
                chart_recom.append(chart)
        else:
            for f in interested_attributes:
                if f in str(encodings):
                    match += 1
                else:
                    match -= 1
            if match > 0:
                chart_recom.append(chart)

    if len(chart_recom) == 0:
        print("##############################################")
        print('No relevant recommendations found, returning all')

        return chart_all[:1], mark, matched_field # Need to return something to avoid empty response
    else:
        return chart_recom, mark, matched_field

if __name__ == '__main__':
    all_fields = np.load('../staticdata/birdstrikes_all_states.npy', allow_pickle=True)

    recommendations_dict = {}
    bar_count=0

    for fields_birdstrikes in all_fields:

            attributes = [field for field in fields_birdstrikes if field.lower() != 'none']
            recommendations = test_get_draco_recommendations(attributes=attributes, datasetname='birdstrikes')
            print(f"Recommendations for {fields_birdstrikes}: {recommendations}")
            recommendations, mark, matched_field= remove_irrelevant_reccomendations(attributes, recommendations)
            if mark=='bar':
                bar_count+=1

            print(f"Filtered Recommendations for {fields_birdstrikes}: {matched_field}, mark: {mark}")
            print(' ************ Bar count:', bar_count)
            key = '+'.join(np.sort(fields_birdstrikes))
            recommendations_dict[key] = recommendations

    with open('bar_precomputed_recommendations.json', 'w') as f:
        json.dump(recommendations_dict, f, indent=4)

