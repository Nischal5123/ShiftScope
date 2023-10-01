from draco import schema_from_dataframe, dict_to_facts
import pandas as pd
import warnings
import importlib.resources as pkg_resources
import draco.asp.examples as examples
from draco import Draco, answer_set_to_dict
from pprint import pprint
from draco.schema import schema_from_dataframe
from vega_datasets import data as vega_data

warnings.filterwarnings("ignore")
def start_draco(current_chart):
    df: pd.DataFrame = vega_data.cars()
    schema: dict = schema_from_dataframe(df)
    processed_current_chart = schema | current_chart
    return processed_current_chart

# Joining the data `schema` dict with the view specification dict






