import Animal_Class as AC
import Anaerobic_Digestion as AD
import CHP
import manure_storage as ms
import Environmental_impact as env
from prettytable import PrettyTable

#define function for user input

def get_user_input(class_name):
    num_animals = int(input(f"How many {class_name} do you have?"))
    if num_animals != 0:
        days_outside = int(input("How many days of the year are they outside of the stable on average?"))
        hours_outside = float(input("On the days they are outside the stable, how many hours on average are they out?"))
        manure_type = int(input("What kind of manure do you collect? 0: only liquid. 1: liquid and solid. 2: only solid."))
    else:
        days_outside = 0
        hours_outside = 0
        manure_type = 0
    return num_animals, days_outside, hours_outside, manure_type


#define variables
manure_l_tot = 0
manure_s_tot = 0
manure_straw_tot = 0
methane_pot_tot = 0
n_tot = 0
p_tot = 0
k_tot = 0



#define list of animal classes used.

animal_classes = ["Milchkuh", "Mutterkuh", "Aufzuchtrind", "Mastkalb", "Mutterkuhkalb", "RiendviehMast", "Zuchtstier", "Mastschwein", "Zuchtschweineplatz", "Legehenne", "Junghenne", "Mastpoulet"]


#get input for every animal class and write it into a dictionary called animals. to get the specific class instance, use "animals[Milchkuh]" for example

animals = {}
for animal_class in animal_classes:
    num_animals, days_outside, hours_outside, manure_type = get_user_input(animal_class)
    animals[animal_class] = getattr(AC, animal_class)(num_animals, days_outside, hours_outside, manure_type)

storage_time = ms.storage_input()

#calculate the manure production, methane potential and nutrients for the input animals and sum it up
for animal_class in animal_classes:
    animals[animal_class].manure_prod()
    animals[animal_class].manure_prod_tot()
    animals[animal_class].methane_pot()
    animals[animal_class].nutrients()
    methane_pot_tot += animals[animal_class].methane_pot_tot
    n_tot += animals[animal_class].n_tot
    p_tot += animals[animal_class].p_tot
    k_tot += animals[animal_class].k_tot
    manure_l_tot += animals[animal_class].manure_l_tot
    manure_s_tot += animals[animal_class].manure_s_tot
    manure_straw_tot += animals[animal_class].manure_straw_tot


#######################################################################################################################
#Anaerobic digestion, storage of digestate and application on field
#######################################################################################################################
# input potential methane production, output effective methane [l/y] adjusted for size of AD plant

manure_tot = manure_l_tot + manure_s_tot        #in kg per year

effective_methane_AD = AD.methane_yield(methane_pot_tot) / 1000      #in m3 per year
methane_loss = AD.methane_loss(effective_methane_AD)
effective_methane_AD -= methane_loss

c_tot = ms.c_total(effective_methane_AD)
c_tot_digestate_AD = c_tot - effective_methane_AD
ch4_storage = ms.ch4_release_AD(c_tot_digestate_AD, storage_time)  #how much ch4 is released during the storage of the digestate [kg/year]
ch4_released_AD = ch4_storage + methane_loss


n_lost_AD = ms.N_reduction_AD(n_tot, storage_time)              #how much N is lost during storage [kg/year]
nh3_AD, n2o_AD = ms.NH3_vs_N2O_AD(n_lost_AD)                    #how much nh3 and n2o is released during storage [kg/year]
nh3_field_AD = ms.nh3_field_AD(manure_tot)                      #in kg per year
n2o_field_AD = ms.n2o_field_AD(manure_tot)                      #in kg per year
n_fertilizer_AD = n_tot - n_lost_AD
p_fertilizer_AD = p_tot
k_fertilizer_AD = k_tot

nh3_tot_AD = nh3_field_AD + nh3_AD
n2o_tot_AD = n2o_field_AD + n2o_AD
biogas_AD, co2_bg_AD = AD.biogas(effective_methane_AD)                      #in [m3]
heat_chp_AD, electricity_chp_AD = CHP.energy_produced(effective_methane_AD)      #in [MW]
heat_demand_AD = AD.heat_demand(manure_tot)                        #in [MW]
heat_net_AD = heat_chp_AD - heat_demand_AD     #heat produced minus heat used for heating the digestate
co2_chp_AD = CHP.co2_release(co2_bg_AD, effective_methane_AD)   #CO2 released after burning of the biogas in CHP

co2_eq_mineral_fertilizer_AD = env.co2_mineral_nitrate(n_fertilizer_AD) + env.co2_mineral_k(k_fertilizer_AD) + env.co2_mineral_P(p_fertilizer_AD)
co2_eq_AD = env.co2_n2o(n2o_tot_AD) + env.co2_methane(ch4_released_AD) + co2_chp_AD


#######################################################################################################################
#no treatment, just storage of manure and application on field
#######################################################################################################################

ch4_untreated = ms.ch4_release_untreated(c_tot, storage_time)               #how much ch4 is released during storage of manure
n_lost_untreated = ms.N_reduction_untreated(n_tot, storage_time)            #how much N is lost during storage of manure
nh3_untreated, n2o_untreated = ms.NH3_vs_N2O_untreated(n_lost_untreated)    #how much nh3 and n2o is released during storage
nh3_untreated_field = ms.nh3_field_untreated(manure_tot)                    #kg nh3 per year
n2o_untreated_field = ms.n2o_field_untreated(manure_tot)                    #kg n2o per year
nh3_tot_untreated = nh3_untreated_field + nh3_untreated                     #kg per year
n2o_tot_untreated = n2o_untreated_field + n2o_untreated                     #kg per year
n_fertilizer_untreated = n_tot - n_lost_untreated
p_fertilizer_untreated = p_tot
k_fertilizer_untreated = k_tot
co2_eq_mineral_fertilizer_untreated = env.co2_mineral_nitrate(n_fertilizer_untreated) + env.co2_mineral_k(k_fertilizer_untreated) + env.co2_mineral_P(p_fertilizer_untreated)

co2_eq_untreated = env.co2_n2o(n2o_tot_untreated) + env.co2_methane(ch4_untreated)












#######################################################################################################################
#print data as a table
#######################################################################################################################

# round the values to 2 digits after the comma
nh3_tot_AD = round(nh3_tot_AD, 2)
n2o_tot_AD = round(n2o_tot_AD, 2)
ch4_AD = round(ch4_released_AD, 2)
heat_AD = round(heat_net_AD * 1000, 2)                    #convert to kW then round
electricity_AD = round(electricity_chp_AD * 1000, 2)      #convert to kW then round
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

# create the table
table = PrettyTable()
table.field_names = ["Data", "Anaerobic Digestion", "No Treatment"]
table.add_row(["Net Heat generated [kW]", heat_AD, heat_untreated])
table.add_row(["Electricity generated [kW]", electricity_AD, electricity_untreated])
table.add_row(["N fertilizer [kg N]", n_fertilizer_AD, n_fertilizer_untreated])
table.add_row(["P fertilizer [kg P]", p_fertilizer_AD, p_fertilizer_untreated])
table.add_row(["K fertilizer [kg K]", k_fertilizer_AD, k_fertilizer_untreated])
table.add_row(["NH3 emitted [kg NH3]", nh3_tot_AD, nh3_tot_untreated])
table.add_row(["N2O emitted [kg N2O]", n2o_tot_AD, n2o_tot_untreated])
table.add_row(["CH4 emitted [kg CH4]", ch4_AD, ch4_untreated])
table.add_row(["CO2 equivalent [kg CO2]", co2_eq_AD, co2_eq_untreated])
table.add_row(["CO2 eq. from replaced mineral fertilizer [kg CO2]", co2_eq_mineral_fertilizer_AD, co2_eq_mineral_fertilizer_untreated])

# print the table
print(table)
