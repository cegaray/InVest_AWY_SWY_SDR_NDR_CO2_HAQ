import os
import spotpy
import numpy as np
import pandas as pd
from natcap.invest.hydropower import hydropower_water_yield as awy
from IS_Member import ismember
from simpledbf import Dbf5

class spotpy_setup(object):
    def __init__(self):
        # Parameters
        self.params = [spotpy.parameter.Uniform('Z',1,100),
                       spotpy.parameter.Uniform('Factor-Kc',0.9, 1.23),
                       ]
        # Folders
        self.PathProject = r'C:\Users\TNC\Videos\03-InVEST'

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self, vector):
        simulation = np.array(vector)
        return simulation

    def evaluation(self):
        PathProject     = self.PathProject
        NameFile        = os.path.join(PathProject,'INPUTS','Observed.csv')
        observations    = pd.read_csv(NameFile)

        return observations

    def objectivefunction(self, simulation, evaluation):

        # Parameters
        x = simulation

        # --------------------------------------------------------------------------------------------------------------
        # Paths
        # --------------------------------------------------------------------------------------------------------------
        PathProject = self.PathProject

        # --------------------------------------------------------------------------------------------------------------
        # Print
        # --------------------------------------------------------------------------------------------------------------
        print('Parameters - AWY')
        print('---------------------------')
        print('Z  = ' + '%.2f' % x[0])
        print('Factor-Kc = ' + '%.2f' % x[1])

        # --------------------------------------------------------------------------------------------------------------
        # Read Biophycial Table
        # --------------------------------------------------------------------------------------------------------------
        Tmp         = os.path.join(PathProject, 'INPUTS', 'Biophysical_Table.csv')
        Table       = pd.read_csv(Tmp)

        # --------------------------------------------------------------------------------------------------------------
        # Afectacion de parametros Kc en la tabla biofisica
        # --------------------------------------------------------------------------------------------------------------
        # Aplica el factor multiplicador a los valores de carga y redondea a 3 decimales
        Raw_Kc      = Table['Kc']
        Values      = round(Table['Kc']*x[1],3)
        # Asigna valores de Kc de 1 a las coberturas de ICE and WATER
        Values[27:36]   = Raw_Kc[27:36]
        # Asigna valor de 0.1 a la cobertura de URBAN
        Values[0:8]     = Raw_Kc[0:8]
        # Si el factor hace que el Kc sea mayor que 1.2, limita el valor a 1.2
        Values[Values >= 1.2] = 1.2
        # Asigna los valores de Kc modificados a la tabla
        Table['Kc'] = Values

        # --------------------------------------------------------------------------------------------------------------
        # Guardar Table Biofisica temporal
        # --------------------------------------------------------------------------------------------------------------
        PathTable = os.path.join(PathProject, 'TMP', 'Biophysical_Table.csv')
        Table.to_csv(PathTable,index=False)

        # --------------------------------------------------------------------------------------------------------------
        # # Parametros de entrada del modelo
        # --------------------------------------------------------------------------------------------------------------
        # Ruta de la tabla biofisica temporal de la region
        BioTable    = PathTable
        # Ruta del raster de coberturas de la region
        LULC        = os.path.join(PathProject, 'INPUTS', 'LULC.tif')
        # Ruta de Agua disponible para las plantas
        PAW         = os.path.join(PathProject, 'INPUTS', 'PAW.tif')
        # Ruta del raster de precipitacion media anual multianual
        Pcp_Annual  = os.path.join(PathProject, 'INPUTS', 'PT', 'PT_4_13.tif')
        # Ruta del raster de profundidad del suelo
        Soil_Depth  = os.path.join(PathProject, 'INPUTS', 'SoilDepth.tif')
        # Ruta del raster de evapotranspiracion media anual multianual
        ETo_Annual  = os.path.join(PathProject, 'INPUTS','ETo', 'ETo_13.tif')
        # Ruta de la cuenca de la Region
        SubWatershed= os.path.join(PathProject, 'INPUTS', 'Basin','Basin_Cal.shp')
        # Ruta de la cuenca de la Region
        Watershed   = os.path.join(PathProject, 'INPUTS', 'Basin','Basin_Cal.shp')
        # Ruta de la carpeta de resultados de la region
        Results     = os.path.join(PathProject, 'OUTPUTS', '01-AWY')

        # --------------------------------------------------------------------------------------------------------------
        # Configuracion de diccionario de entrada del modelo
        # --------------------------------------------------------------------------------------------------------------
        args = {}
        args['biophysical_table_path']          = BioTable
        args['lulc_path']                       = LULC
        args['depth_to_root_rest_layer_path']   = Soil_Depth
        args['do_scarcity_and_valuation']       = False
        args['eto_path']                        = ETo_Annual
        args['pawc_path']                       = PAW
        args['precipitation_path']              = Pcp_Annual
        args['results_suffix']                  = ''
        args['sub_watersheds_path']             = SubWatershed
        args['watersheds_path']                 = Watershed
        args['workspace_dir']                   = Results
        args['seasonality_constant']            = '%0.2f' % x[0]

        # --------------------------------------------------------------------------------------------------------------
        # Ejecución del modelo
        # --------------------------------------------------------------------------------------------------------------
        awy.execute(args)

        # --------------------------------------------------------------------------------------------------------------
        # Lectura del csv de resultados
        # --------------------------------------------------------------------------------------------------------------
        NameFile    = os.path.join( Results , 'output','watershed_results_wyield.csv')
        simulation  = pd.read_csv(NameFile)
        Sim         = simulation['wyield_vol'].values

        # --------------------------------------------------------------------------------------------------------------
        # Busca los datos de rendimiento hidrico en la tabla de resultados asociados a cada cuenca
        # --------------------------------------------------------------------------------------------------------------
        [I, idx]    = ismember(simulation['ws_id'].values, evaluation['ID'].values)
        Obs         = evaluation['AWY'].values[idx]

        # --------------------------------------------------------------------------------------------------------------
        # Calcula la metrica de RMSE
        # --------------------------------------------------------------------------------------------------------------
        objectivefunction = spotpy.objectivefunctions.rmse(Obs, Sim)

        # --------------------------------------------------------------------------------------------------------------
        # Guarda el valor de la metrica en el CSV Metric
        # --------------------------------------------------------------------------------------------------------------
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '01-AWY', 'Metric.csv')
        ID_File = open(PathRestuls, 'a')
        ID_File.write('%0.2f' % x[0] + ',' + '%0.3f' % x[1] + ',' + '%.2f' % objectivefunction + '\n')
        ID_File.close()

        # --------------------------------------------------------------------------------------------------------------
        # Guarda el valor observado en el CSV Obs
        # --------------------------------------------------------------------------------------------------------------
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '01-AWY', 'Obs.csv')
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
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '01-AWY', 'Sim.csv')
        ID_File = open(PathRestuls, 'a')
        for ii in range(0,len(Sim)):
            ID_File.write('%0.2f' % Sim[ii] + '\n')
        ID_File.close()

        # --------------------------------------------------------------------------------------------------------------
        # Salida de la funcion
        # --------------------------------------------------------------------------------------------------------------
        return objectivefunction
