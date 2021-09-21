import os
import spotpy
import spotpy_setup_SDR as spotpy_setup
import pandas as pd
import pygeoprocessing

def CreateFolder(PathName):
    try:
        os.mkdir(PathName)
    except OSError as error:
        print(error)

# --------------------------------------------------------------------------------------------------------------
# Creando folders
# --------------------------------------------------------------------------------------------------------------
PathProject     = r'D:\TARULLA Dropbox\P17-InVEST\03-Productos_Intermedios\03-InVEST'

CreateFolder(os.path.join(PathProject, 'OUTPUTS'))
CreateFolder(os.path.join(PathProject, 'OUTPUTS','03-SDR'))
CreateFolder(os.path.join(PathProject, 'EVALUATIONS'))
CreateFolder(os.path.join(PathProject, 'EVALUATIONS','03-SDR'))
CreateFolder(os.path.join(PathProject, 'PARAMETERS'))
CreateFolder(os.path.join(PathProject, 'PARAMETERS','03-SDR'))

# --------------------------------------------------------------------------------------------------------------
# Create Object - Spotpy
# --------------------------------------------------------------------------------------------------------------
spot_setup  = spotpy_setup.spotpy_setup()

# --------------------------------------------------------------------------------------------------------------
# Guard
# --------------------------------------------------------------------------------------------------------------
PathResults = os.path.join(PathProject, 'EVALUATIONS', '03-SDR', 'Metric.csv')
ID_File = open(PathResults, 'w')
ID_File.write('sdr_max,Factor-C,Kb,RMSE\n')
ID_File.close()

PathResults = os.path.join(PathProject, 'EVALUATIONS', '03-SDR', 'Sim.csv')
ID_File = open(PathResults, 'w')
ID_File.write('Sim\n')
ID_File.close()

results     = []
rep         = 50
timeout     = 2 #Given in Seconds

parallel = "seq"
dbformat = "csv"

PathRestuls = os.path.join(PathProject, 'PARAMETERS','03-SDR','LHS')
sampler     = spotpy.algorithms.lhs(spot_setup, parallel=parallel, dbname=PathRestuls, dbformat=dbformat, sim_timeout=timeout)
sampler.sample(rep)
results.append(sampler.getdata())