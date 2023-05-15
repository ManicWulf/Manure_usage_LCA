import plotly.express as px
import plotly.io as pio
import pandas as pd
import json
import dash
from dash import Dash, dcc, html, Input, Output, State, MATCH, Patch, ALL, dash_table
from dash.dependencies import Input, Output, State

#dash


app = dash.Dash(__name__, suppress_callback_exceptions=True)

animal_classes = ["Milchkuh", "Mutterkuh", "Aufzuchtrind", "Mastkalb", "Mutterkuhkalb", "RiendviehMast", "Zuchtstier", "Mastschwein", "Zuchtschweineplatz", "Legehenne", "Junghenne", "Mastpoulet"]
cattle = ["Milchkuh", "Mutterkuh", "Aufzuchtrind", "Mastkalb", "Mutterkuhkalb", "RiendviehMast", "Zuchtstier"]
pigs = ["Mastschwein", "Zuchtschweineplatz"]
poultry = ["Legehenne", "Junghenne", "Mastpoulet"]


input - button value
def create_accordion(n):
    accordion = []
    for i in range(n):
        new_item = create_accordion_item(i)
        accordion += new_item
    return accordion


def create_accordion_item(i):
    item = html.Div(item_content, id=f"{i}")
    return item




app.layout = html.Div([
    html.H3([
        "Enter the number of farms.",
        dcc.Input(id='num-farms', type='number', value=1),
        html.Button('Submit', id='submit-button', n_clicks=0),
        html.Br(),
        "How many days is the manure or digestate fertilizer stored before field application?",
        html.Br(),
        dcc.Input(id='fertilizer-storage-duration', type='number', value=100),
    ]),
    dcc.Tabs(id='farm-tabs'),  #create the tabs for the different farms
    dcc.Store(id="farm-data-store"),  #create a dict to store data
    html.Div(id="data-div"),     #element to display and check the dict
"""    dash_table.DataTable(id="farm-data-table",
                         columns=[{
                             "name": "data/farm"
                         }],
                         data=[{
                             "animal-type", "num_animals", "days_outside", "num_hours", "manure-type"
                         }],
                         )"""
])


#add farm number into the dict and initiate more keys, one for each farm
@app.callback(
 Output('farm-data-store', 'data'),
 Input('submit-button', 'n_clicks'),
 State('num-farms', 'value'),
 State('farm-data-store', 'data')
)
def update_farm_data_store(n_clicks, num_farms, data):
    if not data:
        data = {}
    if n_clicks:
        data["num_farms"] = num_farms
        for i in range(num_farms):
            data[f"farm{i+1}"] = i+1
    return data


#generate the tabs for each farm with the additional animal sub tabs
@app.callback(
    Output('farm-tabs', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('num-farms', 'value')],
)
def generate_farm_tabs(n_clicks, num_farms):

    if n_clicks:
        return [dcc.Tab(label=f'Farm {i+1}', children=[
            html.Div([
                f"Farm {i+1} Name: ",
                dcc.Input(id={"type": 'farm-name', "index": i+1}, type='text', value=i+1),
                f"Farm {i+1} Distance from processing site: ",
                dcc.Input(id={"type": 'farm-distance', "index": i+1}, type='number', value=0),
                f"Farm {i + 1} manure storage duration before processing: ",
                dcc.Input(id={"type": 'farm-manure-storage-time', "index": i + 1}, type='number', value=0),
                html.Br(),
                html.H3(f"What kinds of animals does farm {i+1} have? Select all that apply"),
                #create new tabs for Cattle, Pigs and Poultry within the farm tabs
                dcc.Tabs(id={"type": "animal-tab", "index": i+1},
                         value="cattle",
                         children=[
                             dcc.Tab(label="Cattle", value="cattle"),
                             dcc.Tab(label="Pigs", value="pigs"),
                             dcc.Tab(label="Poultry", value="poultry"),
                         ]),
                html.Div(id={"type": "animal-tabs-content", "index": i+1})
            ]),
            html.Br(),
            html.Div(id={"type": 'additional-fields', "index": i+1}),
            dcc.Store(id={"type": 'additional-fields-store', "index": i+1}, data={}),       #generate a dict to store if fields have been added already
            dcc.Store(id={"type": 'farm-input-store', "index": i + 1}, data={}),  #generate dict to store the input data for each farm tab
            html.Div(id={"type": 'farm_data_output', "index": i + 1}),

        ]) for i in range(num_farms)]







"""@app.callback(
    Output("farm-data-store", "data"),
    Input({'type': 'farm-name', 'index': ALL}, 'value'),
    Input({'type': 'farm-name', 'index': ALL}, 'index'),
    Input({'type': 'farm-distance', 'index': ALL}, 'value'),
    Input("num-farms", "value"),
    prevent_initial_call=True
)
def update_farm_data(farm_name, farm_index, farm_distance, num_farms):
    patch_data = Patch()
    for i in range(num_farms):
        if farm_index == i+1:
            patch_data[f"farm{i+1}"] = i+1
            patch_data[f"farm{i+1}"]["name"] = farm_name
            patch_data[f"farm{i+1}"]["distance"] = farm_distance
    return patch_data
"""


#generate new input fields in the animal tabs for data input, update the dict to check if the fields have already been added, as well as construct the baseline for the farm_data dict
def add_input_fields(animal_class):
    additional_fields = []
    new_ = [

    ]
    additional_fields += [(html.Br())]
    additional_fields += [(html.Label(f"Number of {animal_class}:"))]
    additional_fields += [(dcc.Input(id=f'num-{animal_class}', type='number', value=0))]

    additional_fields += [(html.Br())]
    additional_fields += [(html.Label(f"Number of days outside the stable per year:"))]
    additional_fields += [(dcc.Input(id=f'days-outside-{animal_class}', type='number', value=0))]

    additional_fields += [(html.Br())]
    additional_fields += [(html.Label(f"Hours per day outside on average on the days outside:"))]
    additional_fields += [(dcc.Input(id=f'num-hours-{animal_class}', type='number', value=0))]

    additional_fields += [(html.Br())]
    additional_fields += [(html.Label(f"What type of manure is collected?:"))]
    additional_fields += [(dcc.Dropdown(options=[
        {"label": "Only solid", "value": "2"},
        {"label": "Only liquid", "value": "0"},
        {"label": "Mixed", "value": "1"}
    ],
        id=f'manure-type-{animal_class}', value=1))]
    return additional_fields


def initiate_data_store(animal_class):
    data = {"farm": {}}
    data["farm"][f"{animal_class}"] = {}

    data["farm"][f"{animal_class}"]["num_animals"] = 0

    data["farm"][f"{animal_class}"]["num_days"] = 0

    data["farm"][f"{animal_class}"]["num_hours"] = 0

    data["farm"][f"{animal_class}"]["manure_type"] = 0

    return data


@app.callback(
    Output({"type": 'animal-tabs-content', "index": MATCH}, 'children'),
    Output({'type': 'additional-fields-store', 'index': MATCH}, 'data'),
    Output({'type': 'farm-input-store', 'index': MATCH}, 'data'),
    Input({"type": 'animal-tab', "index": MATCH}, 'value'),
    State({'type': 'additional-fields-store', 'index': MATCH}, 'data'),
    State({'type': 'farm-input-store', 'index': MATCH}, 'data'),
)
def generate_additional_fields(animal, additional_fields_check, data):
    additional_fields_check_internal = {}   #dict to check if fields have been added already

    additional_fields = []  #initiate list of the fields to be added
    data = data
    if animal == "pigs":
        if additional_fields_check.get('pigs_fields_added'):
            # additional fields have already been added, do not add them again
            return dash.no_update
        else:
            additional_fields_check_internal["pigs_fields_added"] = True    #update dict to make sure fields have been added

            for pig_class in pigs:

                additional_fields += add_input_fields(pig_class)

                data.update(initiate_data_store(pig_class))



    elif animal == "cattle":
        if additional_fields_check.get('cattle_fields_added'):
            # additional fields have already been added, do not add them again
            return dash.no_update
        else:
            additional_fields_check_internal["cattle_fields_added"] = True

            for cattle_class in cattle:

                additional_fields += add_input_fields(cattle_class)

                data.update(initiate_data_store(cattle_class))

    elif animal == "poultry":
        if additional_fields_check.get('poultry_fields_added'):
            # additional fields have already been added, do not add them again
            return dash.no_update
        else:
            additional_fields_check_internal["poultry_fields_added"] = True

            for poultry_class in poultry:

                additional_fields += add_input_fields(poultry_class)

                data.update(initiate_data_store(poultry_class))

    return [additional_fields, additional_fields_check_internal, data]


#update the data dicts for each farm tab to store input data
@app.callback(
    Output({'type': 'farm-input-store', 'index': MATCH}, 'data', allow_duplicate=True),
    Input({"type": 'animal-tab', "index": MATCH}, 'value'),
    State({"type": 'animal-tabs-content', "index": MATCH}, 'value'),
    State({'type': 'farm-input-store', 'index': MATCH}, 'data'),
    [State(f"num-{animal_class}", "value") for animal_class in animal_classes],
    [State(f"days-outside-{animal_class}", "value") for animal_class in animal_classes],
    [State(f"num-hours-{animal_class}", "value") for animal_class in animal_classes],
    [State(f"manure-type-{animal_class}", "value") for animal_class in animal_classes],
    prevent_initial_call=True
    )
def update_farm_animal_input(animal, animal_tab, data, num_animals, days_outside, num_hours, manure_type):
    ctx = dash.callback_context
    if not ctx.triggered:
        return data
    patch_data = Patch()
    triggered_id = ctx.triggered_id
    for animal_class in animal_classes:

        if triggered_id == f"num-{animal_class}":
            patch_data["farm"][f"{animal_class}"]["num_animals"] = num_animals

        elif triggered_id == f"days-outside-{animal_class}":
            patch_data["farm"][f"{animal_class}"]["num_days"] = days_outside

        elif triggered_id == f"num-hours-{animal_class}":
            patch_data["farm"][f"{animal_class}"]["num_hours"] = num_hours

        elif triggered_id == f"manure-type-{animal_class}":
            patch_data["farm"][f"{animal_class}"]["manure_type"] = manure_type

    return patch_data





"""@app.callback(
    Output({"type": 'animal-tabs-content', "index": ALL}, 'children'),
    Output("farm-data-store", "data", allow_duplicate=True),
    Input({"type": 'animal-tab', "index": ALL}, 'value'),
    State({"type": 'farm-data-store', "index": ALL}, 'data'),
    Input("farm-tabs", "value"),
    prevent_initial_call=True
)
def generate_additional_fields(animal, data, farm_index):
    additional_fields = []
    patch_data = Patch()

    if animal == "pigs":

        if not data[f"{farm_index}"]["pigs"] and not data[f"{farm_index}"]["pigs"]["fields_added"]:
            patch_data[f"{farm_index}"]["pigs"] = True
            patch_data[f"{farm_index}"]["pigs"]["fields_added"] = True

            for pig_class in pigs:
                patch_data[f"{farm_index}"]["pigs"][f"{pig_class}"] = True

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Number of {pig_class}:"))
                additional_fields.append(dcc.Input(id='num-{pig_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["pigs"][f"{pig_class}"]["num_animals"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Number of days outside the stable per year:"))
                additional_fields.append(dcc.Input(id=f'days-outside-{pig_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["pigs"][f"{pig_class}"]["num_days"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Hours per day outside on average on the days outside:"))
                additional_fields.append(dcc.Input(id=f'num-hours-{pig_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["pigs"][f"{pig_class}"]["num_hours"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"What type of manure is collected?:"))
                additional_fields.append(dcc.Dropdown(options=[
                    {"label": "Only solid", "value": "2"},
                    {"label": "Only liquid", "value": "0"},
                    {"label": "Mixed", "value": "1"}
                ],
                    id=f'manure-type-{pig_class}', value=1))
                patch_data[f"{farm_index}"]["pigs"][f"{pig_class}"]["manure_type"] = 1
    elif animal == "cattle":

        if not data[f"{farm_index}"]["cattle"] and not data[f"{farm_index}"]["cattle"]["fields_added"]:
            patch_data[f"{farm_index}"]["cattle"] = True
            patch_data[f"{farm_index}"]["cattle"]["fields_added"] = True

            for cattle_class in cattle:
                patch_data[f"{farm_index}"]["cattle"][f"{cattle_class}"] = True

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Number of {cattle_class}:"))
                additional_fields.append(dcc.Input(id=f'num-{cattle_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["cattle"][f"{cattle_class}"]["num_animals"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Number of days outside the stable per year:"))
                additional_fields.append(dcc.Input(id=f'days-outside-{cattle_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["cattle"][f"{cattle_class}"]["num_days"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Hours per day outside on average on the days outside:"))
                additional_fields.append(dcc.Input(id=f'num-hours-{cattle_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["cattle"][f"{cattle_class}"]["num_hours"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"What type of manure is collected?:"))
                additional_fields.append(dcc.Dropdown(options=[
                    {"label": "Only solid", "value": "2"},
                    {"label": "Only liquid", "value": "0"},
                    {"label": "Mixed", "value": "1"}
                ],
                    id=f'manure-type-{cattle_class}', value=1))
                patch_data[f"{farm_index}"]["cattle"][f"{cattle_class}"]["manure_type"] = 1
    elif animal == "poultry":

        if not data[f"{farm_index}"]["poultry"] and not data[f"{farm_index}"]["poultry"]["fields_added"]:
            patch_data[f"farm{farm_index}"]["poultry"] = True
            patch_data[f"farm{farm_index}"]["poultry"]["fields_added"] = True

            for poultry_class in poultry:
                patch_data[f"{farm_index}"]["poultry"][f"{poultry_class}"] = True

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Number of {poultry_class}:"))
                additional_fields.append(dcc.Input(id=f'num-{poultry_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["poultry"][f"{poultry_class}"]["num_animals"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Number of days outside the stable per year:"))
                additional_fields.append(dcc.Input(id=f'days-outside-{poultry_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["poultry"][f"{poultry_class}"]["num_days"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"Hours per day outside on average on the days outside:"))
                additional_fields.append(dcc.Input(id=f'num-hours-{poultry_class}', type='number', value=0))
                patch_data[f"{farm_index}"]["poultry"][f"{poultry_class}"]["num_hours"] = 0

                additional_fields.append(html.Br())
                additional_fields.append(html.Label(f"What type of manure is collected?:"))
                additional_fields.append(dcc.Dropdown(options=[
                    {"label": "Only solid", "value": "2"},
                    {"label": "Only liquid", "value": "0"},
                    {"label": "Mixed", "value": "1"}
                ],
                    id=f'manure-type-{poultry_class}', value=1))
                patch_data[f"{farm_index}"]["poultry"][f"{poultry_class}"]["manure_type"] = 1
    return additional_fields, patch_data
"""
"""@app.callback(
    Output("farm-data-store", "data", allow_duplicate=True),
    [Input({"type": f'num-{animal_class}', "index": ALL}, 'value') for animal_class in animal_classes],
    [Input({"type": f'days-outside-{animal_class}', "index": ALL}, 'value') for animal_class in animal_classes],
    [Input({"type": f'num-hours-{animal_class}', "index": ALL}, 'value') for animal_class in animal_classes],
    [Input({"type": f'manure-type-{animal_class}', "index": ALL}, 'value') for animal_class in animal_classes],
    State('farm-data-store', 'data'),
    Input("animal-tab", "index"),
    prevent_initial_call=True
)
def update_farm_data(num_animal, days_outside, num_hours, manure_type, data, farm_tab_index):
    ctx = dash.callback_context
    if not ctx.triggered:
        return data
    else:
        triggered_id = ctx.triggered_id
        for animal in animal_classes:
            if triggered_id == f'num-{animal}':
                patched_data = Patch()
                patched_data[f"farm{farm_tab_index}"][animal]["num"] = num_animal
                return patched_data
            elif triggered_id == f'days-outside-{animal}':
                patched_data = Patch()
                patched_data[f"farm{farm_tab_index}"][animal]["days"] = days_outside
                return patched_data
            elif triggered_id == f'num-hours-{animal}':
                patched_data = Patch()
                patched_data[f"farm{farm_tab_index}"][animal]["hours"] = num_hours
                return patched_data
            elif triggered_id == f'manure-type-{animal}':
                patched_data = Patch()
                patched_data[f"farm{farm_tab_index}"][animal]["manure-type"] = manure_type
                return patched_data
"""


#display the farm_input dict to check if it's working
@app.callback(
    Output('data-div', 'children'),
    Input({"type": 'farm-input-store', "index": ALL}, 'data')
    )
def display_data(data):
    return json.dumps(data, indent=2)





app.run_server(debug=True)

