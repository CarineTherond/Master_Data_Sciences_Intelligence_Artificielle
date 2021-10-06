#The following modules are included by default with Python
# => list of all included by default modules in https://docs.python.org/3/py-modindex.html#cap-g
import sys
import subprocess


def __isConda() -> bool:
    
    sub = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output = True)
    return (sub.returncode == 0) 


#The following modules are supposed not to be installed
def installModule(moduleName: str)  -> None:
    #help on web site: https://stackoverflow.com/questions/12332975/installing-python-module-within-code
    
    if __isConda() == False:
        try:
            subprocess.run([sys.executable, './myTools/get-pip.py'], capture_output = True)
            subprocess.run([sys.executable, "-m", 'pip', 'install', moduleName], capture_output = True)
        except:
            subprocess.check_call([sys.executable, './myTools/get-pip.py'])
            subprocess.check_call([sys.executable, "-m", 'pip', 'install', moduleName]) 
            
    else:
        try:
            subprocess.run([sys.executable, "-m", 'pip', 'install', moduleName], capture_output = True)
        except:
            subprocess.check_call([sys.executable, "-m", 'pip', 'install', moduleName])         