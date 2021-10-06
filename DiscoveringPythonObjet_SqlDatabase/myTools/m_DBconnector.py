##############################################################################################################################################
#Import handling
##############################################################################################################################################
#The following modules are included by default with Python
# => list of all included by default modules in https://docs.python.org/3/py-modindex.html#cap-g
from abc import ABC, abstractmethod
import getpass

#The following modules are supposed not to be installed
from myTools import m_ModuleInstaller as mi

try:
    import pyodbc
except:
    mi.installModule("pyodbc")
    import pyodbc

try:
    import pandas as pd 
except:
    mi.installModule("pandas")
    import pandas as pd    
  
    
##############################################################################################################################################
#Generic class for Data Base connection
##############################################################################################################################################
class DBconnector(ABC):
    
    def __init__(self: object, server: str = 'undef', name:str = 'undef', username:str = 'undef', dsn:str = 'undef'):
        """ Parameters are either: server, name, username; or: dsn, username """

        self._DBserver : str                = server
        self._DBname : str                  = name
        self._DBusername : str              = username
        self._DBpassword : str              = getpass.getpass("Enter your SQL server password : ")         
        self._DBdsn : str                   = dsn
        
        self._DBisconnectionopen : bool     = False     
        self._DBconduit : pyodbc.Connection = None
        
        self._DBdriver : str                = 'undef'


    @abstractmethod                                                
    def _selectBestDBDriverAvailable(self:object) -> None:
        #The driver must be initialized in a specific Data Base server class
        pass


    def Open(self:object) -> None:
        """ Open a connection through DataBase with already set parameters """
        
        #Connection NOT already opened
        if(self._DBisconnectionopen == False):
            
            #Conduit NOT already created
            if(self._DBconduit is None):
                
                try:
                    
                    #Connection with UserName & Co parameters
                    if (self._DBdsn == 'undef'):
                        
                        self._DBconduit = pyodbc.connect("Driver={" + self._DBdriver \
                                                   + "};Server=" + self._DBserver \
                                                   + ";Database=" + self._DBname \
                                                   + ";UID=" + self._DBusername \
                                                   + ";PWD=" + self._DBpassword + ";")
                        self._DBisconnectionopen = True
                        
                    #Connection with DSN parameter & Co parameters
                    else:
                        
                        self._DBconduit = pyodbc.connect("DSN=" + self._DBdsn + ";UID=" + self._DBusername + ";PWD=" + self._DBpassword + ";")
                        self._DBisconnectionopen = True
                        
                        #We recover connection parameters from conduit opened with DSN
                        self._DBserver = self._DBconduit.getinfo(pyodbc.SQL_SERVER_NAME)
                        self._DBname = self._DBconduit.getinfo(pyodbc.SQL_DATABASE_NAME)
                        self._DBdriver = self._DBconduit.getinfo(pyodbc.SQL_DRIVER_NAME)
                
                except Exception as exc:
                    self._DBisconnectionopen == False
                    self._DBconduit.close()
                    print("\nCouldn't connect to the database : ", exc)
                    raise 
                    
            ##Conduit already created: connection is closed, but ODBC instance is NOT null
            else: 
                self._DBconduit.close()
                raise("\nInconsistent state of the connector: flag set to not connected and conduit is NOT none\n")
                    
        #Connection already opened
        else: 
            self._DBisconnectionopen == False
            if(self._DBconduit is not None):
                self._DBconduit.close()
            raise Exception("\nInconsistent call to Open(), connector already connected to the data source\n")
                    
            
    def Close(self:object) -> None:
        """ Close a connection through DataBase """

        #Connection NOT already closed
        if(self._DBisconnectionopen == True):
            
            #Conduit NOT already deleted
            if(self._DBconduit is not None):
                
                try:
                    self._DBisconnectionopen == False
                    self._DBconduit.close()
                    
                except Exception as exc:
                    print("\nCouldn't disconnect to the database : ", exc)
                    raise   
                    
            #Conduit already deleted: connection is opened, but ODBC instance is None
            else:
                self._DBisconnectionopen == False
                raise("\nInconsistent state of the connector: flag set to connected and conduit is none\n")
                
        #Connection already closed 
        else:
            if(self._DBconduit is not None):
                self._DBconduit.close()
            raise Exception("\nInconsistent call to Close(), connector NOT connected to the data source\n")


    #Getter for attributes which have no corresponding setter
    #########################################################
    @property
    def getConduit(self:object) -> pyodbc.Connection:
        """ Conduit is automatically set after an Open() method call """
        return self._DBconduit   
                 
    @property
    def getIsconnectionopen(self:object) -> bool:
        """ Isconnectionopen flag is automatically set inside the Open() method call """
        return self._DBisconnectionopen   
                         
    @property                                                      
    def getDriver(self:object) -> str: 
        """ Driver is automatically set through connector instanciation (in case of User Name instanciation parameters)
            or automatically set inside the Open() method call (in case of DSN instanciation parameters) """
        return self._DBdriver  


    #Getter / Setter for other attributes
    #####################################
    @property                                                      
    def getServer(self:object) -> str: 
        return self._DBserver

    @property                                                      
    def getName(self:object) -> str: 
        return self._DBname

    @property                                                      
    def getUsername(self:object) -> str: 
        return self._DBusername                         

    @property                                                      
    def getDsn(self:object) -> str: 
        return self._DBdsn 

    @getServer.setter                                               
    def setServer(self:object, server:str) -> None:                    
        self._DBserver = server
        
    @getName.setter                                               
    def setName(self:object, name:str) -> None:                    
        self._DBname = name

    @getUsername.setter                                                    
    def setUsername(self:object, username:str) -> None: 
        self._DBusername = username  
         
    @getDsn.setter                                                      
    def setDsn(self:object, dsn:str) -> None: 
        self._DBdsn = dsn    
        
    
    #Generic command for sending queries to Data Base to which we are connected
    ###########################################################################
    def ExecuteQuery_withRS(self:object, query:str) -> pd.DataFrame:
        """ Sends a query to the connected Data Base
                Parameter query is a Data Base query string """

        MySQL_Answer = pd.DataFrame()
        
        #Connection already opened
        if(self._DBisconnectionopen == True):
            
            #Conduit already created
            if(self._DBconduit is not None):
                
                try:

                    MySQL_Answer = pd.read_sql(query, self.getConduit)
                    
                except Exception as exc:
                    self._DBisconnectionopen == False
                    self._DBconduit.close()
                    print("\nCouldn't send request to the database :", exc) 
                    raise   
                    
            #Conduit NOT already created: connection is opened, but ODBC instance is None
            else:
                self._DBisconnectionopen == False
                raise("\nInconsistent state of the connector: flag set to connected and conduit is none\n")
                
        #Connection NOT already opened
        else:
            if(self._DBconduit is not None):
                self._DBconduit.close()
            raise Exception("\nInconsistent call to Close(), connector NOT connected to the data source\n")
        
        return MySQL_Answer