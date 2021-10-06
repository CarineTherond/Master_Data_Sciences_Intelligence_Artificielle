##############################################################################################################################################
#Import handling
##############################################################################################################################################
#The following modules are included by default with Python
# => list of all included by default modules in https://docs.python.org/3/py-modindex.html#cap-g
import sys
import os
import glob
import argparse as agp

#Importation of my files: Return the asolute name of path in which this script is executed
filePath = os.path.split(os.path.abspath(__file__))[0]

#The previous path is added in the interpreter’s search path for files
# => file m_fn_GetAllSurveyData and module m_SQLconnector are in the same directory as this script, and then it will be found
sys.path.append(filePath)

from myTools import m_fn_GetAllSurveyData as m_fn
from myTools import m_SQLconnector as m_sql


#The following modules are supposed not to be installed
from myTools import m_ModuleInstaller as mi
try:
    import pandas as pd
except:
    mi.installModule("pandas")
    import pandas as pd



##############################################################################################################################################
#Verifies if a previous saved version of 'SurveyStructure' table is existing
##############################################################################################################################################
def SurveyStructureTableSaved_check(fileTable: str) -> bool:

    return glob.glob(fileTable)[0] == fileTable


##############################################################################################################################################
#Algorithm executed inside trg_refreshSurveyView, when triggered
##############################################################################################################################################
def algo_refreshSurveyView(MySQLconnector: m_sql.SQLconnector, fileView: str, fileSurvey: str) -> None:

    try:
        
        strSQLSurveyData = "CREATE OR ALTER VIEW vw_AllSurveyData AS " + m_fn.fn_GetAllSurveyDataSQL(MySQLconnector, fileSurvey) + ";"
    
        #pd.read_sql does not handle queries that return nothing: so we directly use the connection conduit to execute this request
        cur = MySQLconnector.getConduit.cursor()
        cur.execute(strSQLSurveyData)
        
        vw_AllSurveyData = MySQLconnector.ExecuteQuery_withRS("SELECT * FROM vw_AllSurveyData")
    
        #Saving of refreshed vw_AllSurveyData view
        vw_AllSurveyData.fillna('NULL').to_csv(fileView) 

    except Exception as exc:
        MySQLconnector.Close()
        print("\nException : ", exc)
        raise  
    
    
    
##############################################################################################################################################
#Triggering of trg_refreshSurveyView trigger
##############################################################################################################################################
def trg_refreshSurveyView(ParamDict: dict) -> None:
    """ refresh the vw_AllSurveyData view only if needed 
            (vw_AllSurveyData is dynamically constructed by fn_GetAllSurveyDataSQL) """    
    
    try:
        #Connection to Survey_Sample_A19 DataBase
        MySQLconnector = m_sql.SQLconnector(SQLserver = ParamDict["dbserver"], \
                                            SQLname = ParamDict["dbname"], \
                                            SQLusername = ParamDict["dbusername"], \
                                            SQLdsn = ParamDict["dsn"])
        MySQLconnector.Open()
        
        #Inspection of current SQL table SurveyStructure 
        SurveyStructureTable_current = MySQLconnector.ExecuteQuery_withRS(m_fn.SurveyStructureRequest)
        SurveyStructureTable_current.fillna('NULL', inplace = True)
        
        #Check if already existing saved version of SurveyStructure
        if (SurveyStructureTableSaved_check(ParamDict['persistencefilepath']) == True) :
            #Comparison with the previously saved version of table SurveyStructure 
            SurveyStructureTable_saved = pd.read_csv(ParamDict['persistencefilepath'], index_col = 0)
            
            #Rows in current SQL table SurveyStructure has been added or deleted, we need to refresh the vw_AllSurveyData view
            if (SurveyStructureTable_current.shape[0] != SurveyStructureTable_saved.shape[0]) :
                algo_refreshSurveyView(MySQLconnector, ParamDict['resultsfilepath'], ParamDict['persistencefilepath'])
    
            #Content of current SQL table SurveyStructure has been modified, we need to refresh the vw_AllSurveyData view
            else:
                if ((SurveyStructureTable_current == SurveyStructureTable_saved).all().all() != True):
                    algo_refreshSurveyView(MySQLconnector, ParamDict['resultsfilepath'], ParamDict['persistencefilepath'])
        else:
            algo_refreshSurveyView(MySQLconnector, ParamDict['resultsfilepath'], ParamDict['persistencefilepath'])
        
        MySQLconnector.Close()
        
    except Exception as exc:
        MySQLconnector.Close()
        print("\nException : ", exc)
        raise 



if __name__ == '__main__':
    
    try:
        #Line command argument handling: all arguments are considered as optinal
        #=> It will be specifically verified later that the minimum required arguments have been provided
        
        #Help comments for this m_trg_refreshSurveyView.py programm
        my_parser = agp.ArgumentParser(description = 'refresh the vw_AllSurveyData view only if needed \
                                                   (vw_AllSurveyData is dynamically constructed by fn_GetAllSurveyDataSQL)',
                                        epilog = 'Required parameters are either: (server AND name AND username) OR (dsn AND username)')
        
        #SQL connection arguments
        my_parser.add_argument("-dbusername", default = 'undef')
    
        my_parser.add_argument("-dsn", default = 'undef')
        my_parser.add_argument("-dbserver", default = 'undef')
        my_parser.add_argument("-dbname", default = 'undef')
        #save files arguments
        my_parser.add_argument("-persistencefilepath", default = filePath + "/SurveyStructure.csv" , \
                               help = "Optional argument: persistencefilepath - File name (with absolute path) in which saving SurveyStructure table \
                                               - By default 'SurveyStructure.csv' on current directory")
        my_parser.add_argument("-resultsfilepath", default = filePath + "/vw_AllSurveyData.csv", \
                               help = "Optional argument: resultsfilepath - File name (with absolute path) in which saving vw_AllSurveyData view \
                                               - By default 'vw_AllSurveyData.csv' on current directory")
        
        #Handling of received argumernts in a dictionary
        args = my_parser.parse_args()
        
        retParametersDictionary:dict = None
        
        retParametersDictionary = {
                "dsn" : args.dsn,        
                "dbserver" : args.dbserver,
                "dbname" : args.dbname,
                "dbusername" : args.dbusername,
                "persistencefilepath": args.persistencefilepath,
                "resultsfilepath" : args.resultsfilepath
                }
        
        #Verification of provided arguments for either a by name SQL connection, or a by dsn one
        if retParametersDictionary['dsn'] == 'undef':
            #In case where no DSN is used, we need server, name et username
            if(retParametersDictionary['dbserver'] == 'undef' \
                or retParametersDictionary['dbname'] == 'undef' \
                or retParametersDictionary['dbusername'] == 'undef'):
                print("Invalid arguments")
                raise Exception("dbserver, dbname and dbusername must be defined")
        else:
            #In case where DSN is used, we need in addition, the username
            if(retParametersDictionary['dbusername'] == 'undef'):
                print("Invalid arguments")
                raise Exception("dsn and dbusername must be defined")

            
    except Exception as e:
        print("Command Line arguments processing error: " + str(e))
        for k, v in retParametersDictionary.items():
            print('\t{0:<25} {1}'.format(k, v))
        
    else:
        #In case where no exception has been triggered (arguments are OK), we can begin the SurveyStructure analysis
        trg_refreshSurveyView(retParametersDictionary)

 