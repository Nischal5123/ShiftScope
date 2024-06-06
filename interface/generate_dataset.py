from vega_datasets import data as vega_data
import pandas as pd
import json 

if __name__ == "__main__":
    df: pd.DataFrame = vega_data.birdstrikes()
    df = df.sample(n=500, random_state=1)
    df.columns = [col.replace('__', '_') for col in df.columns]
    df.columns = [col.replace('$', 'a') for col in df.columns]
    
    data_dict = {
            "charts": [],  # empty Charts field
            "attributes": list([f] for f in df.columns),
            "data": df.to_dict(orient='records')
        }
    
        # Save to JSON file
    with open('staticdata/birdstrikes_temp.json', 'w') as f:
        json.dump(data_dict, f, indent=4)
