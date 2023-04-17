
#effective methane yields from anaerobic digestion using the theoretical yields from the Animal_Class and 3 different size categories for the AD plant

import Animal_Class as AC

tvm = 36  # thermal value methane in [kJ/l]
s_in_y = 31536000  # seconds in a year
methane_BG = 0.6 #methane content in produced Biogas
CO2_BG = 0.4 #CO2 content in produced Biogas
ch4_loss = 0.02 #percentage of CH4 lost during AD
def methane_yield_eff_small(BMP):
    AD_eff = 0.8        #efficiency of the AD plant. What percentage of the Biomethane potential (BMP) can actually be achieved
    return AD_eff * BMP


def methane_yield_eff_medium(BMP):
    AD_eff = 0.85        #efficiency of the AD plant. What percentage of the Biomethane potential (BMP) can actually be achieved
    return AD_eff * BMP

def methane_yield_eff_large(BMP):
    AD_eff = 0.9        #efficiency of the AD plant. What percentage of the Biomethane potential (BMP) can actually be achieved
    return AD_eff * BMP

#Size 0 is small, size 1 is medium and size 2 is large
def plant_size(BMP): #input is total methane in liter per year

    efficiency = 0.8    #assumption of methane yield effificency, lower end as a safety net
    power = BMP * tvm * efficiency / s_in_y
    if power <= 30:
        return 0
    elif (power > 30) & (power <= 150):
        return 1
    else:
        return 2

def methane_yield(BMP):
    size = plant_size(BMP)
    if size == 0:
        return methane_yield_eff_small(BMP)
    elif size == 1:
        return methane_yield_eff_medium(BMP)
    else:
        return methane_yield_eff_large(BMP)

def biogas(methane_yield):
    biogas = methane_yield/methane_BG
    co2 = biogas*CO2_BG
    return biogas, co2


def methane_loss(methane_yield):
    return methane_yield * ch4_loss

#heat demand to heat up the manure to operating temperature, assuming it's mostly water and therefore using heat capacity of water, input manure amount in kg per year, return average energy consumption in [kW].
def heat_demand(manure_tot):
    t_0 = 10     #starting temperature in °C
    t_1 = 37    #end temperature in °C for mesophilic AD
    C = 4184    #specific heat capacity of Water in [J/kg/K]
    return C * (t_1 - t_0) * manure_tot / s_in_y / 1000             #in kW

