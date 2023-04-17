#################################################################
#Environmental impacts
################################################################


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