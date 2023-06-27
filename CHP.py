#Calculations in regards to Co-Heat_Power generators

efficiency_heat = 0.5
efficiency_el = 0.4
tvm = 36        #thermal value methane [MJ/m3]
s_in_y = 31536000 * 0.85  # seconds in a year, assuming operating 85% of the time
h_in_y = s_in_y / 60
density_co2 = 1.964  #kg / m3 0° C 1 atm
density_ch4 = 0.717 #kg / m3 0°C 1 atm
molar_h = 1             #g/mol
molar_c = 12            #g/mol
molar_o = 16            #g/mol
molar_ch4 = molar_c + 4 * molar_h       #g/mol
molar_co2 = molar_c + 2 * molar_o       #g/mol
molar_ratio_co2_ch4 = molar_co2 / molar_ch4


efficiency_el_sofc = 0.7    # electrical efficiency of solid oxide fuel cells
def energy_produced(eff_methane):       #in kWh
    heat = eff_methane * tvm / s_in_y * h_in_y * efficiency_heat * 1000
    electricity = eff_methane * tvm / s_in_y * h_in_y * efficiency_el * 1000
    return heat, electricity

def co2_release(co2, ch4):              #input in m3 output in kg
    co2_mass = co2 * density_co2
    ch4_mass = ch4 * density_ch4
    co2_released = co2_mass + ch4_mass * molar_ratio_co2_ch4
    return co2_released


def el_produced_sofc(biogas_methane):
    electricity = biogas_methane * tvm / s_in_y * h_in_y * efficiency_el_sofc * 1000
    return electricity
