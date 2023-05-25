import plotly.express as px
import plotly.io as pio
import pandas as pd
import json
import base64
import datetime
import io
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, MATCH, Patch, ALL, dash_table
from dash.dependencies import Input, Output, State


import Animal_Class as ac
import manure_storage as ms
import  Environmental_impact as env
#from dash_extensions.snippets import send_data_frame
#dash


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

animal_classes = ["Milchkuh", "Mutterkuh", "Aufzuchtrind", "Mastkalb", "Mutterkuhkalb", "RiendviehMast", "Zuchtstier", "Mastschwein", "Zuchtschweineplatz", "Legehenne", "Junghenne", "Mastpoulet"]
cattle = ["Milchkuh", "Mutterkuh", "Aufzuchtrind", "Mastkalb", "Mutterkuhkalb", "RiendviehMast", "Zuchtstier"]
pigs = ["Mastschwein", "Zuchtschweineplatz"]
poultry = ["Legehenne", "Junghenne", "Mastpoulet"]
dataframe_columns = ["name", "num-animals", "days-outside", "hours-outside", "manure-type"]


list_data_calc = ["manure_l_tot", "manure_s_tot", "manure_straw_tot", "manure_tot", "methane_pot_tot", "effective_methane_pre_storage",
                  "ch4_pre_storage_volume", "ch4_pre_storage", "c_tot_init", "c_tot_pre_storage", "n_tot",
                  "p_tot", "k_tot", "n_tot_pre_storage", "p_tot_pre_storage", "k_tot_pre_storage", "n_lost_pre_storage",
                  "ch4_released_pre_storage", "nh3_released_pre_storage", "n2o_released_pre_storage",
                  "diesel_transport_tot", "co2_transport_tot"]



def create_data_frame_calc():
    df_table = pd.DataFrame(0, index=list_data_calc, columns=["name", 'Value'])
    df_table["name"] = list_data_calc
    return df_table

data_frame_calc = create_data_frame_calc()

def calculate_data_farm(dict_farm, dict_calc):
    methane_pot_tot_farm = 0
    n_tot_farm = 0
    p_tot_farm = 0
    k_tot_farm = 0
    manure_l_tot_farm = 0
    manure_s_tot_farm = 0
    manure_straw_tot_farm = 0
    ch4_pre_storage_farm = 0
    ch4_pre_storage_volume_farm = 0
    n_lost_pre_storage_farm = 0
    manure_tot_farm = 0
    c_tot_init_farm = 0
    n_tot_pre_storage_farm = 0
    nh3_pre_storage_farm, n2o_pre_storage_farm = 0, 0
    diesel_transport_farm = 0
    co2_transport_farm = 0

    df_calc = pd.DataFrame.from_records(dict_calc)
    df_farm = pd.DataFrame.from_records(dict_farm)
    for animal_class in animal_classes:
        animal = create_animal_class(animal_class, df_farm)
        methane_pot_tot_farm += animal.methane_pot_tot / 1000  # m3 CH4
        n_tot_farm += animal.n_tot
        p_tot_farm += animal.p_tot
        k_tot_farm += animal.k_tot
        manure_l_tot_farm += animal.manure_l_tot / 1000  # in m3
        manure_s_tot_farm += animal.manure_s_tot / 1000  # in m3
        manure_straw_tot_farm += animal.manure_straw_tot / 1000  # in m3

    df_calc.at["n_tot", "value"] += n_tot_farm
    df_calc.at["p_tot", "value"] += p_tot_farm
    df_calc.at["k_tot", "value"] += k_tot_farm
    df_calc.at["methane_pot_tot", "value"] += methane_pot_tot_farm
    manure_tot_farm = manure_s_tot_farm + manure_l_tot_farm
    df_calc.at["manure_tot", "value"] += manure_tot_farm

    #calculate pre storage

    pre_storage_farm = df_farm["pre-storage", "additional-data"]
    c_tot_init_farm = ms.c_total(methane_pot_tot_farm)
    ch4_pre_storage_farm = ms.ch4_release_untreated(c_tot_init_farm, pre_storage_farm)  # ch4 released during pre storage in kg ch4
    ch4_pre_storage_volume_farm = ms.ch4_mass_to_volume(ch4_pre_storage_farm)  # ch4 released in m3 ch4
    effective_methane_pre_storage_farm = methane_pot_tot_farm - ch4_pre_storage_volume_farm  # ch4 potential after pre storage in m3
    c_tot_pre_storage_farm = c_tot_init_farm - ms.c_total(ch4_pre_storage_volume_farm)

    df_calc.at["effective_methane_pre_storage", "value"] += effective_methane_pre_storage_farm
    df_calc.at["ch4_pre_storage_volume", "value"] += ch4_pre_storage_volume_farm
    df_calc.at["ch4_pre_storage", "value"] += ch4_pre_storage_farm

    nh3_pre_storage_farm = ms.nh3_storage_untreated(n_tot_farm, pre_storage_farm)  # NH3 emitted in kg N
    n2o_pre_storage_farm = ms.n2o_storage_untreated(n_tot_farm - nh3_pre_storage_farm, pre_storage_farm)  # N2O emitted in kg N
    n_lost_pre_storage_farm = n2o_pre_storage_farm + nh3_pre_storage_farm  # N lost in kg N
    nh3_pre_storage_farm = ms.n_to_nh3(nh3_pre_storage_farm)  # NH3 in kg NH3
    n2o_pre_storage_farm = ms.n_to_n2o(n2o_pre_storage_farm)  # N2O in kg N2O
    n_tot_pre_storage_farm = n_tot_farm - n_lost_pre_storage_farm

    df_calc.at["c_tot_init", "value"] += c_tot_init_farm
    df_calc.at["c_tot_pre_storage", "value"] += c_tot_pre_storage_farm
    df_calc.at["n_lost_pre_storage", "value"] += n_lost_pre_storage_farm
    df_calc.at["n_tot_pre_storage", "value"] += n_tot_pre_storage_farm
    df_calc.at["p_tot_pre_storage", "value"] += p_tot_farm
    df_calc.at["k_tot_pre_storage", "value"] += k_tot_farm

    df_calc.at["nh3_released_pre_storage", "value"] += nh3_pre_storage_farm  # kg NH3
    df_calc.at["n2o_released_pre_storage", "value"] += n2o_pre_storage_farm  # kg N2O
    df_calc.at["ch4_released_pre_storage", "value"] += ch4_pre_storage_farm  # kg CH4

    distance = df_farm["distance", "additional-data"]
    diesel_transport_farm = env.fuel_consumption_transport(manure_tot_farm, distance)
    co2_transport_farm = env.env_impact_diesel(diesel_transport_farm)

    df_calc.at["diesel_transport_tot", "value"] += diesel_transport_farm
    df_calc.at["co2_transport_tot", "value"] += co2_transport_farm

    dict_calc_new = df_calc.to_dict("records")
    return dict_calc_new


def create_animal_class(animal_class, df_farm):
    row = df_farm.query("name == animal_class")
    num_animals = row["num-animals"].values[0]
    days_outside = row["days-outside"].values[0]
    hours_outside = row["hours_outside"].values[0]
    manure_type = row["manure-type"].values[0]
    animal = getattr(ac, animal_class)(num_animals, days_outside, hours_outside, manure_type)
    animal.manure_prod()
    animal.manure_prod_tot()
    animal.methane_pot()
    animal.nutrients()
    return animal


def create_data_frame(animal):
    df_table = pd.DataFrame(columns=dataframe_columns)
    df_table["name"] = animal
    df_table["manure-type"] = 1
    df_table = df_table.fillna(0)
    return df_table


def create_accordion(n):
    accordion = []
    for i in range(n):
        new_item = create_accordion_item(i)
        accordion += new_item
    return accordion


def create_accordion_item(i):
    data_table = []
    data_table += generate_data_table(i, "cattle", cattle)
    data_table += generate_data_table(i, "pigs", pigs)
    data_table += generate_data_table(i, "poultry", poultry)

    item = [dbc.AccordionItem(
        children=[dbc.Container([
            dbc.Row([
                dbc.Col([
                    "How many days is the manure stored before processing?",
                    dcc.Input(id={"type": 'days-stored-initial', "index": i+1}, type='number', value=0)
                ]),
                dbc.Col([
                    html.Button(f"Store data for farm {i+1}", id={"type": "store-data-button", "index": i+1}, n_clicks=0)
                ])
            ]),
            dcc.Download(id={"type": "download-data-farm", "index": i+1}),
            dbc.Row([
                dbc.Col([
                    "How far is the farm from the processing location in km?",
                    dcc.Input(id={"type": 'distance', "index": i + 1}, type='number', value=0)
                ]),
                ]),
            dbc.Row(
                data_table
            )
        ])],
        title=f"Farm-{i+1}",
        item_id=f"farm-accordion-item-{i+1}",
        id={"type": "farm-accordion-item", "index": i+1}
    )]
    return item


def generate_data_table(k, animals, animals_list):
    data = create_data_frame(animals_list)
    data_table = [html.Br(), html.H3(f"{animals}"), dash_table.DataTable(

        data=data.to_dict("records"),
        columns=[
            {"name": f"Type of {animals}", "id": "name", "editable": False},
            {"name": f"Number of animals", "id": "num-animals", "type": "numeric"},
            {"name": "Avg days outside stable per year", "id": "days-outside", "type": "numeric"},
            {"name": "Avg hours outside per day", "id": "hours-outside", "type": "numeric"},
            {"name": "Type of manure collected", "id": "manure-type", "presentation": "dropdown"},
        ],
        editable=True,
        dropdown={
            "manure-type": {
                "options": [
                    {"label": "Only solid", "value": "2"},
                    {"label": "Only liquid", "value": "0"},
                    {"label": "Mixed", "value": "1"}
                ]
            }
        },
        id={"type": f"data-table-{animals}", "index": k+1}
    )]
    return data_table


def datatable_to_dataframe(dt_1, dt_2, dt_3, pre_storage, post_storage, distance):
    df_1 = pd.DataFrame.from_records(dt_1)
    df_2 = pd.DataFrame.from_records(dt_2)
    df_3 = pd.DataFrame.from_records(dt_3)
    df = pd.concat([df_1, df_2, df_3])
    df = add_manure_storage_cell(df, pre_storage, post_storage, distance)
    return df


def add_manure_storage_cell(df, pre_storage, post_storage, distance):
    df["additional-data"] = 0
    df.loc["pre-storage"] = 0
    df.at["pre-storage", "additional-data"] = pre_storage
    df.at["pre-storage", "name"] = "pre_storage"
    df.loc["post-storage"] = 0
    df.at["post-storage", "additional-data"] = post_storage
    df.at["post-storage", "name"] = "post_storage"
    df.loc["distance"] = 0
    df.at["distance", "additional-data"] = distance
    df.at["distance", "name"] = "distance"
    return df


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            id={"tpye": "farm-data-upload", "index": filename},
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])




app.layout = html.Div([
    html.H3([
        "Enter the number of farms.",
        dcc.Input(id='num-farms', type='number', value=1),
        html.Button('Submit', id='submit-button', n_clicks=0),
        html.Button('Calculate LCA', id='calculate-button', n_clicks=0),
        html.Br(),
        "How many days is the manure or digestate fertilizer stored before field application?",
        html.Br(),
        dcc.Input(id='fertilizer-storage-duration', type='number', value=100),
    ]),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    #dcc.Tabs(id='farm-tabs'),  #create the tabs for the different farms
    dbc.Accordion(id="farm-accordion"),
    #html.Div(id='output-data-upload', style={'display': 'none'})
    html.Div(id='output-data-upload'),
    html.Div(id="output-farm-data-calc")
])




@app.callback(
    Output("farm-accordion", "children"),
    Input('submit-button', 'n_clicks'),
    State('num-farms', 'value'),
)
def generate_accordion(n_clicks, num_farms):
    if n_clicks:
        accordion_items = create_accordion(num_farms)
        return accordion_items


# Download data into csv file
@app.callback(
    Output({"type": "download-data-farm", "index": MATCH}, "data"),
    Input({"type": f'store-data-button', "index": MATCH}, 'n_clicks'),
    State({"type": 'data-table-cattle', "index": MATCH}, 'data'),
    State({"type": 'data-table-pigs', "index": MATCH}, 'data'),
    State({"type": 'data-table-poultry', "index": MATCH}, 'data'),
    State({"type": 'days-stored-initial', "index": MATCH}, "value"),
    State({"type": 'days-stored-initial', "index": MATCH}, "value"),
    State('fertilizer-storage-duration', "value"),
    State({"type": "farm-accordion-item", "index": MATCH}, "title"),
    prevent_initial_call=True
)
def download_data_table_csv(n_clicks, dt_cattle, dt_pigs, dt_poultry, pre_storage, distance, post_storage, title):
    if n_clicks:
        df = datatable_to_dataframe(dt_cattle, dt_pigs, dt_poultry, pre_storage, post_storage, distance)
        return dcc.send_data_frame(df.to_csv, f"{title}.csv")


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


#add farm number into the dict and initiate more keys, one for each farm
"""@app.callback(
    Output("output-farm-data-calc", "children"),
    Input("calculate-button", "n_clicks")
)
def generate_empty_store_calc(n_clicks):
    if n_clicks:
        df = create_data_frame_calc()
        data_table = [html.Br(),
                      html.H3(f"data store"),
                      dash_table.DataTable(
                          data=df.to_dict("records"),
                          columns=[{"name": i, "id": i} for i in df.columns],
                          editable=False,
                          id="data-table-store"
        )]
        return data_table
"""

@app.callback(
    Output("output-farm-data-calc", "children"),
    State({"type": "farm-data-upload", "index": ALL}, "data"),
    Input("calculate-button", "n_clicks"),
    prevent_initial_call=True,
)
def calculate_data(farm_data, n_clicks):
    if n_clicks:
        #df_add = data_frame_calc
        #dict_add = calculate_data_farm(farm, data_frame_calc)
        farm_data_display = []
        #df_add.add(pd.DataFrame.from_records(dict_add))
        for farm in farm_data:
            farm_data_display += [pd.DataFrame.from_records(farm)]

        data_table = []
        for farm_data in farm_data_display:
            data_table += [html.Br(),
                          html.Pre(f"{farm_data}"),
                          html.H3(f"data store"),
                          dash_table.DataTable(
                              data=farm_data.to_dict("records"),
                              columns=[{"name": i, "id": i} for i in farm_data.columns],
                              editable=False,
                              id="data-table-store"
             )]
        return data_table






























"""@app.callback(
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
    return data"""


#generate the tabs for each farm with the additional animal sub tabs
"""@app.callback(
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
"""






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
"""def add_input_fields(animal_class):
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
"""
"""
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

"""
#update the data dicts for each farm tab to store input data
"""
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
"""




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
"""@app.callback(
    Output('data-div', 'children'),
    Input({"type": 'farm-input-store', "index": ALL}, 'data')
    )
def display_data(data):
    return json.dumps(data, indent=2)

"""



app.run_server(debug=True)

