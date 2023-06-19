







###############################
""""
Source: Membrane biogas upgrading processes for the production of natural gas substitute, Separation and Purification Technology 74 (2010) 83–92
"""
################################


#############################
# Single stage membrane with CHP
#############################
# Offgas is recycled and mixed with unfiltered biogas then used in a CHP to provide heating for the plant and some electricity
# assume selectivity of 35, 70% of biogas is used for upgrading, the rest for mixing with offgas, methane recovery 98%.
# this leads to a methane content in the mixed offgas of 40% and 17% of heating energy of the biogas usable for heating
#assuming initial methane concentration in biogas of 60%

specific_compression_power = 0.3        # kWh / m3 biogas
upgrade_percentage = 0.7                #percentage of biogas that is used for upgrading
methane_content_upgraded = 0.98         #methane content of upgraded biomethane
methane_content_chp = 0.4               #methane content in the mixed biogas with flu gas for the chp
methane_loss = 0.01                     #still needs to be researched, only a preliminary guess
# Methane loss in membrane tba


def biomethane_upgraded(methane):
    methane_upgrade = methane * upgrade_percentage
    methane_lost = methane * methane_loss
    biomethane = methane_upgrade - methane_lost
    return biomethane


def biomethane_total_with_co2(biomethane):
    return biomethane / methane_content_upgraded










################################
# double stage, 2 membranes for higher recovery
#####################################