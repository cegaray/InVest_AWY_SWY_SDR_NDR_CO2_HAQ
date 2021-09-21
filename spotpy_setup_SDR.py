import os
import spotpy
import numpy as np
import pandas as pd
from simpledbf import Dbf5
from natcap.invest.sdr import sdr
from IS_Member import ismember

class spotpy_setup(object):
    def __init__(self):
        """
        self.params = [spotpy.parameter.Uniform('sdr_max',  0.5, 0.8),
                       spotpy.parameter.Uniform('Factor-C', 2.0, 3.6),
                       spotpy.parameter.Uniform('Kb', 0.5, 2.0),
                       ]
        """
        self.params = [spotpy.parameter.Uniform('sdr_max', 0.76, 0.76),
                       spotpy.parameter.Uniform('Factor-C', 3.1, 3.6),
                       spotpy.parameter.Uniform('Kb', 1.8, 5.0),
                       ]
        # Folders
        self.PathProject = r'C:\Users\TNC\Videos\03-InVEST'

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self, vector):
        simulation = np.array(vector)
        return simulation

    def evaluation(self):
        PathProject = self.PathProject
        NameFile = os.path.join(PathProject, 'INPUTS', 'Observed.csv')
        observations = pd.read_csv(NameFile)
        return observations

    def objectivefunction(self, simulation, evaluation):
        # Parameters
        x = simulation

        # --------------------------------------------------------------------------------------------------------------
        # Paths
        # --------------------------------------------------------------------------------------------------------------
        PathProject = self.PathProject

        # ---------------------------------------------------------------------
        # Print
        # ---------------------------------------------------------------------
        print('---------------------------')
        print('sdr_max  = ' + '%.2f' % x[0])
        print('Factor-C = ' + '%.2f' % x[1])
        print('Kb       = ' + '%.2f' % x[2])

        # ---------------------------------------------------------------------
        # Read Biophycial Table
        # ---------------------------------------------------------------------
        Tmp    = os.path.join(PathProject, 'INPUTS', 'Biophysical_Table.csv')
        Table  = pd.read_csv(Tmp)

        # ---------------------------------------------------------------------
        # Afectacion de parametro de factor de cobertura en la tabla biofisica
        # ---------------------------------------------------------------------
        Raw_C = Table['usle_c']
        # Aplica el factor multiplicador a los valores del factor C y redondea a 5 decimales
        Values = round(Table['usle_c'] * x[1], 5)
        # Asigna valores de 0 a las coberturas de ICE and WATER
        Values[27:36] = Raw_C[27:36]
        # # Asigna un valor de 1 a las Bare Areas
        Values[0:8]  = Values[0:8]
        # Si el factor hace que el C sea mayor que 1, limita el valor a 1
        Values[Values > 1] = 1
        # Asigna los valores de C modificados a la tabla
        Table['usle_c'] = Values

        # ---------------------------------------------------------------------
        # Guardar Table Biofisica temporal
        # ---------------------------------------------------------------------
        Tmp = os.path.join(PathProject, 'TMP', 'SDR_Biophysical_Table.csv')
        Table.to_csv(Tmp, index=False)

        # ---------------------------------------------------------------------
        # Parametros de entrada del modelo
        # ---------------------------------------------------------------------
        # Ruta de la tabla biofisica temporal de la region
        BioTable        = Tmp
        # Ruta del raster de coberturas de la region
        LULC            = os.path.join(PathProject, 'INPUTS','LULC.tif')
        # Ruta de las cuencas de la Region
        Watershed       = os.path.join(PathProject, 'INPUTS','Basin','Basin_Cal_SDR.shp')
        # Ruta del DEM de la region
        DEM             = os.path.join(PathProject, 'INPUTS','DEM_90m.tif')
        # Ruta de la Erosividad de la lluvia de la region
        Erosivity       = os.path.join(PathProject, 'INPUTS','R.tif')
        # Ruta de la Erodabilidad del suelo de la region
        Erodibility     = os.path.join(PathProject, 'INPUTS', 'K.tif')
        # Ruta de la carpeta de resultados de la region
        Results         = os.path.join(PathProject, 'OUTPUTS', '03-SDR')

        # ---------------------------------------------------------------------
        # Configuracion de diccionario de entrada del modelo de nutrientes
        # ---------------------------------------------------------------------
        args = {}
        args['biophysical_table_path']          = BioTable
        args['dem_path']                        = DEM
        args['drainage_path']                   = ''
        args['erodibility_path']                = Erodibility
        args['erosivity_path']                  = Erosivity
        args['lulc_path']                       = LULC
        args['results_suffix']                  = ''
        args['watersheds_path']                 = Watershed
        args['workspace_dir']                   = Results
        args['threshold_flow_accumulation']     = '1000'
        args['ic_0_param']                      = '0.5'
        args['sdr_max']                         = '%0.2f' % x[0]
        args['k_param']                         = '%0.2f' % x[2]

        # ---------------------------------------------------------------------
        # Ejecucion del modelo
        # ---------------------------------------------------------------------
        sdr.execute(args)

        # ---------------------------------------------------------------------
        # Lectura del dbf de resultados
        # ---------------------------------------------------------------------
        NameFile    = os.path.join( Results , 'watershed_results_sdr.dbf')
        dbf         = Dbf5(NameFile)
        simulation  = dbf.to_dataframe()

        # ---------------------------------------------------------------------
        # Busca los datos de carga de sedimentos en la tabla de resultados asociados a cada cuenca
        # ---------------------------------------------------------------------
        Sim = simulation['sed_export'].values
        [I, idx] = ismember(simulation['ws_id'].values, evaluation['ID'].values)
        Obs = evaluation['SDR'].values[idx]

        # ---------------------------------------------------------------------
        # Guarda el valor de la metrica en el CSV Metr
        # ---------------------------------------------------------------------
        objectivefunction = spotpy.objectivefunctions.rmse(Obs, Sim)

        # --------------------------------------------------------------------------------------------------------------
        # Guarda el valor de la metrica en el CSV Metric
        # --------------------------------------------------------------------------------------------------------------
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '03-SDR', 'Metric.csv')
        ID_File = open(PathRestuls, 'a')
        ID_File.write('%0.2f' % x[0] + ',' + '%0.2f' % x[1] + ',' + '%0.2f' % x[2] + ',' + '%.2f' % objectivefunction + '\n')
        ID_File.close()

        # --------------------------------------------------------------------------------------------------------------
        # Guarda el valor observado en el CSV Obs
        # --------------------------------------------------------------------------------------------------------------
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '03-SDR', 'Obs.csv')
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
        PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '03-SDR', 'Sim.csv')
        ID_File = open(PathRestuls, 'a')
        for ii in range(0, len(Sim)):
            ID_File.write('%0.2f' % Sim[ii] + '\n')
        ID_File.close()

        return objectivefunction
