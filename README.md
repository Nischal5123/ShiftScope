
# SIGMOD 2024


## Visualization interface 

The front-end and back-end code of the interface is under the _interface/_ folder. 

* _client/_: Front-end code for the visualization interface
* _components/_: Third party components used in the front-end
* _server/_: Back-end NodeJS server for the front-end
* _staticdata/_: Example datasets served by the NodeJS server
* _modelserver.py_: Back-end Flask server 



<img src="assets/UI.png" width="100%">

To build the app:
* Install python packages: pip install -r requirements.txt (suggest using virtual environment https://docs.python.org/3/tutorial/venv.html)
* Install js packages: npm install
* Build for production: npm run build:prod

To run the app:
* Start the recommendation engine (Flask server): python modelserver.py
* Start the back-end NodeJS server: npm run start:prod
* Visit: http://localhost:8000/index.html

Alternatively, for development (live code update):
* Start recommendation engine: python modelserver.py
* Start development: npm start

The app supports a JSON format input, consisting a list of charts specified in Vega-Lite and a data array for the charts. See _staticdata/_ for examples. The input data can be loaded via an url or a file upload, in the right format. Note that no format checking is performed. By default, the _cars.json_ is loaded when the app starts.


## 📄 Citation

If you find this work useful, please cite:

```bibtex
@inproceedings{10.1145/3626246.3654753,
author = {Saha, Sanad and Aryal, Nischal and Battle, Leilani and Termehchy, Arash},
title = {ShiftScope: Adapting Visualization Recommendations to Users' Dynamic Data Focus},
year = {2024},
isbn = {9798400704222},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3626246.3654753},
doi = {10.1145/3626246.3654753},
abstract = {Visualization Recommendation Systems help users discover important insights during data exploration. These systems should understand users' exploration behaviors and goals to suggest relevant visualizations. However, users' mental models constantly evolve as they learn more about their data or as their personal or organizational goals change, leading to shifts in their data focus. Current systems do not adapt to these changes; therefore, they may inevitably suggest irrelevant visualizations over time. Thus, we introduce ShiftScope, an interactive system that recommends personalized visualizations while adapting to users' conceptualization of data. ShiftScope utilizes a dual-agent reinforcement learning framework, where one agent adapts to evolution in data focus and collaborates with the other agent to recommend the best visualizations to satisfy users' current and future exploration needs.},
booktitle = {Companion of the 2024 International Conference on Management of Data},
pages = {536–539},
numpages = {4},
keywords = {exploratory data analysis, personalized visualization recommendation, reinforcement learning, user modeling},
location = {Santiago AA, Chile},
series = {SIGMOD/PODS '24}
}
