import os
import spotpy
import numpy as np
import pandas as pd
from simpledbf import Dbf5
from natcap.invest.seasonal_water_yield import seasonal_water_yield as swy
import rasterio
from IS_Member import ismember

class spotpy_setup(object):
    def __init__(self):
        self.params = [spotpy.parameter.Uniform('Gamma', 0.01, 1.0),
                       ]
        # Folders
        self.PathProject = r'D:\TARULLA Dropbox\P17-InVEST\03-Productos_Intermedios\03-InVEST'

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self, vector):
        simulation = np.array(vector)
        return simulation

    def evaluation(self):
        PathProject     = self.PathProject
        NameFile        = os.path.join(PathProject, 'INPUTS', 'Observed.csv')
        observations    = pd.read_csv(NameFile)

        return observations

    def objectivefunction(self, simulation, evaluation):
        # ---------------------------------------------------------------------
        # Parameters
        # ---------------------------------------------------------------------
        x1 = simulation
        #x  = [1.0/100.0, x1]
        x = [1.0 / 10.0, 0.8]

        # --------------------------------------------------------------------------------------------------------------
        # Paths
        # --------------------------------------------------------------------------------------------------------------
        PathProject = self.PathProject

        # ---------------------------------------------------------------------
        # Print
        # ---------------------------------------------------------------------
        print('---------------------------')
        print('Alpha = ' + '%.2f' % x[0])
        print('Gamma = ' + '%.2f' % x[1])

        # ---------------------------------------------------------------------
        # Parametros de entrada del modelo
        # ---------------------------------------------------------------------
        # Ruta del raster de coberturas de la region
        LULC        = os.path.join(PathProject, 'INPUTS', 'LULC.tif')
        # Ruta del DEM de la region
        DEM         = os.path.join(PathProject, 'INPUTS', 'DEM_90m.tif')
        # Ruta de la tabla biofisica de la region
        BioTable    = os.path.join(PathProject, 'INPUTS', 'Biophysical_Table.csv')
        # Ruta de la tabla de eventos de lluvia de la region
        RainTable   = os.path.join(PathProject, 'INPUTS', 'Rainfall_Day_Table.csv')
        # Ruta del grupo de suelos
        SoilGroup   = os.path.join(PathProject, 'INPUTS', 'SoilGroups.tif')
        # Ruta de la carpeta de precipitaciones
        Pcp_Montly  = os.path.join(PathProject, 'INPUTS', 'PT')
        # Ruta de la carpeta de evapotrasnpiración
        ETP_Montly  = os.path.join(PathProject, 'INPUTS', 'ETo')
        # Ruta de la cuenca de la Region
        Watershed   = os.path.join(PathProject, 'INPUTS', 'Basin', 'Basin_Cal_SZH.shp')
        # Ruta de la carpeta de resultados de la region
        Results     = os.path.join(PathProject, 'OUTPUTS', '02-SWY')

        # --------------------------------------------------------------------------------------------------------------
        # Configuracion de diccionario de entrada del modelo
        # --------------------------------------------------------------------------------------------------------------
        args = {}
        Suffix                                  = ''
        args['results_suffix']                  = Suffix
        args['biophysical_table_path']          = BioTable
        args['rain_events_table_path']          = RainTable
        args['lulc_raster_path']                = LULC
        args['dem_raster_path']                 = DEM
        args['aoi_path']                        = Watershed
        args['et0_dir']                         = ETP_Montly
        args['precip_dir']                      = Pcp_Montly
        args['soil_group_path']                 = SoilGroup
        args['workspace_dir']                   = Results
        args['monthly_alpha']                   = False
        args['user_defined_climate_zones']      = False
        args['user_defined_local_recharge']     = False
        args['threshold_flow_accumulation']     = '1000'
        args['alpha_m']                         = '%.3f' % x[0]
        args['beta_i']                          = '1.0'
        args['gamma']                           = '%.3f' % x[1]

        # --------------------------------------------------------------------------------------------------------------
        # Ejecución del modelo
        # --------------------------------------------------------------------------------------------------------------
        swy.execute(args)

        # ---------------------------------------------------------------------
        # Lectura del dbf de resultados
        # ---------------------------------------------------------------------
        NameFile    = os.path.join(Results, 'aggregated_results_swy.dbf')
        dbf         = Dbf5(NameFile)
        simulation  = dbf.to_dataframe()

        # ---------------------------------------------------------------------
        # Busca los datos de carga de sedimentos en la tabla de resultados asociados a cada cuenca
        # ---------------------------------------------------------------------
        Obs         = simulation['AET_mn'].values

        # ---------------------------------------------------------------------
        ## read Results
        # ---------------------------------------------------------------------
        NameFile = os.path.join(Results, 'intermediate_outputs', 'aet.tif')
        Sim = rasterio.open(NameFile)
        Sim = Sim.read(1)
        Sim = np.array([np.mean(Sim[Sim >= 0])])

        print('Obs =' + str(Obs) + ' - Sim =' + str(Sim))

        # ---------------------------------------------------------------------
        # Guarda el valor de la metrica en el CSV Metr
        # ---------------------------------------------------------------------
        #objectivefunction = spotpy.objectivefunctions.rmse(int(Obs), int(Sim))
        objectivefunction = np.abs(Obs - Sim)

        # --------------------------------------------------------------------------------------------------------------
        # Guarda el valor de la metrica en el CSV Metric
        # --------------------------------------------------------------------------------------------------------------
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '02-SWY', 'Metric.csv')
        ID_File = open(PathRestuls, 'a')
        ID_File.write(
            '%0.2f' % x[0] + ',' + '%0.2f' % x[1] + ',' + '%.2f' % objectivefunction + '\n')
        ID_File.close()

        # --------------------------------------------------------------------------------------------------------------
        # Guarda el valor observado en el CSV Obs
        # --------------------------------------------------------------------------------------------------------------
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '02-SWY', 'Obs.csv')
        if os.path.exists(PathRestuls):
            o = 1
        else:
            ID_File = open(PathRestuls, 'w')
            ID_File.write('Obs\n')
            for ii in range(0, len(Obs)):
                ID_File.write('%0.2f' % Obs[ii] + '\n')
            ID_File.close()

        # --------------------------------------------------------------------------------------------------------------
        # Guarda la simulacion en el archivo CSV Sim
        # --------------------------------------------------------------------------------------------------------------
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '02-SWY', 'Sim.csv')
        ID_File = open(PathRestuls, 'a')
        for ii in range(0, len(Sim)):
            ID_File.write('%0.2f' % Sim[ii] + '\n')
        ID_File.close()

        return objectivefunction