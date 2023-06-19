#################################################################
#Environmental impacts
################################################################

# assume good practice and otpimal fertilizer usage
# a certain percentage of plant accessible fertilizer is going to be used by plants, the rest is washed out etc
# STILL NEED TO FIND SOURCE!! for now assume 90% is used by plants

n_fertilizer_efficiency = 0.9
n_fertilizer_lost = 0.1

def n_fertilizer_lost_post_application(n_fert):
    return n_fertilizer_lost * n_fert

################################################################
#CO2 equivalent

def co2_methane(methane):
    factor = 84         #1 kg of CH4 is equivalent to 84 kg of CO2
    return methane * factor


def co2_n2o(n2o):
    factor = 298  # 1 kg of N2O is equivalent to 298 kg of CO2
    return n2o * factor


#def co2_nh3(nh3):
 #   factor = 84  # 1 kg of CH4 is equivalent to 84 kg of CO2
  #  return methane * factor


#mineral fertilizers


def co2_mineral_nitrate(mineral_n):   #input in kg mineral nitrate fertilizer
    factor = 0.4
    return factor * mineral_n   #output in kg CO2 eq


def co2_mineral_n(mineral_n):           #input in kg mineral nitrogen fertilizer
    factor = 2.2
    return factor * mineral_n           #output in kg CO2 eq


def co2_mineral_P(mineral_p):   #input in kg mineral P fertilizer
    factor = 0.5
    return factor * mineral_p   #output in kg CO2 eq


def co2_mineral_k(mineral_k):   #input in kg mineral K
    factor = 0.4
    return factor * mineral_k   #output in kg CO2 eq


################################################################
#Transportation
################################################################

fuel_consumption_tractor = 0.48     #[l/kg] assume tractors use diesel
co2_diesel = 2.620                   #[g/l] in kg CO2 per liter of diesel


def fuel_consumption_transport(manure_volume, distance): #input manure volume in m3 (assumption 1000kg/m3) and distance in km
    num_trips = (manure_volume / 10) * 2          # assumption of using tractors with a slurry tank that can hold 10t of manure. Every manure transport includes 1 empty trip back!
    fuel_per_trip = distance * fuel_consumption_tractor     #[l] in liter diesel
    return num_trips * fuel_per_trip


def env_impact_diesel(diesel):  #input in [l] diesel
    return diesel * co2_diesel  #output in kg CO2



###############################################
#swiss UBP
###############################################

ubp_factor_p = 970 *1000     # [UBP/ kg P] for P into surface waters
ubp_factor_nh3 = 44 * 1000    #[UBP/kg NH3]
ubp_factor_co2 = 1000      #[UBP/ kg CO2-eq]
ubp_factor_n = 36 * 1000      #[UBP/ kg N] for n into surface waters
ubp_factor_energy_non_renew = 8.3  #[UBP/MJ Oil-eq]
ubp_factor_energy_renew = 2.8      #[UBP/MJ oil-eq]


def ubp_eutrophication_p(p_to_water):
    return ubp_factor_p * p_to_water


def ubp_eutrophication_n(n_to_water):
    return ubp_factor_n * n_to_water


def ubp_nh3(nh3_emission):
    return ubp_factor_nh3 * nh3_emission


def ubp_co2_eq(co2_eq):
    return ubp_factor_co2 * co2_eq


def ubp_energy_non_renew(energy_non_renew):
    return energy_non_renew * ubp_factor_energy_non_renew


def ubp_energy_renew(energy_renew):
    return energy_renew * ubp_factor_energy_renew







########################################
#Acidification potential
########################################

acid_factor_nh3 = 1.88      #SO2-eq.


def acidification_nh3(nh3_emission):
    return nh3_emission * acid_factor_nh3



###########################################
# GHG impact electricity mix Switzerland

co2_el_produktion = 29.6     # gCO2/kWh, Produktionsstrommix
co2_el_lieferant = 54.7     # g CO2 / kWh, Lieferantenstrommix
co2_el_verbraucher = 128    # g CO2 / kWh, Verbraucherstrommix

def co2_swiss_el_mix(el_generated):
    return co2_el_lieferant * el_generated         #input in kWh, output in g CO2