import os
import spotpy
import spotpy_setup_AWY as spotpy_setup
import pandas as pd
from simpledbf import Dbf5

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
CreateFolder(os.path.join(PathProject, 'OUTPUTS','01-AWY'))
CreateFolder(os.path.join(PathProject, 'EVALUATIONS'))
CreateFolder(os.path.join(PathProject, 'EVALUATIONS','01-AWY'))
CreateFolder(os.path.join(PathProject, 'PARAMETERS'))
CreateFolder(os.path.join(PathProject, 'PARAMETERS','01-AWY'))

# --------------------------------------------------------------------------------------------------------------
# Create Object - Spotpy
# --------------------------------------------------------------------------------------------------------------
spot_setup  = spotpy_setup.spotpy_setup()

# --------------------------------------------------------------------------------------------------------------
# Guardar
# --------------------------------------------------------------------------------------------------------------
PathResults = os.path.join(PathProject, 'EVALUATIONS', '01-AWY', 'Metric.csv')
ID_File = open(PathResults, 'w')
ID_File.write('Z,Factor-Kc,RMSE\n')
ID_File.close()

PathRestuls = os.path.join(PathProject, 'EVALUATIONS', '01-AWY', 'Sim.csv')
ID_File = open(PathRestuls, 'w')
ID_File.write('Sim\n')
ID_File.close()

results     = []
rep         = 100
timeout     = 2 #Given in Seconds

parallel = "seq"
dbformat = "csv"

PathRestuls = os.path.join(PathProject, 'PARAMETERS','01-AWY','LHS')
sampler     = spotpy.algorithms.lhs(spot_setup, parallel=parallel, dbname=PathRestuls, dbformat=dbformat, sim_timeout=timeout)
sampler.sample(rep)
results.append(sampler.getdata())

