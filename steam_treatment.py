



#########################
# Steam pre treatment of (lignose) solid manure and straw
# according to sources, this can increase methane yield by 10-400%, I'll assume 50% increase, since that seems to be more or less the average for most treatments
# one paper proposes an energy cost of 0.2 - 0.6 MJ/kg of material. This is for a very efficient Method, and on labscale. Milling, a very energy intensive practice
# uses about 4 - 12.5 MJ/kg. So I'll assume 2 MJ/kg for steam treatment, higher than the most efficient, still very new method, but clearly better than Milling.

methane_increase_factor = 1.5
energy_use_steam = 2            # MJ/kg

mj_to_kwh = 0.277

energy_use_steam_kwh = energy_use_steam * mj_to_kwh
def methane_yield_steam(methane_yield):
    return methane_increase_factor * methane_yield

def heat_requirement_steam(manure):
    return manure * energy_use_steam_kwh        #input in kg manure or straw, output in kWh