import os
import pandas as pd
import numpy as np
# Seasonal Water Yield
from natcap.invest.seasonal_water_yield import seasonal_water_yield as swy
# Sediment Delivery Ratio
from natcap.invest.sdr import sdr
# Nutrient Delivery Ratio
from natcap.invest.ndr import ndr
# Anual Water Yield
from natcap.invest.hydropower import hydropower_water_yield as awy
# Carbons
from natcap.invest import carbon


def Run_InVEST(Inputs):

    # ----------------------------------------------------------------------------------------------------------------------
    # Input parameters
    # ----------------------------------------------------------------------------------------------------------------------
    args = {}
    args['biophysical_table_path']          = Inputs['BioTable']
    args['lulc_path']                       = Inputs['LULC']
    args['depth_to_root_rest_layer_path']   = Inputs['Soil_Depth']
    args['do_scarcity_and_valuation']       = False
    args['eto_path']                        = Inputs['ETo_Annual']
    args['pawc_path']                       = Inputs['PAW']
    args['precipitation_path']              = Inputs['Pcp_Annual']
    args['results_suffix']                  = Inputs['Suffix']
    args['seasonality_constant']            = Inputs['z']
    args['sub_watersheds_path']             = ''
    args['watersheds_path']                 = Inputs['Watershed']
    args['alpha_m']                         = Inputs['alpha_m']
    args['aoi_path']                        = Inputs['Watershed']
    args['beta_i']                          = Inputs['beta_i']
    args['dem_raster_path']                 = Inputs['DEM']
    args['et0_dir']                         = Inputs['ETo_Month']
    args['gamma']                           = Inputs['gamma']
    args['lulc_raster_path']                = Inputs['LULC']
    args['monthly_alpha']                   = False
    args['precip_dir']                      = Inputs['Pcp_Month']
    args['rain_events_table_path']          = Inputs['RainfallTable']
    args['soil_group_path']                 = Inputs['Soil_Group']
    args['threshold_flow_accumulation']     = Inputs['Threshold']
    args['user_defined_climate_zones']      = False
    args['user_defined_local_recharge']     = False
    args['dem_path']                        = Inputs['DEM']
    args['drainage_path']                   = ''
    args['erodibility_path']                = Inputs['Erodibility']
    args['erosivity_path']                  = Inputs['Erosivity']
    args['ic_0_param']                      = Inputs['ic_0']
    args['sdr_max']                         = Inputs['sdr_max']
    args['calc_n']                          = True
    args['calc_p']                          = True
    args['runoff_proxy_path']               = Inputs['Proxy']
    args['subsurface_critical_length_n']    = Inputs['sub_C_len_n']
    args['subsurface_critical_length_p']    = Inputs['Sub_C_len_p']
    args['subsurface_eff_n']                = Inputs['Sub_eff_n']
    args['subsurface_eff_p']                = Inputs['Sub_eff_p']
    args['calc_sequestration']              = False
    args['carbon_pools_path']               = Inputs['BioTable']
    args['do_redd']                         = False
    args['do_valuation']                    = False
    args['lulc_cur_path']                   = Inputs['LULC']

    # ----------------------------------------------------------------------------------------------------------------------
    # Anual Water Yield
    # ----------------------------------------------------------------------------------------------------------------------
    args['workspace_dir'] = os.path.join(Inputs['PathResults'], '01-AWY')
    awy.execute(args)

    # ----------------------------------------------------------------------------------------------------------------------
    # Seasonal Water Yield
    # ----------------------------------------------------------------------------------------------------------------------
    args['workspace_dir'] = os.path.join(Inputs['PathResults'], '02-SWY')
    swy.execute(args)

    # ----------------------------------------------------------------------------------------------------------------------
    # Sediment Delivery Ratio
    # ----------------------------------------------------------------------------------------------------------------------
    args['k_param'] = Inputs['k_param_sdr']
    args['workspace_dir'] = os.path.join(Inputs['PathResults'], '03-SDR')
    sdr.execute(args)

    # ----------------------------------------------------------------------------------------------------------------------
    # Nutrient Delivery Ratio
    # ----------------------------------------------------------------------------------------------------------------------
    args['k_param'] = Inputs['k_param_ndr']
    args['workspace_dir'] = os.path.join(Inputs['PathResults'], '04-NDR')
    ndr.execute(args)

    # ----------------------------------------------------------------------------------------------------------------------
    # Carbons
    # ----------------------------------------------------------------------------------------------------------------------
    args['workspace_dir'] = os.path.join(Inputs['PathResults'], '05-CO2')
    carbon.execute(args)


# ----------------------------------------------------------------------------------------------------------------------
# Step-01 InVEST
# ----------------------------------------------------------------------------------------------------------------------
Inputs = {}
Inputs['PathInput']     = r'C:\Users\cesar_garay\Documents\03-InVEST\INPUTS'
Inputs['PathResults']   = r'C:\Users\cesar_garay\Documents\03-InVEST\OUTPUTS\NB1'
Inputs['Pcp_Annual']    = os.path.join(Inputs['PathInput'], 'PT','PT_4_13.tif')
Inputs['Pcp_Month']     = os.path.join(Inputs['PathInput'], 'PT')
Inputs['ETo_Annual']    = os.path.join(Inputs['PathInput'], 'ETo','ETo_13.tif')
Inputs['ETo_Month']     = os.path.join(Inputs['PathInput'], 'ETo')
Inputs['Proxy']         = os.path.join(Inputs['PathInput'], 'Proxy_NDR.tif')
Inputs['LULC']          = os.path.join(Inputs['PathInput'], 'LULC_NBS_1_Positivo.tif')
Inputs['Soil_Group']    = os.path.join(Inputs['PathInput'], 'SoilGroups.tif')
Inputs['Erosivity']     = os.path.join(Inputs['PathInput'], 'R.tif')
Inputs['Erodibility']   = os.path.join(Inputs['PathInput'], 'K.tif')
Inputs['Soil_Depth']    = os.path.join(Inputs['PathInput'], 'SoilDepth.tif')
Inputs['PAW']           = os.path.join(Inputs['PathInput'], 'PAW.tif')
Inputs['DEM']           = os.path.join(Inputs['PathInput'], 'DEM_90m.tif')
Inputs['BioTable']      = os.path.join(Inputs['PathInput'], 'Biophysical_Table.csv')
Inputs['RainfallTable'] = os.path.join(Inputs['PathInput'], 'Rainfall_Day_Table.csv')
Inputs['Watershed']     = os.path.join(Inputs['PathInput'], 'Basin','Basin_Cal_SZH.shp')
Inputs['Suffix']        = ''

# ---------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------
Inputs['z']             = '90.02'
Inputs['alpha_m']       = '0.1'
Inputs['beta_i']        = '1'
Inputs['gamma']         = '0.8'
Inputs['Threshold']     = '1000'
Inputs['ic_0']          = '0.5'
Inputs['sdr_max']       = '0.76'
Inputs['sub_C_len_n']   = '20'
Inputs['Sub_C_len_p']   = '20'
Inputs['Sub_eff_n']     = '0'
Inputs['Sub_eff_p']     = '0'
Inputs['k_param_sdr']   = '3.43'
Inputs['k_param_ndr']   = '2'

# ---------------------------------------------------------------------
# Run InVEST
# ---------------------------------------------------------------------
Run_InVEST(Inputs)