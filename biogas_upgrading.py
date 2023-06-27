






biogas_ch4 = 0.6                # %
biogas_co2 = 0.4                # %

upgrade_percentage_biogas = 0.7     # how many percent of biogas are upgraded
chp_biogas_flow_percentage = 0.3    # how much raw biogas goes into chp

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

def biogas_upgraded(biogas):
    return upgrade_percentage_biogas * biogas

def biogas_chp(biogas):
    return chp_biogas_flow_percentage * biogas

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










###############################
# 3 stage upgrading, source: Biowaste-to-biomethane or biowaste-to-energy? An LCA study on
# anaerobic digestion of organic waste
#######################################

electricity_biogas_upgrade_3_stage = 0.29       # kWh / m3 raw biogas
co2_removal_3_stage = 0.98                        # %
ch4_slip_3_stage = 0.0069                         # %
offgas_ch4_3_stage = 0.0079                       # %
offgas_co2_3_stage = 0.9894                      # %
biomethane_ch4_3_stage = 0.9747                  # %
biomethane_co2_3_stage = 0.0172                   # %
biomethane_ch4_co2_ratio_3_stage = biomethane_ch4_3_stage / biomethane_co2_3_stage


def offgas_volume_3_stage(biogas):
    return biogas * ((biogas_ch4 - biogas_ch4 * ch4_slip_3_stage - biomethane_ch4_co2_ratio_3_stage * biogas_co2) / (offgas_ch4_3_stage - biomethane_ch4_co2_ratio_3_stage * offgas_co2_3_stage))


def biomethane_volume_3_stage(biogas):
    offgas = offgas_volume_3_stage(biogas)
    return (biogas_co2 * biogas - offgas_co2_3_stage * offgas) / biomethane_co2_3_stage


def ch4_slippage_3_stage(biogas):
    return biogas_ch4 * ch4_slip_3_stage * biogas


def co2_offgas_3_stage(biogas):
    return offgas_co2_3_stage * offgas_volume_3_stage(biogas)


def ch4_offgas_3_stage(biogas):
    return offgas_ch4_3_stage * offgas_volume_3_stage(biogas)


def co2_biomethane_3_stage(biogas):
    return biomethane_co2_3_stage * biomethane_volume_3_stage(biogas)


def ch4_biomethane_3_stage(biogas):
    return biomethane_ch4_3_stage * biomethane_volume_3_stage(biogas)


def energy_use_3_stage(biogas):                             # input in m3, output in kWh
    return biogas * electricity_biogas_upgrade_3_stage


def ch4_biogas(biogas):
    return biogas_ch4 * biogas


def co2_biogas(biogas):
    return biogas_co2 * biogas