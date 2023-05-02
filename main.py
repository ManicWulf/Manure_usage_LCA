from prettytable import PrettyTable
import plotly.graph_objs as go

import Anaerobic_Digestion as AD
import Animal_Class as AC
import CHP
import Environmental_impact as env
import manure_storage as ms


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



#define list of animal classes used.

animal_classes = ["Milchkuh", "Mutterkuh", "Aufzuchtrind", "Mastkalb", "Mutterkuhkalb", "RiendviehMast", "Zuchtstier", "Mastschwein", "Zuchtschweineplatz", "Legehenne", "Junghenne", "Mastpoulet"]

num_farms = int(input("How many farms do you want to calculate for? "))
farms = {}

# Get user input for each farm and store in a nested dictionary
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
                        "animals": farm_dict}

# Calculate methane potential, n_tot, p_tot, k_tot, manure and pre storage for each farm
for farm_name, farm_data in farms.items():
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
        methane_pot_tot_farm += animal.methane_pot_tot / 1000       #m3 CH4
        n_tot_farm += animal.n_tot
        p_tot_farm += animal.p_tot
        k_tot_farm += animal.k_tot
        manure_l_tot_farm += animal.manure_l_tot / 1000         #in m3
        manure_s_tot_farm += animal.manure_s_tot / 1000         #in m3
        manure_straw_tot_farm += animal.manure_straw_tot / 1000 #in m3

    n_tot += n_tot_farm
    p_tot += p_tot_farm
    k_tot += k_tot_farm
    methane_pot_tot += methane_pot_tot_farm
    manure_tot_farm = manure_s_tot_farm + manure_l_tot_farm
    manure_tot += manure_tot_farm
    # Calculate values for pre storage

    pre_storage_farm = int(input(f"How many days on average is the manure going to be stored before processing in the digester for farm {farm_name}? "))
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

    print(f"farm {farm_name}: N2O in pre storage:", n2o_pre_storage_farm)
    print(f"N-tot of {farm_name}", n_tot_farm)

    diesel_transport_farm = env.fuel_consumption_transport(manure_tot_farm, farms[farm_name]["distance_from_power_plant"])
    co2_transport_farm = env.env_impact_diesel(diesel_transport_farm)
    diesel_transport_tot += diesel_transport_farm
    co2_transport_tot += co2_transport_farm


post_storage = ms.storage_input()
print("CH4 released pre storage:", ch4_released_pre_storage)
print("N-tot:", n_tot)
print("N-tot pre storage:", n_tot_pre_storage)
#######################################################################################################################
#Anaerobic digestion, storage of digestate and application on field
#######################################################################################################################



# input potential methane production, output effective methane [m3/y] adjusted for size of AD plant




#methane lost during anaerobic digestion
effective_methane_AD = AD.methane_yield(effective_methane_pre_storage)             #in m3 per year
methane_loss = AD.methane_loss(effective_methane_AD)                 #m3 per year
co2_methane_loss = env.co2_methane(ms.ch4_volume_to_mass(methane_loss))                        #kg CO2
co2_methane_pre_storage = env.co2_methane(ch4_pre_storage)                                      #kg CO2

c_tot_digestate_AD = c_tot_pre_storage - ms.c_total(effective_methane_AD)  #in kg C

effective_methane_post_loss_AD = effective_methane_AD - methane_loss                                 #m3 per year

ch4_post_storage = ms.ch4_release_AD(c_tot_digestate_AD, post_storage)  #how much ch4 is released during the storage of the digestate [kg/year]
co2_methane_post_storage = env.co2_methane(ch4_post_storage)

ch4_released_AD = ch4_pre_storage + ch4_post_storage + ms.ch4_volume_to_mass(methane_loss)       #kg CH4

#n_lost_post_storage_AD = ms.N_reduction_AD(n_tot_pre_storage, post_storage)              #how much N is lost during storage [kg/year]
#nh3_post_storage_AD, n2o_post_storage_AD = ms.NH3_vs_N2O_AD(n_lost_post_storage_AD)                    #how much nh3 and n2o is released during storage [kg/year]
nh3_post_storage_AD = ms.nh3_storage_ad(n_tot_pre_storage, post_storage)  # NH3 emitted in kg N
n2o_post_storage_AD= ms.n2o_storage_ad(n_tot_pre_storage, post_storage)  # N2O emitted in kg N
n_lost_post_storage_AD = n2o_post_storage_AD + nh3_post_storage_AD  # N lost in kg N
nh3_post_storage_AD = ms.n_to_nh3(nh3_post_storage_AD)  # NH3 in kg NH3
n2o_pre_storage_farm = ms.n_to_n2o(n2o_post_storage_AD)  # N2O in kg N2O
n_acc_ad = ms.n_acc_ad(n_tot_pre_storage)
nh3_field_AD = ms.nh3_field(n_acc_ad)                      #in kg N per year
n2o_field_AD = ms.n2o_field(n_acc_ad - nh3_field_AD)                      #in kg N per year
nh3_field_AD = ms.n_to_nh3(nh3_field_AD)        #in kg NH3
n2o_field_AD = ms.n_to_n2o(n2o_field_AD)        #in kg N2O
n_fertilizer_AD = n_acc_ad - n_lost_post_storage_AD
p_fertilizer_AD = p_tot
k_fertilizer_AD = k_tot

co2_n2o_pre_storage = env.co2_n2o(n2o_released_pre_storage)
co2_n2o_post_storage = env.co2_n2o(n2o_post_storage_AD)
co2_n2o_field = env.co2_n2o(n2o_field_AD)

print("N lost post storage AD:", n_lost_post_storage_AD)
print("ch4 released AD post storage:", ch4_post_storage)
print("CH4 released AD loss:", ms.ch4_volume_to_mass(methane_loss))

nh3_tot_AD = nh3_field_AD + nh3_post_storage_AD + nh3_released_pre_storage
n2o_tot_AD = n2o_field_AD + n2o_post_storage_AD + n2o_released_pre_storage
biogas_AD, co2_bg_AD = AD.biogas(effective_methane_post_loss_AD)                      #in [m3]
heat_chp_AD, electricity_chp_AD = CHP.energy_produced(effective_methane_post_loss_AD)      #in [kWh]
heat_demand_AD = AD.heat_demand(manure_tot)                        #in [kWh]
electricity_demand_ad = AD.electricity_demand(biogas_AD)            #in [kWh]
heat_net_AD = heat_chp_AD - heat_demand_AD     #heat produced minus heat used for heating the digestate
net_electricity_ad = electricity_chp_AD - electricity_demand_ad
co2_chp_AD = CHP.co2_release(co2_bg_AD, effective_methane_post_loss_AD)   #CO2 released after burning of the biogas in CHP

co2_eq_mineral_fertilizer_AD = env.co2_mineral_nitrate(n_fertilizer_AD) + env.co2_mineral_k(k_fertilizer_AD) + env.co2_mineral_P(p_fertilizer_AD)
co2_eq_AD = env.co2_n2o(n2o_tot_AD) + env.co2_methane(ch4_released_AD) + co2_chp_AD + co2_transport_tot


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
co2_eq_mineral_fertilizer_untreated = env.co2_mineral_nitrate(n_fertilizer_untreated) + env.co2_mineral_k(k_fertilizer_untreated) + env.co2_mineral_P(p_fertilizer_untreated)

co2_eq_untreated = env.co2_n2o(n2o_tot_untreated) + env.co2_methane(ch4_untreated)

print("N lost storage untreated:", n_lost_untreated)
print("N2O released untreated storage:", n2o_untreated)
print("N2O released untreated field:", n2o_untreated_field)









#######################################################################################################################
#print data as a table
#######################################################################################################################

# round the values to 2 digits after the comma
nh3_tot_AD = round(nh3_tot_AD, 2)
n2o_tot_AD = round(n2o_tot_AD, 2)
ch4_AD = round(ch4_released_AD, 2)
heat_AD = round(heat_net_AD, 2)
electricity_AD = round(net_electricity_ad, 2)
co2_eq_AD = round(co2_eq_AD, 2)
n_fertilizer_AD = round(n_fertilizer_AD, 2)
p_fertilizer_AD = round(p_fertilizer_AD, 2)
k_fertilizer_AD = round(k_fertilizer_AD, 2)
co2_eq_mineral_fertilizer_AD = round(co2_eq_mineral_fertilizer_AD, 2) * -1

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
co2_transport_tot = round(co2_transport_tot, 2)

manure_tot = round(manure_tot, 2)
print("Total manure produced is", manure_tot, "m3.")

# create the table
table_env = PrettyTable()
table_env.field_names = ["Data", "Anaerobic Digestion", "No Treatment"]
table_env.add_row(["Heat produced after consumption [kWh]", heat_AD, heat_untreated])
table_env.add_row(["Electricity produced after consumption [kWh]", electricity_AD, electricity_untreated])
table_env.add_row(["N fertilizer [kg N]", n_fertilizer_AD, n_fertilizer_untreated])
table_env.add_row(["P fertilizer [kg P]", p_fertilizer_AD, p_fertilizer_untreated])
table_env.add_row(["K fertilizer [kg K]", k_fertilizer_AD, k_fertilizer_untreated])
table_env.add_row(["NH3 emitted [kg NH3]", nh3_tot_AD, nh3_tot_untreated])
table_env.add_row(["N2O emitted [kg N2O]", n2o_tot_AD, n2o_tot_untreated])
table_env.add_row(["CH4 emitted [kg CH4]", ch4_AD, ch4_untreated])
table_env.add_row(["CO2 equivalent total [kg CO2]", co2_eq_AD, co2_eq_untreated])
table_env.add_row(["CO2 eq. from replaced mineral fertilizer [kg CO2]", co2_eq_mineral_fertilizer_AD, co2_eq_mineral_fertilizer_untreated])

# print the table
print(table_env)


##########################
#plots using plotly
########################

#create pie chart of CO2 eq. emissions for AD


#round the relevant data points to 2 digits

co2_n2o_ad = round(env.co2_n2o(n2o_tot_AD), 2)
co2_methane_ad = round(env.co2_methane(ch4_released_AD), 2)
co2_chp_AD = round(co2_chp_AD, 2)
co2_transport_tot = round(co2_transport_tot, 2)

# create a list of values for the pie chart
values_pie_co2_ad = [co2_n2o_ad, co2_methane_ad, co2_chp_AD, co2_transport_tot]


# create a list of labels for the pie chart
labels_pie_co2_ad = ["N2O", "CH4", "CHP generator", "Transport"]

# create a list of sources for N2O and CH4
n2o_sources_labels = ["Pre storage", "AD process", "Post storage", "Field application"]
ch4_sources_labels = ["Pre storage", "AD process", "Post storage", "Field application"]

# create a list of source data for n2o and ch4 sources

data_n2o_sources = [round(co2_n2o_pre_storage, 2), 0, round(co2_n2o_post_storage, 2), round(co2_n2o_field, 2)]
data_ch4_sources = [round(co2_methane_pre_storage, 2), round(co2_methane_loss, 2), round(co2_methane_post_storage, 2), 0]


#create a hovertemplate for the pie chart
hovertemplate_pie_co2_ad = (
    "<b>%{label}</b><br>" +
    "Value: %{value} kg CO2 eq.<br>" +
    "%{percent}% of total<br><br>" +
    "<b>Sources:</b><br>" +
    f"{'<br>'.join(n2o_sources_labels)}: %{data_n2o_sources}<br>" +
    f"{'<br>'.join(ch4_sources_labels)}: %{data_ch4_sources}"
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

pie_co2_ad.update_layout(title_text="Contributors to GHG emissions of the Anaerobic Digestion in [kg CO2 eq.]")

# plot
pie_co2_ad.show()


# create the sunburst chart
sunburst_fig = go.Figure(go.Sunburst(
    labels=labels_pie_co2_ad + n2o_sources_labels + ch4_sources_labels,
    parents=[""] * len(labels_pie_co2_ad) + labels_pie_co2_ad[0:1] * len(n2o_sources_labels) + labels_pie_co2_ad[1:2] * len(ch4_sources_labels),
    values=values_pie_co2_ad + data_n2o_sources + data_ch4_sources,
    maxdepth=2,
))

# set title
sunburst_fig.update_layout(title_text="GHG Emissions from Anaerobic Digestion (in kg CO2 eq.)")

# show the figure
sunburst_fig.show()
