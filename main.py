from prettytable import PrettyTable
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import plotly.io as pio
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import glob
import os
import numpy as np

import Anaerobic_Digestion as AD
import Animal_Class as AC
import CHP
import Environmental_impact as env
import manure_storage as ms
import biogas_upgrading as bg
import steam_treatment as st

# define function for user input


def get_user_input(class_name):
    try:
        num_animals_f = int(input(f"How many {class_name} do you have?") or 0)
        if num_animals_f != 0:
            days_outside_f = int(input("How many days of the year are they outside of the stable on average?"))
            hours_outside_f = float(input("On the days they are outside the stable, how many hours on average are they out?"))
            manure_type_f = int(input("What kind of manure do you collect? 0: only liquid. 1: liquid and solid. 2: only solid."))
        else:
            days_outside_f = 0
            hours_outside_f = 0
            manure_type_f = 0
    except ValueError:
        print("Invalid input. Please enter a valid integer value.")
        return get_user_input(class_name)
    return num_animals_f, days_outside_f, hours_outside_f, manure_type_f


# define variables
manure_l_tot = 0
manure_s_tot = 0
manure_straw_tot = 0
manure_tot = 0
methane_pot_tot = 0
methane_pot_solid = 0
methane_pot_liquid = 0
methane_pot_straw = 0
effective_methane_pre_storage = 0
ch4_pre_storage_volume = 0
ch4_pre_storage = 0
c_tot_init = 0
c_tot_pre_storage = 0
n_tot = 0
p_tot = 0
k_tot = 0
n_tot_pre_storage = 0
p_tot_pre_storage = 0
k_tot_pre_storage = 0
n_lost_pre_storage = 0
ch4_released_pre_storage = 0
nh3_released_pre_storage = 0
n2o_released_pre_storage = 0
diesel_transport_tot = 0
co2_transport_tot = 0

effective_methane_pre_storage_solid = 0
ch4_pre_storage_volume_solid = 0
ch4_pre_storage_solid = 0
c_tot_init_solid = 0
c_tot_pre_storage_solid = 0

effective_methane_pre_storage_liquid = 0
ch4_pre_storage_volume_liquid = 0
ch4_pre_storage_liquid = 0
c_tot_init_liquid = 0
c_tot_pre_storage_liquid = 0

effective_methane_pre_storage_straw = 0
ch4_pre_storage_volume_straw = 0
ch4_pre_storage_straw = 0
c_tot_init_straw = 0
c_tot_pre_storage_straw = 0





#define list of animal classes used.

animal_classes = ["Milchkuh", "Mutterkuh", "Aufzuchtrind", "Mastkalb", "Mutterkuhkalb", "RiendviehMast", "Zuchtstier", "Mastschwein", "Zuchtschweineplatz", "Legehenne", "Junghenne", "Mastpoulet"]


##########################################
#dash app
##########################################



"""app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='num-farms', type='number', placeholder='Enter number of farms'),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='farm-inputs')
])

@app.callback(
    Output('farm-inputs', 'children'),
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('num-farms', 'value')]
)
def generate_farm_inputs(n_clicks, num_farms):
    if n_clicks:
        return [html.Div([
            html.H3(f'Farm {i+1}'),
            dcc.Input(id=f'farm-name-{i+1}', type='text', placeholder=f'Enter farm {i+1} name'),
            dcc.Input(id=f'distance-{i+1}', type='number', placeholder=f'Enter distance for farm {i+1}'),
            html.H4('Animal counts'),
            html.Div([
                dcc.Input(id=f'{animal_class.lower()}-{i+1}', type='number', placeholder=f'Enter number of {animal_class}', value=0)
                for animal_class in animal_classes
            ])
        ]) for i in range(num_farms)]
"""

###################################################
# read the csv files generated with visualization and do the calculations based on that


path = os.path.join(os.getcwd(), 'farm_files')
all_files = glob.glob(os.path.join(path, "*.csv"))

print(path)

farms = {}
post_storage = None
for filename in all_files:
    farm_name = os.path.basename(filename).split('.')[0]
    df = pd.read_csv(filename)
    distance_from_power_plant = df.loc[df['name'] == 'distance', 'additional-data'].values[0]
    pre_storage = df.loc[df['name'] == 'pre_storage', 'additional-data'].values[0]
    post_storage = df.loc[df['name'] == 'post_storage', 'additional-data'].values[0]

    farm_dict = {}
    for index, row in df.iterrows():
        animal_class = row['name']
        if animal_class in animal_classes:
            num_animals = row['num-animals']
            days_outside = row['days-outside']
            hours_outside = row['hours-outside']
            manure_type = row['manure-type']

            farm_dict[animal_class] = {"num_animals": num_animals,
                                       "days_outside": days_outside,
                                       "hours_outside": hours_outside,
                                       "manure_type": manure_type}

    farms[farm_name] = {"distance_from_power_plant": distance_from_power_plant,
                        "pre_storage": pre_storage,
                        "animals": farm_dict}


print(farms)
"""num_farms = int(input("How many farms do you want to calculate for? "))


# Get user input for each farm and store in a nested dictionary
farms = {}
for i in range(num_farms):
    farm_name = input(f"Enter name for farm {i + 1}: ")
    distance_from_power_plant = int(input(f"Enter distance from power plant for farm {farm_name} in km: "))

    farm_dict = {}
    for animal_class in animal_classes:
        num_animals, days_outside, hours_outside, manure_type = get_user_input(animal_class)
        farm_dict[animal_class] = {"num_animals": num_animals,
                                   "days_outside": days_outside,
                                   "hours_outside": hours_outside,
                                   "manure_type": manure_type}

    farms[farm_name] = {"distance_from_power_plant": distance_from_power_plant,
                        "animals": farm_dict}"""








# Calculate methane potential, n_tot, p_tot, k_tot, manure and pre storage for each farm
for farm_name, farm_data in farms.items():
    methane_pot_tot_farm = 0
    methane_pot_solid_farm = 0
    methane_pot_liquid_farm = 0
    methane_pot_straw_farm = 0
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


    # Calculate values for each animal class for the current farm
    for animal_class, animal_data in farm_data["animals"].items():
        num_animals = animal_data["num_animals"]
        days_outside = animal_data["days_outside"]
        hours_outside = animal_data["hours_outside"]
        manure_type = animal_data["manure_type"]

        animal = getattr(AC, animal_class)(num_animals, days_outside, hours_outside, manure_type)
        animal.manure_prod()
        animal.manure_prod_tot()
        animal.methane_pot()
        animal.nutrients()

        n_tot_farm += animal.n_tot
        p_tot_farm += animal.p_tot
        k_tot_farm += animal.k_tot
        manure_l_tot_farm += animal.manure_l_tot / 1000         #in m3
        manure_s_tot_farm += animal.manure_s_tot / 1000         #in m3
        manure_straw_tot_farm += animal.manure_straw_tot / 1000 #in m3
        methane_pot_tot_farm += animal.methane_pot_tot / 1000 + ms.methane_potential_straw(animal.manure_straw_tot / 1000)  # m3 CH4
        methane_pot_solid_farm += animal.methane_pot_s / 1000  # m3 CH4
        methane_pot_liquid_farm += animal.methane_pot_l / 1000  # m3 CH4
        methane_pot_straw_farm += ms.methane_potential_straw(animal.manure_straw_tot / 1000)


    n_tot += n_tot_farm
    p_tot += p_tot_farm
    k_tot += k_tot_farm
    methane_pot_tot += methane_pot_tot_farm
    methane_pot_solid += methane_pot_solid_farm
    methane_pot_liquid += methane_pot_liquid_farm
    methane_pot_straw += methane_pot_straw_farm
    manure_l_tot += manure_l_tot_farm
    manure_s_tot += manure_s_tot_farm
    manure_straw_tot += manure_straw_tot_farm
    manure_tot_farm = manure_l_tot_farm + manure_straw_tot_farm + manure_s_tot_farm
    manure_tot += (manure_l_tot_farm + manure_straw_tot_farm + manure_s_tot_farm)
    # Calculate values for pre storage

    pre_storage_farm = farm_data["pre_storage"]
    c_tot_init_farm = ms.c_total(methane_pot_tot_farm)
    ch4_pre_storage_farm = ms.ch4_release_untreated(c_tot_init_farm, pre_storage_farm)  #ch4 released during pre storage in kg ch4
    ch4_pre_storage_volume_farm = ms.ch4_mass_to_volume(ch4_pre_storage_farm)  # ch4 released in m3 ch4
    effective_methane_pre_storage_farm = methane_pot_tot_farm - ch4_pre_storage_volume_farm  # ch4 potential after pre storage in m3
    c_tot_pre_storage_farm = c_tot_init_farm - ms.c_total(ch4_pre_storage_volume_farm)

    effective_methane_pre_storage += effective_methane_pre_storage_farm
    ch4_pre_storage_volume += ch4_pre_storage_volume_farm
    ch4_pre_storage += ch4_pre_storage_farm

    #n_lost_pre_storage_farm = ms.N_reduction_untreated(n_tot_farm, pre_storage_farm)
    #nh3_pre_storage_farm, n2o_pre_storage_farm = ms.NH3_vs_N2O_untreated(n_lost_pre_storage_farm)
    nh3_pre_storage_farm = ms.nh3_storage_untreated(n_tot_farm, pre_storage_farm)            #NH3 emitted in kg N
    n2o_pre_storage_farm = ms.n2o_storage_untreated(n_tot_farm - nh3_pre_storage_farm, pre_storage_farm)            #N2O emitted in kg N
    n_lost_pre_storage_farm = n2o_pre_storage_farm + nh3_pre_storage_farm   #N lost in kg N
    nh3_pre_storage_farm = ms.n_to_nh3(nh3_pre_storage_farm)                #NH3 in kg NH3
    n2o_pre_storage_farm = ms.n_to_n2o(n2o_pre_storage_farm)                #N2O in kg N2O
    n_tot_pre_storage_farm = n_tot_farm - n_lost_pre_storage_farm

    c_tot_init += c_tot_init_farm
    c_tot_pre_storage += c_tot_pre_storage_farm
    n_lost_pre_storage += n_lost_pre_storage_farm
    n_tot_pre_storage += n_tot_pre_storage_farm
    p_tot_pre_storage += p_tot_farm
    k_tot_pre_storage += k_tot_farm

    nh3_released_pre_storage += nh3_pre_storage_farm        #kg NH3
    n2o_released_pre_storage += n2o_pre_storage_farm        #kg N2O
    ch4_released_pre_storage += ch4_pre_storage_farm        #kg CH4


    distance = farm_data["distance_from_power_plant"]
    diesel_transport_farm = env.fuel_consumption_transport(manure_tot_farm, distance)
    co2_transport_farm = env.env_impact_diesel(diesel_transport_farm)
    diesel_transport_tot += diesel_transport_farm
    co2_transport_tot += co2_transport_farm


    #########################################
    # Steam pretreatment, same emissions for pre storage, using methane potential after pre storage for calculation of increased yield.
    ########################################
    c_tot_init_farm_solid = ms.c_total(methane_pot_solid_farm)
    c_tot_init_farm_liquid = ms.c_total(methane_pot_liquid_farm)
    c_tot_init_farm_straw = ms.c_total(methane_pot_straw_farm)

    ch4_pre_storage_farm_solid = ms.ch4_release_untreated(c_tot_init_farm_solid, pre_storage_farm)  #ch4 released during pre storage in kg ch4
    ch4_pre_storage_volume_farm_solid = ms.ch4_mass_to_volume(ch4_pre_storage_farm_solid)  # ch4 released in m3 ch4

    ch4_pre_storage_farm_liquid = ms.ch4_release_untreated(c_tot_init_farm_liquid, pre_storage_farm)  # ch4 released during pre storage in kg ch4
    ch4_pre_storage_volume_farm_liquid = ms.ch4_mass_to_volume(ch4_pre_storage_farm_liquid)  # ch4 released in m3 ch4

    ch4_pre_storage_farm_straw = ms.ch4_release_untreated(c_tot_init_farm_straw, pre_storage_farm)  # ch4 released during pre storage in kg ch4
    ch4_pre_storage_volume_farm_straw = ms.ch4_mass_to_volume(ch4_pre_storage_farm_straw)  # ch4 released in m3 ch4

    effective_methane_pre_storage_farm_solid = methane_pot_solid_farm - ch4_pre_storage_volume_farm_solid  # ch4 potential after pre storage in m3
    c_tot_pre_storage_farm_solid = c_tot_init_farm_solid - ms.c_total(ch4_pre_storage_volume_farm_solid)

    effective_methane_pre_storage_farm_liquid = methane_pot_liquid_farm - ch4_pre_storage_volume_farm_liquid  # ch4 potential after pre storage in m3
    c_tot_pre_storage_farm_liquid = c_tot_init_farm_liquid - ms.c_total(ch4_pre_storage_volume_farm_solid)

    effective_methane_pre_storage_farm_straw = methane_pot_straw_farm - ch4_pre_storage_volume_farm_straw  # ch4 potential after pre storage in m3
    c_tot_pre_storage_farm_straw = c_tot_init_farm_straw - ms.c_total(ch4_pre_storage_volume_farm_straw)        #C tot after pre storage emissions

    effective_methane_pre_storage_solid += effective_methane_pre_storage_farm_solid     #ch4 potential after pre storage in m3
    ch4_pre_storage_volume_solid += ch4_pre_storage_volume_farm_solid                   # ch4 released during pre storage in m3
    ch4_pre_storage_solid += ch4_pre_storage_farm_solid
    c_tot_init_solid += c_tot_init_farm_solid
    c_tot_pre_storage_solid += c_tot_pre_storage_farm_solid

    effective_methane_pre_storage_liquid += effective_methane_pre_storage_farm_liquid
    ch4_pre_storage_volume_liquid += ch4_pre_storage_volume_farm_liquid
    ch4_pre_storage_liquid += ch4_pre_storage_farm_liquid
    c_tot_init_liquid += c_tot_init_farm_liquid
    c_tot_pre_storage_liquid += c_tot_pre_storage_farm_liquid

    effective_methane_pre_storage_straw += effective_methane_pre_storage_farm_straw
    ch4_pre_storage_volume_straw += ch4_pre_storage_volume_farm_straw
    ch4_pre_storage_straw += ch4_pre_storage_farm_straw
    c_tot_init_straw += c_tot_init_farm_straw
    c_tot_pre_storage_straw += c_tot_pre_storage_farm_straw         # c tot after pre storage emissions










#######################################################################################################################
#no treatment, just storage of manure and application on field
#######################################################################################################################

ch4_untreated = ms.ch4_release_untreated(c_tot_init, post_storage)               #how much ch4 is released during storage of manure
#n_lost_untreated = ms.N_reduction_untreated(n_tot, post_storage)            #how much N is lost during storage of manure
#nh3_untreated, n2o_untreated = ms.NH3_vs_N2O_untreated(n_lost_untreated)    #how much nh3 and n2o is released during storage
nh3_untreated = ms.nh3_storage_untreated(n_tot, post_storage)                     #nh3 released during storage in kg N
n2o_untreated = ms.n2o_storage_untreated(n_tot - nh3_untreated, post_storage)                     #n2o released during storage in kg N
n_lost_untreated = nh3_untreated + n2o_untreated                    #total N emitted during storage in kg N
nh3_untreated = ms.n_to_nh3(nh3_untreated)                          #NH3 emitted in kg NH3
n2o_untreated = ms.n_to_n2o(n2o_untreated)                          #N2O emitted in kg N2O
n_acc_untreated = ms.n_acc_manure(n_tot)                    #accessible nitrogen in manure
nh3_untreated_field = ms.nh3_field(n_acc_untreated)                    #kg N per year
n2o_untreated_field = ms.n2o_field(n_acc_untreated - nh3_untreated_field)                    #kg N per year
nh3_untreated_field = ms.n_to_nh3(nh3_untreated_field)              #kg NH3
n2o_untreated_field = ms.n_to_n2o(n2o_untreated_field)              #kg N2O
nh3_tot_untreated = nh3_untreated_field + nh3_untreated                     #kg per year
n2o_tot_untreated = n2o_untreated_field + n2o_untreated                     #kg per year
n_fertilizer_untreated = n_acc_untreated - n_lost_untreated
p_fertilizer_untreated = p_tot
k_fertilizer_untreated = k_tot

# co2 eq make up
# data_n2o_sources_untreated = [round(co2_n2o_pre_storage, 2), 0, round(co2_n2o_post_storage, 2), round(co2_n2o_field, 2)]
# data_ch4_sources_untreated = [round(co2_methane_pre_storage, 2), round(co2_methane_loss, 2), round(co2_methane_post_storage, 2), 0]
co2_n2o_pre_storage_untreated = 0
co2_n2o_post_storage_untreated = env.co2_n2o(n2o_untreated)
co2_n2o_field_untreated = env.co2_n2o(n2o_untreated_field)

co2_methane_pre_storage_untreated = 0
co2_methane_post_storage_untreated = env.co2_methane(ch4_untreated)
co2_methane_field = 0

co2_eq_mineral_fertilizer_untreated = env.co2_mineral_nitrate(n_fertilizer_untreated) + env.co2_mineral_k(k_fertilizer_untreated) + env.co2_mineral_P(p_fertilizer_untreated)

co2_eq_untreated = env.co2_n2o(n2o_tot_untreated) + env.co2_methane(ch4_untreated)

so2_eq_nh3_untreated = env.acidification_nh3(nh3_tot_untreated)



#UBP
n_eutrophication_untreated = env.n_fertilizer_lost_post_application(n_acc_untreated - n_lost_untreated)

ubp_nh3_emission_untreated = env.ubp_nh3(nh3_tot_untreated)
ubp_co2_emission_untreated = env.ubp_co2_eq(co2_eq_untreated)
ubp_n_eutrophication_untreated = env.ubp_eutrophication_n(n_eutrophication_untreated)

# ubp_energy_non_renew_untreated = env.ubp_energy_non_renew(energy_renew_ad)

ubp_untreated = ubp_co2_emission_untreated + ubp_nh3_emission_untreated + ubp_n_eutrophication_untreated








# input potential methane production, output effective methane [m3/y] adjusted for size of AD plant

#######################################################################################################################
#Anaerobic digestion, storage of digestate and application on field
#######################################################################################################################



#methane lost during anaerobic digestion
effective_methane_AD = AD.methane_yield(effective_methane_pre_storage)             #in m3 per year
methane_loss_ad = AD.methane_loss(effective_methane_AD)                 #m3 per year
methane_loss_mass_ad = ms.ch4_volume_to_mass(methane_loss_ad)
co2_methane_loss = env.co2_methane(methane_loss_mass_ad)                        #kg CO2
co2_methane_pre_storage = env.co2_methane(ch4_pre_storage)                                      #kg CO2

c_tot_digestate_AD = c_tot_pre_storage - ms.c_total(effective_methane_AD)  #in kg C

effective_methane_post_loss_AD = effective_methane_AD - methane_loss_ad                                 #m3 per year

ch4_post_storage = ms.ch4_release_AD(c_tot_digestate_AD, post_storage)  #how much ch4 is released during the storage of the digestate [kg/year]
co2_methane_post_storage = env.co2_methane(ch4_post_storage)

ch4_released_ad = ch4_pre_storage + ch4_post_storage + methane_loss_mass_ad       #kg CH4

#n_lost_post_storage_AD = ms.N_reduction_AD(n_tot_pre_storage, post_storage)              #how much N is lost during storage [kg/year]
#nh3_post_storage_AD, n2o_post_storage_AD = ms.NH3_vs_N2O_AD(n_lost_post_storage_AD)                    #how much nh3 and n2o is released during storage [kg/year]
nh3_post_storage_AD = ms.nh3_storage_ad(n_tot_pre_storage, post_storage)  # NH3 emitted in kg N
n2o_post_storage_AD = ms.n2o_storage_ad(n_tot_pre_storage, post_storage)  # N2O emitted in kg N
n_lost_post_storage_AD = n2o_post_storage_AD + nh3_post_storage_AD  # N lost in kg N
nh3_post_storage_AD = ms.n_to_nh3(nh3_post_storage_AD)  # NH3 in kg NH3
n2o_post_storage_AD = ms.n_to_n2o(n2o_post_storage_AD)  # N2O in kg N2O
n_acc_ad = ms.n_acc_ad(n_tot_pre_storage)
nh3_field_AD = ms.nh3_field(n_acc_ad)                      #in kg N per year
n2o_field_AD = ms.n2o_field(n_acc_ad - nh3_field_AD)                      #in kg N per year
nh3_field_AD = ms.n_to_nh3(nh3_field_AD)        #in kg NH3
n2o_field_AD = ms.n_to_n2o(n2o_field_AD)        #in kg N2O
n_fertilizer_ad = n_acc_ad - n_lost_post_storage_AD
p_fertilizer_ad = p_tot
k_fertilizer_ad = k_tot

co2_n2o_pre_storage = env.co2_n2o(n2o_released_pre_storage)
co2_n2o_post_storage = env.co2_n2o(n2o_post_storage_AD)
co2_n2o_field = env.co2_n2o(n2o_field_AD)



nh3_tot_ad = nh3_field_AD + nh3_post_storage_AD + nh3_released_pre_storage
n2o_tot_ad = n2o_field_AD + n2o_post_storage_AD + n2o_released_pre_storage
biogas_AD, co2_bg_AD = AD.biogas(effective_methane_post_loss_AD)                      #in [m3]
heat_chp_AD, electricity_chp_AD = CHP.energy_produced(effective_methane_post_loss_AD)      #in [kWh]
heat_demand_AD = AD.heat_demand(manure_tot)                        #in [kWh]
electricity_demand_ad = AD.electricity_demand(biogas_AD)            #in [kWh]
heat_net_ad = heat_chp_AD - heat_demand_AD     #heat produced minus heat used for heating the digestate
electricity_net_ad = electricity_chp_AD - electricity_demand_ad

co2_eq_mineral_fertilizer_ad = env.co2_mineral_nitrate(n_fertilizer_ad) + env.co2_mineral_k(k_fertilizer_ad) + env.co2_mineral_P(p_fertilizer_ad)
co2_eq_ad = env.co2_n2o(n2o_tot_ad) + env.co2_methane(ch4_released_ad) + co2_transport_tot

so2_eq_nh3_ad = env.acidification_nh3(nh3_tot_ad)


co2_biogenic_ad = CHP.co2_release(co2_bg_AD, effective_methane_post_loss_AD)   #CO2 released after burning of the biogas in CHP, biogenic CO2

# CO2 eq. of electricity demand, assuming it is bought from the electricity net.
co2_eq_electricity_demand_ad = env.co2_swiss_el_mix(electricity_demand_ad)   # in kg CO2


# CO2 eq. per kWh of electricity sold
co2_eq_el_production_ad = co2_eq_ad / electricity_chp_AD


# CO2 emissions avoided from heating assuming oil would be used:

co2_heat_avoided_ad = env.co2_oil_kwh(heat_net_ad)

# CO2 emissions avoided from electricity sold, assuming swiss elec mix as marginal resource

co2_el_avoided_ad = env.co2_swiss_el_mix(electricity_chp_AD)
# CO2 avoided with el + heat

co2_avoided_tot_ad = co2_el_avoided_ad + co2_heat_avoided_ad



#UBP
n_eutrophication_ad = env.n_fertilizer_lost_post_application(n_acc_ad - n_lost_post_storage_AD)

ubp_nh3_emission_ad = env.ubp_nh3(nh3_tot_ad)
ubp_co2_emission_ad = env.ubp_co2_eq(co2_eq_ad)
ubp_n_eutrophication_ad = env.ubp_eutrophication_n(n_eutrophication_ad)

energy_renew_ad = (electricity_chp_AD + heat_chp_AD) * 3.6      #total energy produced in MJ oil eq.

electricity_demand_ad_joule = electricity_demand_ad * 3.6       # el. demand in MJ
ubp_energy_renew_ad = env.ubp_energy_non_renew(electricity_demand_ad_joule)     # ubp for electricity used, assuming that el is bought and therefore non renewable. Heat demand is covered by own production, so no additional ubp

ubp_ad = ubp_nh3_emission_ad + ubp_co2_emission_ad + ubp_n_eutrophication_ad + ubp_energy_renew_ad




#####################################
# Biogas upgrading with 3-stage-membrane to 98% CH4 content in biomethane
# use of CHP with offgas and 30% of raw biogas to meet heat needs of plant
#####################################

biogas_upgraded = bg.biogas_upgraded(biogas_AD)
biogas_chp_upgrading = bg.biogas_chp(biogas_AD)

offgas_biomethane_3_stage = bg.offgas_volume_3_stage(biogas_upgraded)           # offgas volume
offgas_biomethane_ch4_3_stage = bg.ch4_offgas_3_stage(biogas_upgraded)          # ch4 volume in offgas
offgas_biomethane_co2_3_stage = bg.co2_offgas_3_stage(biogas_upgraded)          # co2 volume in offgas
biomethane_volume_3_stage = bg.biomethane_volume_3_stage(biogas_upgraded)       # biomethane volume
biomethane_ch4_3_stage = bg.ch4_biomethane_3_stage(biogas_upgraded)             # ch4 in biomethane
biomethane_co2_3_stage = bg.co2_biomethane_3_stage(biogas_upgraded)             # co2 in biomethane
ch4_loss_upgrading_3_stage = bg.ch4_slippage_3_stage(biogas_upgraded)

methane_biogas_chp_upgrading = bg.ch4_biogas(biogas_chp_upgrading)                          # methane volume in the 30% raw biogas used for chp
methane_tot_chp_upgrading = methane_biogas_chp_upgrading + offgas_biomethane_ch4_3_stage    #total methane of offgas + raw biogas mixture going to chp

electricity_demand_upgrading_3_stage = bg.energy_use_3_stage(biogas_upgraded)       # in kWh
electricity_demand_upgrading_3_stage_tot = electricity_demand_upgrading_3_stage + electricity_demand_ad     #kWh

heat_chp_upgrading, electricity_chp_upgrading = CHP.energy_produced(methane_tot_chp_upgrading)      # kWh

electricity_sofc_upgrading = CHP.el_produced_sofc(biomethane_volume_3_stage * 0.98)     # electricity potential if the biomethane is used in fuel cells, biomethane at 98% methane content

heat_net_upgrading = heat_chp_upgrading - heat_demand_AD        # kWh

electricity_produced_upgrading = electricity_sofc_upgrading + electricity_chp_upgrading
electricity_net_upgrading = electricity_chp_upgrading + electricity_sofc_upgrading - electricity_demand_upgrading_3_stage_tot

# environmental impacts
ch4_released_ad_upgrading = ch4_released_ad


ch4_loss_upgrading_mass = ms.ch4_volume_to_mass(ch4_loss_upgrading_3_stage)     # m3 to kg ch4
ch4_released_upgrading_3_stage = ch4_released_ad_upgrading + ch4_loss_upgrading_mass      # in kg CH4

co2_methane_loss_upgrading = env.co2_methane(ch4_loss_upgrading_mass)       # in kg CO2 eq.



co2_methane_upgrading = env.co2_methane(ch4_released_upgrading_3_stage)

co2_eq_upgrading = env.co2_n2o(n2o_tot_ad) + co2_methane_upgrading + co2_transport_tot

co2_biogas_upgrading_chp = bg.co2_biogas(biogas_chp_upgrading)

co2_eq_electricity_chp_upgrading = env.co2_swiss_el_mix(electricity_chp_upgrading)        # in kg CO2
co2_eq_electricity_sofc_upgrading = env.co2_swiss_el_mix(electricity_sofc_upgrading)      #kg CO2


energy_renew_upgrading = (electricity_chp_upgrading + heat_chp_upgrading) * 3.6


co2_biogenic_upgrading = ms.co2_volume_to_mass(co2_biogas_upgrading_chp + offgas_biomethane_co2_3_stage)

# CO2 eq. of electricity demand, assuming it is bought from the electricity net.
co2_eq_electricity_demand_bg_upgrade_upgrading = env.co2_swiss_el_mix(electricity_demand_upgrading_3_stage)
co2_eq_electricity_demand_upgrading = env.co2_swiss_el_mix(electricity_demand_upgrading_3_stage_tot)    # kg CO2


# CO2 eq. per kWh of electricity sold
co2_eq_el_production_upgrading = co2_eq_upgrading / electricity_produced_upgrading


# CO2 emissions avoided from heating assuming oil would be used:

co2_heat_avoided_upgrading = env.co2_oil_kwh(heat_net_upgrading)

# CO2 emissions avoided from electricity sold, assuming swiss elec mix as marginal resource

co2_el_avoided_upgrading = env.co2_swiss_el_mix(electricity_produced_upgrading)
# CO2 avoided with el + heat

co2_avoided_tot_upgrading = co2_el_avoided_upgrading + co2_heat_avoided_upgrading

#UBP
n_eutrophication_upgrading = env.n_fertilizer_lost_post_application(n_acc_ad - n_lost_post_storage_AD)

ubp_nh3_emission_upgrading = env.ubp_nh3(nh3_tot_ad)
ubp_co2_emission_upgrading = env.ubp_co2_eq(co2_eq_upgrading)
ubp_n_eutrophication_upgrading = env.ubp_eutrophication_n(n_eutrophication_upgrading)


electricity_demand_upgrading_3_stage_tot_joule = electricity_demand_upgrading_3_stage_tot * 3.6     # el. demand in MJ
ubp_energy_renew_upgrading = env.ubp_energy_non_renew(electricity_demand_upgrading_3_stage_tot_joule)  # ubp for electricity used, assuming that el is bought and therefore non renewable. Heat demand is covered by own production, so no additional ubp

ubp_upgrading = ubp_nh3_emission_upgrading + ubp_co2_emission_upgrading + ubp_n_eutrophication_upgrading + ubp_energy_renew_upgrading







#########################################
# Steam pretreatment, no new emissions for pre storage, using methane potential after pre storage for calculation of increased yield.
########################################

methane_pot_straw_steam = st.methane_yield_steam(effective_methane_pre_storage_straw)     # m3
methane_pot_solid_steam = st.methane_yield_steam(effective_methane_pre_storage_solid)      # m3

heat_demand_steam = st.heat_requirement_steam(manure_s_tot + manure_straw_tot) * 1000  # [kWh]

effective_methane_pot_tot_pre_storage_steam = methane_pot_solid_steam + methane_pot_straw_steam + effective_methane_pre_storage_liquid

c_tot_pre_storage_steam = ms.c_total(effective_methane_pot_tot_pre_storage_steam)


#methane lost during anaerobic digestion
effective_methane_ad_steam = AD.methane_yield(effective_methane_pot_tot_pre_storage_steam)             #in m3 per year
methane_loss_steam = AD.methane_loss(effective_methane_ad_steam)                 #m3 per year
methane_loss_mass_steam = ms.ch4_volume_to_mass(methane_loss_steam)
co2_methane_loss_steam = env.co2_methane(methane_loss_mass_steam)                        #kg CO2
co2_methane_pre_storage_steam = env.co2_methane(ch4_pre_storage)                                      #kg CO2

c_tot_digestate_ad_steam = c_tot_pre_storage_steam - ms.c_total(effective_methane_ad_steam)  #in kg C

effective_methane_post_loss_ad_steam = effective_methane_ad_steam - methane_loss_steam                                 #m3 per year

ch4_post_storage_steam = ms.ch4_release_AD(c_tot_digestate_ad_steam, post_storage)  #how much ch4 is released during the storage of the digestate [kg/year]
co2_methane_post_storage_steam = env.co2_methane(ch4_post_storage_steam)

ch4_released_ad_steam = ch4_pre_storage + ch4_post_storage_steam + methane_loss_mass_steam       #kg CH4


nh3_post_storage_ad_steam = ms.nh3_storage_ad(n_tot_pre_storage, post_storage)  # NH3 emitted in kg N
n2o_post_storage_ad_steam = ms.n2o_storage_ad(n_tot_pre_storage, post_storage)  # N2O emitted in kg N
n_lost_post_storage_ad_steam = n2o_post_storage_ad_steam + nh3_post_storage_ad_steam  # N lost in kg N
nh3_post_storage_ad_steam = ms.n_to_nh3(nh3_post_storage_ad_steam)  # NH3 in kg NH3
n2o_post_storage_ad_steam = ms.n_to_n2o(n2o_post_storage_ad_steam)  # N2O in kg N2O
n_acc_ad_steam = ms.n_acc_ad(n_tot_pre_storage)
nh3_field_ad_steam = ms.nh3_field(n_acc_ad)                      #in kg N per year
n2o_field_ad_steam = ms.n2o_field(n_acc_ad_steam - nh3_field_ad_steam)                      #in kg N per year
nh3_field_ad_steam = ms.n_to_nh3(nh3_field_ad_steam)        #in kg NH3
n2o_field_ad_steam = ms.n_to_n2o(n2o_field_ad_steam)        #in kg N2O
n_fertilizer_ad_steam = n_acc_ad - n_lost_post_storage_ad_steam
p_fertilizer_ad_steam = p_tot
k_fertilizer_ad_steam = k_tot

co2_n2o_pre_storage_steam = env.co2_n2o(n2o_released_pre_storage)
co2_n2o_post_storage_steam = env.co2_n2o(n2o_post_storage_ad_steam)
co2_n2o_field_steam = env.co2_n2o(n2o_field_ad_steam)



nh3_tot_ad_steam = nh3_field_ad_steam + nh3_post_storage_ad_steam + nh3_released_pre_storage
n2o_tot_ad_steam = n2o_field_ad_steam + n2o_post_storage_ad_steam + n2o_released_pre_storage
biogas_ad_steam, co2_bg_ad_steam = AD.biogas(effective_methane_post_loss_ad_steam)                      #in [m3]
heat_chp_ad_steam, electricity_chp_ad_steam = CHP.energy_produced(effective_methane_post_loss_ad_steam)      #in [kWh]
heat_demand_ad_steam = AD.heat_demand(manure_tot)                        #in [kWh]
electricity_demand_ad_steam = AD.electricity_demand(biogas_ad_steam)            #in [kWh]
heat_net_ad_steam = heat_chp_ad_steam - heat_demand_ad_steam - heat_demand_steam     #heat produced minus heat used for heating the digestate and for steam explosions [kWh]
net_electricity_ad_steam = electricity_chp_ad_steam - electricity_demand_ad_steam
co2_biogenic_ad_steam = CHP.co2_release(co2_bg_ad_steam, effective_methane_post_loss_ad_steam)   #CO2 released after burning of the biogas in CHP, biogenic CO2

co2_n2o_ad_steam = env.co2_n2o(n2o_tot_ad_steam)
co2_ch4_ad_steam = env.co2_methane(ch4_released_ad_steam)

co2_eq_mineral_fertilizer_ad_steam = env.co2_mineral_nitrate(n_fertilizer_ad_steam) + env.co2_mineral_k(k_fertilizer_ad_steam) + env.co2_mineral_P(p_fertilizer_ad_steam)
co2_eq_ad_steam = co2_n2o_ad_steam + co2_ch4_ad_steam + co2_transport_tot

so2_eq_nh3_ad_steam = env.acidification_nh3(nh3_tot_ad_steam)

co2_eq_electricity_chp_steam = env.co2_swiss_el_mix(net_electricity_ad_steam)       # kg CO2



co2_biogenic_steam = CHP.co2_release(co2_bg_ad_steam, effective_methane_post_loss_ad_steam)   #CO2 released after burning of the biogas in CHP, biogenic CO2

# CO2 eq. of electricity demand, assuming it is bought from the electricity net.
co2_eq_electricity_demand_steam = env.co2_swiss_el_mix(electricity_demand_ad_steam)     #kg CO2


# CO2 eq. per kWh of electricity sold
co2_eq_el_production_steam = co2_eq_ad_steam / electricity_chp_ad_steam

# CO2 emissions avoided from heating assuming oil would be used:

co2_heat_avoided_steam = env.co2_oil_kwh(heat_net_ad_steam)

# CO2 emissions avoided from electricity sold, assuming swiss elec mix as marginal resource

co2_el_avoided_steam = env.co2_swiss_el_mix(electricity_chp_ad_steam)
# CO2 avoided with el + heat

co2_avoided_tot_steam = co2_el_avoided_steam + co2_heat_avoided_steam

#UBP
n_eutrophication_ad_steam = env.n_fertilizer_lost_post_application(n_acc_ad_steam - n_lost_post_storage_ad_steam)

ubp_nh3_emission_ad_steam = env.ubp_nh3(nh3_tot_ad_steam)
ubp_co2_emission_ad_steam = env.ubp_co2_eq(co2_eq_ad_steam)
ubp_n_eutrophication_ad_steam = env.ubp_eutrophication_n(n_eutrophication_ad_steam)

energy_renew_ad_steam = (electricity_chp_ad_steam + heat_chp_ad_steam) * 3.6      #total energy produced in MJ oil eq.
electricity_demand_ad_steam_joule = electricity_demand_ad_steam * 3.6           # el. demand in MJ
ubp_energy_renew_ad_steam = env.ubp_energy_non_renew(electricity_demand_ad_steam_joule)     # ubp for electricity used, assuming that el is bought and therefore non renewable. Heat demand is covered by own production, so no additional ubp

ubp_ad_steam = ubp_nh3_emission_ad_steam + ubp_co2_emission_ad_steam + ubp_n_eutrophication_ad_steam + ubp_energy_renew_ad_steam




#####################################
# Biogas upgrading and Steam treatment
# use of CHP with offgas and 30% of raw biogas to meet heat needs of plant
#####################################


biogas_upgraded_steam = bg.biogas_upgraded(biogas_ad_steam)
biogas_chp_upgrading_steam = bg.biogas_chp(biogas_ad_steam)
offgas_biomethane_3_stage_steam = bg.offgas_volume_3_stage(biogas_upgraded_steam)           # offgas volume
offgas_biomethane_ch4_3_stage_steam = bg.ch4_offgas_3_stage(biogas_upgraded_steam)          # ch4 volume in offgas
offgas_biomethane_co2_3_stage_steam = bg.co2_offgas_3_stage(biogas_upgraded_steam)          # co2 volume in offgas
biomethane_volume_3_stage_steam = bg.biomethane_volume_3_stage(biogas_upgraded_steam)       # biomethane volume
biomethane_ch4_3_stage_steam = bg.ch4_biomethane_3_stage(biogas_upgraded_steam)             # ch4 in biomethane
biomethane_co2_3_stage_steam = bg.co2_biomethane_3_stage(biogas_upgraded_steam)             # co2 in biomethane
ch4_loss_upgrading_3_stage_steam = bg.ch4_slippage_3_stage(biogas_upgraded_steam)

methane_biogas_chp_upgrading_steam = bg.ch4_biogas(biogas_chp_upgrading_steam)                          # methane volume in the 30% raw biogas used for chp
methane_tot_chp_upgrading_steam = methane_biogas_chp_upgrading_steam + offgas_biomethane_ch4_3_stage_steam    #total methane of offgas + raw biogas mixture going to chp

electricity_demand_upgrading_3_stage_steam = bg.energy_use_3_stage(biogas_upgraded_steam)       # in kWh
electricity_demand_upgrading_3_stage_tot_steam = electricity_demand_upgrading_3_stage_steam + electricity_demand_ad_steam     #kWh

heat_chp_upgrading_steam, electricity_chp_upgrading_steam = CHP.energy_produced(methane_tot_chp_upgrading_steam)      # kWh

electricity_sofc_upgrading_steam = CHP.el_produced_sofc(biomethane_volume_3_stage_steam * 0.98)     # electricity potential if the biomethane is used in fuel cells, biomethane at 98% methane content

heat_net_upgrading_steam = heat_chp_upgrading_steam - heat_demand_ad_steam - heat_demand_steam       # kWh
electricity_net_upgrading_steam = electricity_chp_upgrading_steam + electricity_sofc_upgrading_steam - electricity_demand_upgrading_3_stage_tot_steam

# environmental impacts

ch4_loss_upgrading_mass_steam = ms.ch4_volume_to_mass(ch4_loss_upgrading_3_stage_steam)     # m3 to kg ch4
ch4_released_upgrading_3_stage_steam = ch4_released_ad_steam + ch4_loss_upgrading_mass_steam      # in kg CH4

co2_eq_electricity_chp_upgrading_steam = env.co2_swiss_el_mix(electricity_net_upgrading_steam)      # kg CO2

co2_methane_loss_upgrading_steam = env.co2_methane(ch4_loss_upgrading_mass_steam)           # co2 eq of methane lost during the upgrading process
co2_methane_loss_ad_upgrading_steam = env.co2_methane(ch4_released_ad_steam)                # co2 eq of methane lost during the ad process after steam treatment

co2_methane_upgrading_steam = env.co2_methane(ch4_released_upgrading_3_stage_steam)

co2_eq_upgrading_steam = co2_methane_pre_storage_steam + co2_methane_post_storage_steam + env.co2_n2o(n2o_tot_ad_steam) + co2_methane_upgrading_steam + co2_transport_tot

co2_biogas_upgrading_chp_steam = bg.co2_biogas(biogas_chp_upgrading_steam)


energy_renew_upgrading_steam = (electricity_chp_upgrading_steam + heat_chp_upgrading_steam) *3.6      # MJ of total electricity + heat generated

electricity_demand_upgrading_3_stage_tot_steam_joule = electricity_demand_upgrading_3_stage_tot_steam * 3.6     # el. demand in MJ

electricity_produced_upgrading_steam = electricity_chp_upgrading_steam + electricity_sofc_upgrading_steam

co2_biogenic_upgrading_steam = ms.co2_volume_to_mass(co2_biogas_upgrading_chp_steam + offgas_biomethane_co2_3_stage_steam)

# CO2 eq. of electricity demand, assuming it is bought from the electricity net.
co2_eq_electricity_demand_ad_upgrading_steam = env.co2_swiss_el_mix(electricity_demand_ad_steam)
co2_eq_electricity_demand_bg_upgrade_upgrading_steam = env.co2_swiss_el_mix(electricity_demand_upgrading_3_stage_steam)

co2_eq_electricity_demand_upgrading_steam = env.co2_swiss_el_mix(electricity_demand_upgrading_3_stage_tot_steam)        #kg CO2


# CO2 eq. per kWh of electricity sold
co2_eq_el_production_upgrading_steam = co2_eq_upgrading_steam / electricity_produced_upgrading_steam


# CO2 emissions avoided from heating assuming oil would be used:

co2_heat_avoided_upgrading_steam = env.co2_oil_kwh(heat_net_upgrading_steam)

# CO2 emissions avoided from electricity sold, assuming swiss elec mix as marginal resource

co2_el_avoided_upgrading_steam = env.co2_swiss_el_mix(electricity_produced_upgrading_steam)
# CO2 avoided with el + heat

co2_avoided_tot_upgrading_steam = co2_el_avoided_upgrading_steam + co2_heat_avoided_upgrading_steam

#UBP
n_eutrophication_upgrading_steam = env.n_fertilizer_lost_post_application(n_acc_ad_steam - n_lost_post_storage_ad_steam)

ubp_nh3_emission_upgrading_steam = env.ubp_nh3(nh3_tot_ad_steam)
ubp_co2_emission_upgrading_steam = env.ubp_co2_eq(co2_eq_upgrading_steam)
ubp_n_eutrophication_upgrading_steam = env.ubp_eutrophication_n(n_eutrophication_upgrading_steam)

ubp_energy_renew_upgrading_steam = env.ubp_energy_non_renew(electricity_demand_upgrading_3_stage_tot_steam_joule)

ubp_upgrading_steam = ubp_nh3_emission_upgrading_steam + ubp_co2_emission_upgrading_steam + ubp_n_eutrophication_upgrading_steam + ubp_energy_renew_upgrading_steam









































#######################################################################################################################
#print data as a table
#######################################################################################################################

list_figures = []       # list of all figures, for printing and downloading


# round the values to 2 digits after the comma

# round AD
nh3_tot_ad = round(nh3_tot_ad, 2)
n2o_tot_ad = round(n2o_tot_ad, 2)
ch4_released_ad = round(ch4_released_ad, 2)
heat_net_ad = round(heat_net_ad, 2)
electricity_net_ad = round(electricity_net_ad, 2)
co2_eq_ad = round(co2_eq_ad, 2)
n_fertilizer_ad = round(n_fertilizer_ad, 2)
p_fertilizer_ad = round(p_fertilizer_ad, 2)
k_fertilizer_ad = round(k_fertilizer_ad, 2)
co2_eq_mineral_fertilizer_ad = round(co2_eq_mineral_fertilizer_ad, 2) * -1
so2_eq_nh3_ad = round(so2_eq_nh3_ad, 2)
energy_renew_ad = round(energy_renew_ad, 2)
ubp_ad = round(ubp_ad, 2)



co2_transport_tot = round(co2_transport_tot, 2)
# round untreated
nh3_tot_untreated = round(nh3_tot_untreated, 2)
n2o_tot_untreated = round(n2o_tot_untreated, 2)
ch4_untreated = round(ch4_untreated, 2)
heat_untreated = 0
electricity_untreated = 0
co2_eq_untreated = round(co2_eq_untreated, 2)
n_fertilizer_untreated = round(n_fertilizer_untreated, 2)
p_fertilizer_untreated = round(p_fertilizer_untreated, 2)
k_fertilizer_untreated = round(k_fertilizer_untreated, 2)
co2_eq_mineral_fertilizer_untreated = round(co2_eq_mineral_fertilizer_untreated, 2) * -1

ubp_untreated = round(ubp_untreated, 2)

so2_eq_nh3_untreated = round(so2_eq_nh3_untreated, 2)





manure_tot = round(manure_tot, 2)
print("Total manure produced is", manure_tot, "m3.")


# round biogas upgrading

heat_net_upgrading = round(heat_net_upgrading, 2)
electricity_net_upgrading = round(electricity_net_upgrading, 2)
ch4_released_upgrading_3_stage = round(ch4_released_upgrading_3_stage, 2)
co2_eq_upgrading = round(co2_eq_upgrading, 2)
ubp_upgrading = round(ubp_upgrading, 2)
energy_renew_upgrading = round(energy_renew_upgrading, 2)
biomethane_volume_3_stage = round(biomethane_volume_3_stage, 2)
co2_methane_upgrading = round(co2_methane_upgrading, 2)

# round steam treatment
nh3_tot_ad_steam = round(nh3_tot_ad_steam, 2)
n2o_tot_ad_steam = round(n2o_tot_ad_steam, 2)
ch4_released_ad_steam = round(ch4_released_ad_steam, 2)
heat_net_ad_steam = round(heat_net_ad_steam, 2)
net_electricity_ad_steam = round(net_electricity_ad_steam, 2)
co2_eq_ad_steam = round(co2_eq_ad_steam, 2)
n_fertilizer_ad_steam = round(n_fertilizer_ad_steam, 2)
p_fertilizer_ad_steam = round(p_fertilizer_ad_steam, 2)
k_fertilizer_ad_steam = round(k_fertilizer_ad_steam, 2)
co2_eq_mineral_fertilizer_ad_steam = round(co2_eq_mineral_fertilizer_ad_steam, 2) * -1
so2_eq_nh3_ad_steam = round(so2_eq_nh3_ad_steam, 2)
energy_renew_ad_steam = round(energy_renew_ad_steam, 2)
ubp_ad_steam = round(ubp_ad_steam, 2)



# round steam + biogas upgrading

heat_net_upgrading_steam = round(heat_net_upgrading_steam, 2)
electricity_net_upgrading_steam = round(electricity_net_upgrading_steam, 2)
ch4_released_upgrading_3_stage_steam = round(ch4_released_upgrading_3_stage_steam, 2)
co2_eq_upgrading_steam = round(co2_eq_upgrading_steam, 2)
ubp_upgrading_steam = round(ubp_upgrading_steam, 2)
biomethane_volume_3_stage_steam = round(biomethane_volume_3_stage_steam, 2)
co2_methane_upgrading_steam = round(co2_methane_upgrading_steam, 2)



######################################
# create list with dataframes for sensitivity analysis
#####################################

list_sens_analysis = []

##########################
#plots using plotly
########################

# create table for env. impacts

# create the DataFrame
data = [
    ["Heat generated after consumption [kWh]", heat_untreated, heat_net_ad, heat_net_upgrading, heat_net_ad_steam, heat_net_upgrading_steam],
    ["Electricity generated after consumption [kWh]", electricity_untreated, electricity_net_ad, electricity_net_upgrading, net_electricity_ad_steam, electricity_net_upgrading_steam],
    ["N fertilizer [kg N]", n_fertilizer_untreated, n_fertilizer_ad, n_fertilizer_ad, n_fertilizer_ad_steam, n_fertilizer_ad_steam],
    ["P fertilizer [kg P]", p_fertilizer_untreated, p_fertilizer_ad, p_fertilizer_ad, p_fertilizer_ad_steam, p_fertilizer_ad_steam],
    ["K fertilizer [kg K]", k_fertilizer_untreated, k_fertilizer_ad, k_fertilizer_ad, k_fertilizer_ad_steam, k_fertilizer_ad_steam],
    ["NH3 emitted [kg NH3]", nh3_tot_untreated, nh3_tot_ad, nh3_tot_ad, nh3_tot_ad_steam, nh3_tot_ad_steam],
    ["N2O emitted [kg N2O]", n2o_tot_untreated, n2o_tot_ad, n2o_tot_ad, n2o_tot_ad_steam, n2o_tot_ad_steam],
    ["CH4 emitted [kg CH4]", ch4_untreated, ch4_released_ad, ch4_released_upgrading_3_stage, ch4_released_ad_steam, ch4_released_upgrading_3_stage_steam],
    ["Global warming potential 100 [kg CO2-eq.]", co2_eq_untreated, co2_eq_ad, co2_eq_upgrading, co2_eq_ad_steam, co2_eq_upgrading_steam],
    ["CO2 eq. from replaced mineral fertilizer [kg CO2]", co2_eq_mineral_fertilizer_untreated, co2_eq_mineral_fertilizer_ad, co2_eq_mineral_fertilizer_ad, co2_eq_mineral_fertilizer_ad_steam, co2_eq_mineral_fertilizer_ad_steam],
    ["Acidification [kg SO2-eq.]", so2_eq_nh3_untreated, so2_eq_nh3_ad, so2_eq_nh3_ad, so2_eq_nh3_ad_steam, so2_eq_nh3_ad_steam],
    ["Schweizerische Umweltbelastungspunkte [UBP]", ubp_untreated, ubp_ad, ubp_upgrading, ubp_ad_steam, ubp_upgrading_steam],
    ["Biomethane produced [m3]", 0, 0, biomethane_volume_3_stage, 0, biomethane_volume_3_stage_steam]
]
columns = ["Data", "Untreated", "Anaerobic Digestion", "AD + Biogas upgrading + CHP", "AD + Steam + CHP", "AD + Steam + Upgrading + CHP"]
df = pd.DataFrame(data, columns=columns)

# create the table
table_env_plot = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df[col] for col in df.columns],
               fill_color='lavender',
               align=['left'] + ['right'] * (len(df.columns) - 1)))
])

table_env_plot.update_layout(title="General overview table")

list_figures.append(table_env_plot)




# create table for CO2/kWh




# create the DataFrame
data_co2_eq_el_production = [
    ["Electricity generated [kWh]", None, electricity_net_ad, electricity_produced_upgrading, electricity_chp_ad_steam, electricity_produced_upgrading_steam],
    ["CO2 eq. [kg CO2-eq.]", None, co2_eq_ad, co2_eq_upgrading, co2_eq_ad_steam, co2_eq_upgrading_steam],
    ["Global warming impact of generated electricity [kg CO2-eq. / kWh]", env.co2_el_verbraucher, co2_eq_el_production_ad, co2_eq_el_production_upgrading, co2_eq_el_production_steam, co2_eq_el_production_upgrading_steam],
]
# round values
for i, item_list in enumerate(data_co2_eq_el_production):
    for j, list_item in enumerate(item_list):
        if isinstance(list_item, (int, float)):
            data_co2_eq_el_production[i][j] = round(list_item, 2)


columns = ["Data", "Electricity Mix", "Anaerobic Digestion", "AD + Biogas upgrading + CHP + SOFC", "AD + Steam + CHP", "AD + Steam + Upgrading + CHP + SOFC"]
df_co2_eq_el_production = pd.DataFrame(data_co2_eq_el_production, columns=columns)

# create the table
table_co2_eq_el_production = go.Figure(data=[go.Table(
    header=dict(values=list(df_co2_eq_el_production.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df_co2_eq_el_production[col] for col in df_co2_eq_el_production.columns],
               fill_color='lavender',
               align=['left'] + ['right'] * (len(df_co2_eq_el_production.columns) - 1)))
])

table_co2_eq_el_production.update_layout(title="GHG emissions per kWh electricity generated")
list_figures.append(table_co2_eq_el_production)

list_sens_analysis.append(df_co2_eq_el_production)





#create pie chart of CO2 eq. emissions for AD


#round the relevant data points to 2 digits

co2_n2o_ad = round(env.co2_n2o(n2o_tot_ad), 2)
co2_methane_ad = round(env.co2_methane(ch4_released_ad), 2)
co2_biogenic_ad = round(co2_biogenic_ad, 2)

# create a list of values for the pie chart
values_pie_co2_ad = [co2_n2o_ad, co2_methane_ad, co2_biogenic_ad, co2_transport_tot]


# create a list of labels for the pie chart
labels_pie_co2_ad = ["N2O", "CH4", "CHP generator", "Transport"]

# create a list of sources for N2O and CH4
n2o_sources_labels = ["Pre storage", "AD process", "Post storage", "Field application"]
ch4_sources_labels = ["Pre storage", "AD process", "Post storage", "Field application"]

# create a list of source data for n2o and ch4 sources

data_n2o_sources_ad = [round(co2_n2o_pre_storage, 2), 0, round(co2_n2o_post_storage, 2), round(co2_n2o_field, 2)]
data_ch4_sources_ad = [round(co2_methane_pre_storage, 2), round(co2_methane_loss, 2), round(co2_methane_post_storage, 2), 0]


#create a hovertemplate for the pie chart
hovertemplate_pie_co2_ad = (
    "<b>%{label}</b><br>" +
    "Value: %{value} kg CO2 eq.<br>" +
    "%{percent}% of total<br><br>" +
    "<b>Sources:</b><br>" +
    f"{'<br>'.join(n2o_sources_labels)}: %{data_n2o_sources_ad}<br>" +
    f"{'<br>'.join(ch4_sources_labels)}: %{data_ch4_sources_ad}"
)

#create pie chart
pie_co2_ad = go.Figure(
    data=[go.Pie(
        labels=labels_pie_co2_ad,
        values=values_pie_co2_ad,
        hovertemplate=hovertemplate_pie_co2_ad
    )]
)

# set title

pie_co2_ad.update_layout(title="Contributors to GHG emissions of the Anaerobic Digestion in [kg CO2 eq.]")

# plot
list_figures.append(pie_co2_ad)


#plotly express sunburst co2 untreated
# create a list of labels for the pie chart
labels_emissions_sb_untreated = ["N2O", "N2O", "N2O", "N2O", "CH4", "CH4", "CH4"]

# create a list of sources for N2O and CH4
labels_sources_sb_untreated = ["Pre storage", "AD process", "Post storage", "Field application", "Pre storage", "Post storage", "Field application"]


# create a list of source data for n2o and ch4 sources
data_n2o_sources_untreated = [round(co2_n2o_pre_storage_untreated, 2), 0, round(co2_n2o_post_storage_untreated, 2), round(co2_n2o_field_untreated, 2)]
data_ch4_sources_untreated = [round(co2_methane_pre_storage_untreated, 2), round(co2_methane_post_storage_untreated, 2), co2_methane_field]


data_sb_untreated = pd.DataFrame(dict(
    emissions=labels_emissions_sb_untreated,
    sources=labels_sources_sb_untreated,
    values=data_n2o_sources_untreated + data_ch4_sources_untreated
))

# create the sunburst chart
sb_co2_untreated = px.sunburst(data_sb_untreated, path=["emissions", "sources"], values="values")

# set title
sb_co2_untreated.update_layout(title="GHG Emissions from no treatment (in kg CO2 eq.)")

# show the figure
list_figures.append(sb_co2_untreated)




#plotly express sunburst co2 AD
# create a list of labels for the pie chart
labels_emissions_sb_ad = ["N2O", "N2O", "N2O", "N2O", "CH4", "CH4", "CH4", "CH4", "Electricity", "Transport"]

# create a list of sources for N2O and CH4
labels_sources_sb_ad = ["Pre storage", "AD process", "Post storage", "Field application", "Pre storage", "AD process", "Post storage", "Field application", "Anaerobic Digestion", None]


# create a list of source data for n2o and ch4 sources
data_n2o_sources_ad = [round(co2_n2o_pre_storage, 2), 0, round(co2_n2o_post_storage, 2), round(co2_n2o_field, 2)]
data_ch4_sources_ad = [round(co2_methane_pre_storage, 2), round(co2_methane_loss, 2), round(co2_methane_post_storage, 2), co2_methane_field]
data_electricity_ad = [round(co2_eq_electricity_demand_ad, 2)]
data_process_ad = [round(co2_transport_tot, 2)]

data_sb_ad = pd.DataFrame(dict(
    emissions=labels_emissions_sb_ad,
    sources=labels_sources_sb_ad,
    values=data_n2o_sources_ad + data_ch4_sources_ad + data_electricity_ad + data_process_ad
))

# create the sunburst chart
sb_co2_ad = px.sunburst(data_sb_ad, path=["emissions", "sources"], values="values")

# set title
sb_co2_ad.update_layout(title="GHG Emissions from Anaerobic Digestion (in kg CO2 eq.)")

# show the figure
list_figures.append(sb_co2_ad)




#plotly express sunburst co2 upgrading
# create a list of labels for the pie chart
labels_emissions_sb_upgrading = ["N2O", "N2O", "N2O", "N2O",
                                 "CH4", "CH4", "CH4", "CH4", "CH4",
                                 "Electricity", "Electricity",
                                 "Transport"]

# create a list of sources for N2O and CH4
labels_sources_sb_upgrading = ["Pre storage", "AD process", "Post storage", "Field application",
                               "Pre storage", "AD process", "Biogas upgrading", "Post storage", "Field application",
                               "Anaerobic Digestion", "Biogas upgrading",
                               None]


# create a list of source data for n2o and ch4 sources
data_n2o_sources_upgrading = [round(co2_n2o_pre_storage, 2), 0, round(co2_n2o_post_storage, 2), round(co2_n2o_field, 2)]
data_ch4_sources_upgrading = [round(co2_methane_pre_storage, 2), round(co2_methane_loss, 2), round(co2_methane_loss_upgrading, 2), round(co2_methane_post_storage, 2), 0]
data_electricity_upgrading = [round(co2_eq_electricity_demand_ad, 2), round(co2_eq_electricity_demand_bg_upgrade_upgrading, 2)]
data_process_upgrading = [co2_transport_tot]

data_sb_upgrading = pd.DataFrame(dict(
    emissions=labels_emissions_sb_upgrading,
    sources=labels_sources_sb_upgrading,
    values=data_n2o_sources_upgrading + data_ch4_sources_upgrading + data_electricity_upgrading + data_process_upgrading
))

# create the sunburst chart
sb_co2_upgrading = px.sunburst(data_sb_upgrading, path=["emissions", "sources"], values="values")

# set title
sb_co2_upgrading.update_layout(title="GHG Emissions from AD + Biogas Upgrading  (in kg CO2 eq.)")

# show the figure
list_figures.append(sb_co2_upgrading)





#plotly express sunburst co2 steam treatment
# create a list of labels for the pie chart
labels_emissions_sb_steam = ["N2O", "N2O", "N2O", "N2O",
                             "CH4", "CH4", "CH4", "CH4",
                             "Electricity",
                             "Transport"]

# create a list of sources for N2O and CH4
labels_sources_sb_steam = ["Pre storage", "AD process", "Post storage", "Field application",
                           "Pre storage", "AD process", "Post storage", "Field application",
                           "Anaerobic Digestion",
                           None]


# create a list of source data for n2o and ch4 sources
data_n2o_sources_steam = [round(co2_n2o_pre_storage, 2), 0, round(co2_n2o_post_storage, 2), round(co2_n2o_field, 2)]
data_ch4_sources_steam = [round(co2_methane_pre_storage, 2), round(co2_methane_loss_steam, 2), round(co2_methane_post_storage_steam, 2), 0]
data_electricity_steam = [round(co2_eq_electricity_demand_steam, 2)]
data_process_steam = [co2_transport_tot]

data_sb_steam = pd.DataFrame(dict(
    emissions=labels_emissions_sb_steam,
    sources=labels_sources_sb_steam,
    values=data_n2o_sources_steam + data_ch4_sources_steam + data_electricity_steam + data_process_steam
))

# create the sunburst chart
sb_co2_steam = px.sunburst(data_sb_steam, path=["emissions", "sources"], values="values")

# set title
sb_co2_steam.update_layout(title="GHG Emissions from Steam treatment + AD  (in kg CO2 eq.)")

# show the figure
list_figures.append(sb_co2_steam)




#plotly express sunburst co2 steam treatment + biogas upgrading
# create a list of labels for the pie chart
labels_emissions_sb_upgrading_steam = ["N2O", "N2O", "N2O", "N2O",
                                       "CH4", "CH4", "CH4", "CH4", "CH4",
                                       "Electricity", "Electricity",
                                       "Transport"]

# create a list of sources for N2O and CH4
labels_sources_sb_upgrading_steam = ["Pre storage", "AD process", "Post storage", "Field application",
                                     "Pre storage", "AD process", "Biogas upgrading", "Post storage", "Field application",
                                     "Anaerobic Digestion", "Biogas upgrading",
                                     None]



# create a list of source data for n2o and ch4 sources
data_n2o_sources_upgrading_steam = [round(co2_n2o_pre_storage, 2), 0, round(co2_n2o_post_storage, 2), round(co2_n2o_field, 2)]
data_ch4_sources_upgrading_steam = [round(co2_methane_pre_storage_steam, 2), round(co2_methane_loss_ad_upgrading_steam, 2), round(co2_methane_loss_upgrading_steam, 2), round(co2_methane_post_storage_steam, 2), 0]
data_electricity_upgrading_steam = [round(co2_eq_electricity_demand_ad_upgrading_steam, 2), round(co2_eq_electricity_demand_bg_upgrade_upgrading_steam, 2)]
data_process_upgrading_steam = [co2_transport_tot]

data_sb_upgrading_steam = pd.DataFrame(dict(
    emissions=labels_emissions_sb_upgrading_steam,
    sources=labels_sources_sb_upgrading_steam,
    values=data_n2o_sources_upgrading_steam + data_ch4_sources_upgrading_steam + data_electricity_upgrading_steam + data_process_upgrading_steam
))

# create the sunburst chart
sb_co2_upgrading_steam = px.sunburst(data_sb_upgrading_steam, path=["emissions", "sources"], values="values")

# set title
sb_co2_upgrading_steam.update_layout(title="GHG Emissions from Steam treatment + Biogas upgrading + AD  (in kg CO2 eq.)")

# show the figure
list_figures.append(sb_co2_upgrading_steam)






##########################################
# Bar charts
###########################################
list_types = ["Untreated", "Anaerobic Digestion", "AD + Biogas upgrading + CHP", "AD + Steam + CHP", "AD + Steam + Upgrading + CHP"]
types_co2_eq_el_production = ["Electricity Mix", "Anaerobic Digestion", "AD + Biogas upgrading + CHP + SOFC", "AD + Steam + CHP", "AD + Steam + Upgrading + CHP + SOFC"]



############################
# bar chart CO2 equivalents per kWh electricity produced
#############################


list_co2_el_production = [env.co2_el_verbraucher, co2_eq_el_production_ad, co2_eq_el_production_upgrading, co2_eq_el_production_steam, co2_eq_el_production_upgrading_steam]
for i, my_item in enumerate(list_co2_el_production):
    list_co2_el_production[i] = round(my_item, 2)


df_co2_el_production_bar = pd.DataFrame({
    "Type": types_co2_eq_el_production,
    "CO2-eq el": list_co2_el_production
})



co2_eq_el_production_bar = px.bar(df_co2_el_production_bar, x="Type", y="CO2-eq el", title="CO2 eq. GWP 100")
co2_eq_el_production_bar.update_layout(yaxis_title="Global warming Impact [kg CO2-eq. / kWh]")



list_figures.append(co2_eq_el_production_bar)


list_sens_analysis.append(df_co2_el_production_bar)


############################
# bar chart CO2 equivalents, grouped with comparison negative CO2, that is CO2 emissions that are avoided
#############################

list_types_short = ["Anaerobic Digestion", "AD + Biogas upgrading + CHP", "AD + Steam + CHP", "AD + Steam + Upgrading + CHP"]


labels_co2_avoided = ["Emissions", "Avoided", "Biogenic"]

list_co2_emissions = [co2_eq_ad, co2_eq_upgrading, co2_eq_ad_steam, co2_eq_upgrading_steam]
list_co2_avoided = [co2_avoided_tot_ad, co2_avoided_tot_upgrading, co2_avoided_tot_steam, co2_avoided_tot_upgrading_steam]
list_co2_biogenic = [co2_biogenic_ad, co2_biogenic_upgrading, co2_biogenic_ad_steam, co2_biogenic_upgrading_steam]

for i, my_item in enumerate(list_co2_avoided):
    list_co2_avoided[i] = round(my_item, 2) * -1

for i, my_item in enumerate(list_co2_biogenic):
    list_co2_biogenic[i] = round(my_item, 2) * -1




df_co2_avoided_bar = pd.DataFrame({
    "Type": list_types_short,
    "Emissions": list_co2_emissions,
    "Avoided": list_co2_avoided,
    "Biogenic": list_co2_biogenic
})


co2_eq_avoided_bar = px.bar(df_co2_avoided_bar, x="Type", y=labels_co2_avoided, barmode="group", title="GHG emissions vs emissions avoided vs potential biogenic CO2 capture")
co2_eq_avoided_bar.update_layout(yaxis_title="GWP 100 [kg CO2-eq.]")



list_figures.append(co2_eq_avoided_bar)


list_sens_analysis.append(df_co2_avoided_bar)





############################
# bar chart CO2 equivalents
#############################


co2_n2o_untreated = round(env.co2_n2o(n2o_tot_untreated), 2)
co2_methane_untreated = round(env.co2_methane(ch4_untreated), 2)
co2_chp_untreated = 0
co2_transport_tot_untreated = 0


labels_co2_short = ["N2O", "CH4", "Transport"]

list_co2_n2o = [co2_n2o_untreated, co2_n2o_ad, co2_n2o_ad, co2_n2o_ad_steam, co2_n2o_ad_steam]
list_co2_methane = [co2_methane_untreated, co2_methane_ad, co2_methane_upgrading, co2_ch4_ad_steam, co2_methane_upgrading_steam]

list_co2_transport = [co2_transport_tot_untreated, co2_transport_tot, co2_transport_tot, co2_transport_tot, co2_transport_tot]

df_co2_bar = pd.DataFrame({
    "Type": list_types,
    "N2O": list_co2_n2o,
    "CH4": list_co2_methane,
    "Transport": list_co2_transport
})

print(df_co2_bar)

co2_eq_bar = px.bar(df_co2_bar, x="Type", y=labels_co2_short, title="CO2 eq. GWP 100")
co2_eq_bar.update_layout(yaxis_title="GWP 100 [kg CO2-eq.]")



list_figures.append(co2_eq_bar)

list_sens_analysis.append(df_co2_bar)


######################################
# Bar NH3 emissions with sources   nh3_tot_AD = nh3_field_AD + nh3_post_storage_AD + nh3_released_pre_storage
###################################


list_pre_storage_nh3 = [0, nh3_released_pre_storage, nh3_released_pre_storage, nh3_released_pre_storage, nh3_released_pre_storage]
list_post_storage_nh3 = [nh3_untreated, nh3_post_storage_AD, nh3_post_storage_AD, nh3_post_storage_ad_steam, nh3_post_storage_ad_steam]
list_field_nh3 = [nh3_untreated_field, nh3_field_AD, nh3_field_AD, nh3_field_ad_steam, nh3_field_ad_steam]
list_acid = [so2_eq_nh3_untreated, so2_eq_nh3_ad, so2_eq_nh3_ad, so2_eq_nh3_ad_steam, so2_eq_nh3_ad_steam]
labels_nh3_bar = ["Pre Storage", "Post Storage", "Field application"]


df_nh3_bar = pd.DataFrame({
    "Type": list_types,
    "Pre Storage": list_pre_storage_nh3,
    "Post Storage": list_post_storage_nh3,
    "Field application": list_field_nh3
})


nh3_emission_bar = px.bar(df_nh3_bar, x="Type", y=labels_nh3_bar, title="NH3 emissions")
nh3_emission_bar.update_layout(yaxis_title="NH3 emissions [kg NH3]")

list_figures.append(nh3_emission_bar)


list_sens_analysis.append(df_nh3_bar)



#################################
# Bar chart electricity and heat
####################################


list_electricity = [electricity_chp_AD, electricity_produced_upgrading, electricity_chp_ad_steam, electricity_produced_upgrading_steam]
list_heat = [heat_net_ad, heat_net_upgrading, heat_net_ad_steam, heat_net_upgrading_steam]

df_el_heat_bar = pd.DataFrame({
    "Type": list_types_short,
    "Electricity": list_electricity,
    "Heat": list_heat
})

energy_generation_bar = px.bar(df_el_heat_bar, x="Type", y=["Electricity", "Heat"], barmode="group", title="Heat and electricity generated")
energy_generation_bar.update_layout(yaxis_title="Energy generated [kWh]")

list_figures.append(energy_generation_bar)


list_sens_analysis.append(df_el_heat_bar)


##########################
# Bar chart UBP
#############################
# ubp_untreated = ubp_co2_emission_untreated + ubp_nh3_emission_untreated + ubp_n_eutrophication_untreated + ubp_energy_non_renew_untreated
# ubp_ad = ubp_nh3_emission_ad + ubp_co2_emission_ad + ubp_n_eutrophication_ad + ubp_energy_renew_ad


list_ubp_co2 = [ubp_co2_emission_untreated, ubp_co2_emission_ad, ubp_co2_emission_upgrading, ubp_co2_emission_ad_steam, ubp_co2_emission_upgrading_steam]
list_ubp_nh3 = [ubp_nh3_emission_untreated, ubp_nh3_emission_ad, ubp_nh3_emission_upgrading, ubp_nh3_emission_ad_steam, ubp_nh3_emission_upgrading_steam]
list_ubp_eutrophication = [ubp_n_eutrophication_untreated, ubp_n_eutrophication_ad, ubp_n_eutrophication_upgrading, ubp_n_eutrophication_ad_steam, ubp_n_eutrophication_upgrading_steam]
list_ubp_energy = [0, ubp_energy_renew_ad, ubp_energy_renew_upgrading, ubp_energy_renew_ad_steam, ubp_energy_renew_upgrading_steam]

df_ubp_bar = pd.DataFrame({
    "Type": list_types,
    "CO2 emission": list_ubp_co2,
    "NH3 emission": list_ubp_nh3,
    "Eutrophication": list_ubp_eutrophication,
    "Energy": list_ubp_energy
})
list_ubp_factors = ["CO2 emission", "NH3 emission", "Eutrophication", "Energy"]

ubp_bar = px.bar(df_ubp_bar, x="Type", y=list_ubp_factors, title="Schweizerische Umweltbelastungspunkte (UBP)")
ubp_bar.update_layout(yaxis_title="Umweltbelastungspunkte [UBP]")


list_figures.append(ubp_bar)


list_sens_analysis.append(df_ubp_bar)


####################################
# Bar chart N2O emissions
###################################
# n2o_untreated + n2o_untreated_field
# n2o_tot_AD = n2o_field_AD + n2o_post_storage_AD + n2o_released_pre_storage



list_n2o_pre_storage = [0, n2o_released_pre_storage, n2o_released_pre_storage, n2o_released_pre_storage, n2o_released_pre_storage]
list_n2o_post_storage = [n2o_untreated, n2o_post_storage_AD, n2o_post_storage_AD, n2o_post_storage_ad_steam, n2o_post_storage_ad_steam]
list_n2o_field = [n2o_untreated_field, n2o_field_AD, n2o_field_AD, n2o_field_ad_steam, n2o_field_ad_steam]


df_n2o_bar = pd.DataFrame({
    "Type": list_types,
    "Pre Storage": list_n2o_pre_storage,
    "Post Storage": list_n2o_post_storage,
    "Field application": list_n2o_field
})

labels_n2o_bar = ["Pre Storage", "Post Storage", "Field application"]

n2o_emission_bar = px.bar(df_n2o_bar, x="Type", y=labels_n2o_bar, title="N2O emissions")
n2o_emission_bar.update_layout(yaxis_title="N2O emissions [kg N2O]")

list_figures.append(n2o_emission_bar)



list_sens_analysis.append(df_n2o_bar)


###############################################
# CH4 emissions bar chart
##############################################
# ch4_released_AD = ch4_pre_storage + ch4_post_storage + methane_loss_mass


list_ch4_pre_storage = [0, ch4_pre_storage, ch4_pre_storage, ch4_pre_storage, ch4_pre_storage]
list_ch4_post_storage = [ch4_untreated, ch4_post_storage, ch4_post_storage, ch4_post_storage_steam, ch4_post_storage_steam]
list_ch4_ad = [0, methane_loss_mass_ad, methane_loss_mass_ad, methane_loss_mass_steam, methane_loss_mass_steam]
list_ch4_upgrading = [0, 0, ch4_loss_upgrading_mass, 0, ch4_loss_upgrading_mass_steam]


df_ch4_bar = pd.DataFrame({
    "Type": list_types,
    "Pre Storage": list_ch4_pre_storage,
    "Post Storage": list_ch4_post_storage,
    "Digester": list_ch4_ad,
    "Upgrading": list_ch4_upgrading
})

labels_ch4_bar = ["Pre Storage", "Post Storage", "Digester", "Upgrading"]

ch4_emission_bar = px.bar(df_ch4_bar, x="Type", y=labels_ch4_bar, title="CH4 emissions")
ch4_emission_bar.update_layout(yaxis_title="Methane emissions [kg CH4]")

list_figures.append(ch4_emission_bar)


list_sens_analysis.append(df_ch4_bar)

# Bar chart fossil Fuel replaced



# show figures

path_download = os.path.join(os.getcwd(), 'downloads')

for fig in list_figures:
    #fig.show()

    # Set the size of the figure
    fig.update_layout(
        width=1920,
        height=1080
    )

    # Adjust the margins to make sure all elements are visible
    fig.update_layout(
        margin=dict(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        )
    )

    title = fig.layout.title.text
    filename_png = os.path.join(path_download, f"{title}.png")
    filename_html = os.path.join(path_download, f"{title}.html")
    pio.write_image(fig, filename_png)
    pio.write_html(fig, filename_html)


# combine the sens analysis list and download as excel file

filename_sens_analysis = os.path.join(path_download, "sens_analysis.xlsx")
sens_anaylsis_df = pd.concat(list_sens_analysis)
sens_anaylsis_df.to_excel(filename_sens_analysis)






