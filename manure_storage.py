#modeling the storage of the manure, loss of nutrients and CH4 released

storage = 0         #days manure is stored before used


#######################################################
# some literature values
#######################################################

# molar weights and ratios
molar_h = 1             #g/mol
molar_c = 12            #g/mol
molar_o = 16            #g/mol
molar_n = 14            #g/mol
rho_methane = 0.717     #density of methane at standard conditions [kg/Nm3] 0°C, 1 atm
molar_ch4 = molar_c + 4 * molar_h       #g/mol
molar_n2o = 2 * molar_n + molar_o       #g/mol
molar_nh3 = molar_n + 3 * molar_h       #g/mol
molar_ratio_ch4_c = molar_c / molar_ch4   #molar ratio of carbon and methane to calculate the carbon mass
molar_ratio_n_n2o = molar_n / molar_n2o
molar_ratio_n_nh3 = molar_n / molar_nh3




# emission values, austrian Study, 2006
t_standard = 80     #values are for storage of manure for 80 days
ch4_emissions_net_storage_untreated = 4045   #g CH4 per m3
ch4_emissions_net_storage_AD = 1342        #g CH4 per m3
nh3_emissions_net_storage_untreated = 41   #g NH3 per m3
nh3_emissions_net_storage_AD = 9.9         #g NH3 per m3
ch4_emissions_net_field_untreated = 0       #g CH4 per m3
ch4_emissions_net_field_AD = 0        #g CH4 per m3
nh3_emissions_net_field_untreated = 186   #g NH3 per m3
nh3_emissions_net_field_AD = 220         #g NH3 per m3
n2o_emissions_net_storage_untreated = 20    #g N2O per m3
n2o_emissions_net_field_untreated = 4       #g N2O per m3
n2o_emissions_net_storage_AD = 2.9         #g N2O per m3 (original value from austrian study: 28,5 ; new value of 2,9 is from swiss study and seems more realistic)
n2o_emissions_net_field_AD = 2.7            #g N2O per m3


n_start_untreated = 3.96                    #g N / kg manure
n_end_untreated = 3.25                      #g N / kg manure
c_start_untreated = 35.36                   #g C / kg manure
c_end_untreated = 20.05                     #g C / kg manure
n_start_AD = 3.17                           #g N / kg manure
n_end_AD = 2.48                             #g N / kg manure
c_start_AD = 20.38                          #g C / kg manure
c_end_AD = 13.28                            #g C / kg manure

"""
n_lost_untreated = 1 - (n_end_untreated / n_start_untreated)
c_lost_untreated = 1 - (c_end_untreated / c_start_untreated)
n_lost_AD = 1 - (n_end_AD / n_start_AD)
c_lost_AD = 1 - (c_end_AD / c_start_AD)
"""
# what percentage of N and C is lost everyday of storage
"""
n_lost_daily_untreated = 1 - (n_end_untreated / n_start_untreated) ** (1/t_standard)
c_lost_daily_untreated = 1 - (c_end_untreated / c_start_untreated) ** (1/t_standard)
n_lost_daily_AD = 1 - (n_end_AD / n_start_AD) ** (1/t_standard)
c_lost_daily_AD = 1 - (c_end_AD / c_start_AD) ** (1/t_standard)
"""
ch4_emission_factor_storage_untreated_c = (ch4_emissions_net_storage_untreated * molar_ratio_ch4_c) / (c_start_untreated * 1000)
ch4_emission_factor_storage_ad_c = (ch4_emissions_net_storage_AD * molar_ratio_ch4_c) / (c_start_AD * 1000)
ch4_emission_factor_storage_untreated_daily = 1 - (1 - ch4_emission_factor_storage_untreated_c) ** (1 / t_standard)
ch4_emission_factor_storage_ad_daily = 1 - (1 - ch4_emission_factor_storage_ad_c) ** (1 / t_standard)


# what percentage of the lost N is emitted as N2O and what percentage is NH3
n2o_emissions_net_storage_untreated_N = n2o_emissions_net_storage_untreated * molar_ratio_n_n2o     # emissions in g N instead of g N2O
nh3_emissions_net_storage_untreated_N = nh3_emissions_net_storage_untreated * molar_ratio_n_nh3     # emissions in g N
n2o_emissions_net_storage_AD_N = n2o_emissions_net_storage_AD * molar_ratio_n_n2o                   # emissions in g N
nh3_emissions_net_storage_AD_N = nh3_emissions_net_storage_AD * molar_ratio_n_nh3                   # emissions in g N

#NH3 and N2O lost in percentage of total N, assuming density of 1000 kg / m3 of manure/slurry
#n2o_emissions_factor_storage_untreated_N = n2o_emissions_net_storage_untreated_N / n_start_untreated
#nh3_emissions_factor_storage_untreated_N = nh3_emissions_net_storage_untreated_N / n_start_untreated
n2o_emissions_factor_storage_AD_N = n2o_emissions_net_storage_AD_N / (n_start_AD * 1000)
nh3_emissions_factor_storage_AD_N = nh3_emissions_net_storage_AD_N / (n_start_AD * 1000)

emission_factor_nh3_storage_ad_daily = 1 - (1 - nh3_emissions_factor_storage_AD_N) ** (1 / t_standard)
emission_factor_n2o_storage_ad_daily = 1 - (1 - n2o_emissions_factor_storage_AD_N) ** (1 / t_standard)

#######################################
n2o_ratio_storage_untreated = n2o_emissions_net_storage_untreated_N / (n2o_emissions_net_storage_untreated_N + nh3_emissions_net_storage_untreated_N)
nh3_ratio_storage_untreated = 1 - n2o_ratio_storage_untreated
n2o_ratio_storage_AD = n2o_emissions_net_storage_AD_N / (n2o_emissions_net_storage_AD_N + nh3_emissions_net_storage_AD_N)
nh3_ratio_storage_AD = 1 - n2o_ratio_storage_AD
########################################

# carbon percentage made into methane
c_start = 35.36
c_end = 20.38

c_to_methane = c_start-c_end
c_to_methane_percent = c_to_methane / c_start

########################################################
#Emissions according to Swiss studies, Stoffflüsse landwirtschaftliche Biogasproduktion und Ökobilanz, Carbotec AG
########################################################
t_storage_standard = 90             #days of storage used in data
emission_factor_storage_nh3 = 0.0135        #1,35% of total N is emitted as NH3 for covered storage (13,5% for uncovered, but we assume all storage will be covered in the future/when this tool applies)
emission_factor_storage_n2o = 0.005         #0.5% of (total N - NH3 emission) is emitted as N2O

emission_factor_nh3_storage_untreated_daily = 1 - (1 - emission_factor_storage_nh3) ** (1 / t_storage_standard)
emission_factor_n2o_storage_untreated_daily = 1 - (1 - emission_factor_storage_n2o) ** (1 / t_storage_standard)


max_ch4_left_digestate = 164    # g CH4 / m3, assume half of this is released in post storage
ch4_released_post_storage = max_ch4_left_digestate / 2  #ch4 released in post storage of digestate, only half of the max because the assumption is the rest is covered, so no methane can be emitted
########################################################
# functions, assuming the literature values can be taken as is
########################################################


def storage_input():
    storage_time = int(input("How many days on average is the manure or digestate stored before used?"))
    return storage_time


def c_total(theoretical_methane):                       #input methane in norm m3
    methane_mass = rho_methane * theoretical_methane
    mass_c = methane_mass * molar_ratio_ch4_c
    return mass_c / c_to_methane_percent          #output in kg C


def n_to_nh3(n_nh3):
    return n_nh3 / molar_ratio_n_nh3


def n_to_n2o(n_n2o):
    return n_n2o / molar_ratio_n_n2o


def c_to_ch4(carbon):
    return carbon / molar_ratio_ch4_c


def ch4_volume_to_mass(methane_volume):     #input methane in m3 output methane in kg CH4
    return methane_volume * rho_methane


def ch4_mass_to_volume(methane_mass):
    return methane_mass / rho_methane


def ch4_to_c(methane):                      #input methane in kg CH4 output in kg C
    return methane * molar_ratio_ch4_c


def ch4_release_untreated(c_tot, storage_time):      #function to calculate the CH4 released during storage, for now assume all manure has density of 1kg/l same as water
    if storage_time == 0 or c_tot <= 0:
        return 0
    else:
        c_lost = c_tot * ch4_emission_factor_storage_untreated_daily
        c_new = c_tot - c_lost
        storage_time -= 1
        ch4_released = c_lost / molar_ratio_ch4_c
        return ch4_released + ch4_release_untreated(c_new, storage_time)      #carbon released in kg CH4


def ch4_release_AD(c_tot, storage_time):  # function to calculate the CH4 released during storage after AD, c_tot is how much carbon is left in the digestate (C_tot - methane_yield)
    if storage_time == 0 or c_tot <= 0:
        return 0
    else:
        c_lost = c_tot * ch4_emission_factor_storage_ad_daily   #c_tot in kg C
        c_new = c_tot - c_lost
        storage_time -= 1
        ch4_released = c_lost / molar_ratio_ch4_c
        return ch4_released + ch4_release_AD(c_new, storage_time)       #carbon released in kg CH4

"""
def N_reduction_untreated(N_tot, storage_time):  #function to calculate the N-loss during storage, input N_tot in kg N
    if storage_time == 0 or N_tot <= 0:
        return 0
    else:
        N_lost = N_tot * n_lost_daily_untreated
        N_new = N_tot - N_lost
        storage_time -= 1
        return N_lost + N_reduction_untreated(N_new, storage_time)          #nitrogen released in kg N


def N_reduction_AD(N_tot, storage_time):  #function to calculate the N-loss during storage, input in kg N
    if storage_time == 0 or N_tot <= 0:
        return 0
    else:
        N_lost = N_tot * n_lost_daily_AD
        N_new = N_tot - N_lost
        storage_time -= 1
        return N_lost + N_reduction_AD(N_new, storage_time)             #nitrogen released in kg N
"""

def nh3_storage_untreated(n_tot, storage_time):                             #input in kg N
    if storage_time == 0 or n_tot <= 0:
        return 0
    else:
        nh3_emitted = n_tot * emission_factor_nh3_storage_untreated_daily
        n_new = n_tot - nh3_emitted
        storage_time -= 1
        return nh3_emitted + nh3_storage_untreated(n_new, storage_time)         #output NH3 in kg N


def n2o_storage_untreated(n_tot, storage_time):                     #input in kg N
    if storage_time == 0 or n_tot <= 0:
        return 0
    else:
        n2o_emitted = n_tot * emission_factor_n2o_storage_untreated_daily
        n_new = n_tot - n2o_emitted
        storage_time -= 1
        return n2o_emitted + nh3_storage_untreated(n_new, storage_time)     #output N2O in kg N


def nh3_storage_ad(n_tot, storage_time):
    if storage_time == 0 or n_tot <= 0:
        return 0
    else:
        nh3_emitted = n_tot * emission_factor_nh3_storage_ad_daily
        n_new = n_tot - nh3_emitted
        storage_time -= 1
        return nh3_emitted + nh3_storage_ad(n_new, storage_time)  # output NH3 in kg N


def n2o_storage_ad(n_tot, storage_time):
    if storage_time == 0 or n_tot <= 0:
        return 0
    else:
        n2o_emitted = n_tot * emission_factor_n2o_storage_ad_daily
        n_new = n_tot - n2o_emitted
        storage_time -= 1
        return n2o_emitted + n2o_storage_ad(n_new, storage_time)  # output N2O in kg N

""""
def NH3_vs_N2O_untreated(n_lost):   #input in kg N
    nh3 = n_lost * nh3_ratio_storage_untreated / molar_ratio_n_nh3      #NH3 in kg NH3
    n2o = n_lost * n2o_ratio_storage_untreated / molar_ratio_n_n2o      #N2O in kg N2O

    return nh3, n2o


def NH3_vs_N2O_AD(n_lost):      #input in kg N
    nh3 = n_lost * nh3_ratio_storage_AD / molar_ratio_n_nh3     #kg NH3
    n2o = n_lost * n2o_ratio_storage_AD / molar_ratio_n_n2o     #kg N2O

    return nh3, n2o


"""

#Field application

factor_n_acc_manure = 0.467     #percentage of nitrogen that is accessible for plants in the case of manure
factor_n_acc_ad = 0.513  #percentage of nitrogen that is accessible for plants in the case of digestate
nh3_factor_emission_field = 0.5     #percentage of accessible nitrogen that is emitted on field application as NH3
factor_schleppschlauch = 0.75    #reduction in NH3 emissions when using Schleppschlauch or similar tools (assume it's always used, since it's going to be mandatory in switzerland)
nh3_factor_emission_field_new = nh3_factor_emission_field * factor_schleppschlauch
n2o_emission_field = 0.1        #Nitrogen emitted as N2O, in percent of (total nitrogen - NH3 emission)


def n_acc_manure(n_tot):
    return factor_n_acc_manure * n_tot      # input n_tot in kg N, output n_acc in kg N


def n_acc_ad(n_tot):
    return factor_n_acc_ad * n_tot      # input n_tot in kg N, output n_acc in kg N


def nh3_field(n_acc):
    return nh3_factor_emission_field_new * n_acc         #in kg N


def n2o_field(n_acc):
    return n2o_emission_field * n_acc        #in kg N


def P_reduction(P_tot):     #function to calculate the P-loss during storage
    pass


def K_reduction(K_tot):     #function to calculate the K-loss during storage
    pass


