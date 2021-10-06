##############################################################################################################################################
#Import handling
##############################################################################################################################################
from myTools import m_DBconnector as m_db

#The following modules are supposed not to be installed
from myTools import m_ModuleInstaller as mi
try:
    import pyodbc
except:
    mi.installModule("pyodbc")
    import pyodbc

##############################################################################################################################################
#Generic class for Data Base connection, on SQL server, with ODBC driver
##############################################################################################################################################
class SQLconnector(m_db.DBconnector):

    listOfMicrosoftOdbcDrivers = ["ODBC Driver 17 for SQL Server", "ODBC Driver 13.1 for SQL Server", \
                                  "ODBC Driver 13 for SQL Server", "ODBC Driver 11 for SQL Server", \
                                  "SQL Server Native Client 11.0", "SQL Server Native Client 10.0", \
                                  "SQL Native Client", "SQL Server"]
    
    def __init__(self: object, SQLserver: str = 'undef', SQLname:str = 'undef', SQLusername: str = 'undef', SQLdsn: str = 'undef'): 
        """ Open a connexion with a SQL Data Base, with an ODBC driver
                Possible parameters are either: SQLserver, SQLname, SQLusername; or: SQLdsn, SQLusername """
        
        super().__init__(server = SQLserver, name = SQLname, username = SQLusername, dsn = SQLdsn)
        
        #In case where a DSN is used, no need to find a driver (as already 'included' in DSN)
        if (SQLdsn == 'undef'): 
            self._selectBestDBDriverAvailable()
        

    def _selectBestDBDriverAvailable(self:object) -> None:
        listOfAllAvailableDrivers:list[str] = pyodbc.drivers()

        if(listOfAllAvailableDrivers is not None):

            #At least one driver is installed on the machine
            for i in range( len(SQLconnector.listOfMicrosoftOdbcDrivers) ):
                
                if(SQLconnector.listOfMicrosoftOdbcDrivers[i] in listOfAllAvailableDrivers):
                    self._DBdriver = SQLconnector.listOfMicrosoftOdbcDrivers[i]
        
        if (self._DBdriver == 'undef'):

            #Either no available installed driver 
            #or installed driver are not in the list of the one developped by Microsoft for ODBC
            raise Exception("\nNo available Microsoft SQL ODBC driver, the connection can not open\n")


##############################################################################################################################################
#Example of class use
##############################################################################################################################################
def ExampleDBConnection(ConnectionWithDSN = False, VerifSetter = False) -> None:
   """ Opens a connection with a local DataBase
       and sends a SELECT * request """ 
   
   try:
       
       #Connection with User Name parameters
       if (ConnectionWithDSN == False): 
           
           #Use of Setter to set up connection
           if (VerifSetter == True):
               
               #Instanciation without any parameters
               MySQLconnector = SQLconnector()
               
               #Connection parameters are set after instanciation (use of setter)
               MySQLconnector.setServer     = "LAPTOP-97S6E2L6"
               MySQLconnector.setName       = "Survey_Sample_A19"
               MySQLconnector.setUsername   = "sa"
               
           #Connection parameters directly set during instanciation
           else:
               MySQLconnector = SQLconnector(SQLserver = "LAPTOP-97S6E2L6", SQLname = "Survey_Sample_A19", SQLusername = "sa")
               
               
       #Connection with DSN parameters
       else: 
           
           #Use of Setter to set up connection
           if (VerifSetter == True):
               
               #Instanciation without any parameters
               MySQLconnector = SQLconnector()
               
               #Connection parameters are set after instanciation (use of setter)
               MySQLconnector.setDsn        = "ConnexionSQL_CAT"
               MySQLconnector.setUsername   = "sa"
           
           #Connection parameters directly set during instanciation
           else:
               MySQLconnector = SQLconnector(SQLdsn = "ConnexionSQL_CAT", SQLusername = "sa")
       
        
       #Connection opening
       MySQLconnector.Open()
       
       
       #Verification of attributes with getter
       print(f"\nServer Getter - {MySQLconnector.getServer}")
       print(f"Name Getter - {MySQLconnector.getName}")
       print(f"Username Getter - {MySQLconnector.getUsername}")
       print(f"Dsn Getter - {MySQLconnector.getDsn}")
       print(f"Driver Getter - {MySQLconnector.getDriver}") 
       print(f"Conduit Getter - {MySQLconnector.getConduit}")
       print(f"Isconnectionopen Getter - {MySQLconnector.getIsconnectionopen}\n")
       
       #SELECT query sent
       Sql_surveyQuery = "SELECT * FROM dbo.Survey"
       print(MySQLconnector.ExecuteQuery_withRS(Sql_surveyQuery).head())
    
       MySQLconnector.Close()

   except Exception as exc:
       MySQLconnector.Close()
       print("\nException :", exc) 
       raise 

   
if __name__ == '__main__':

   #Connection with either User Name & Co parameters or with DSN parameters
   ConDSN = True
   
   #Use of setter activation / deactivation
   SetterUse = True

   ExampleDBConnection(ConnectionWithDSN = ConDSN, VerifSetter = SetterUse)
                
