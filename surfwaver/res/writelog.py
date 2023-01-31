import json
from attrdict import AttrDict
import os
import shutil

filename = "log/settings.json"
default_settings_file = "log\default_settings.json"

class sysParam(object):

    def __init__(self) -> None:
        try:
            file = open(filename , "r")
            self.data = AttrDict(json.load(file))      #   dict
            self.ROOTDR = self.data.gframe.rootdir    #   string
        except:
            self.ROOTDR = None #os.path.expanduser('~')
            raise "Settings file not found"
        
    #def setroot(self, newdir):
    #    self.ROOTDR    
    #
#
    #    def gather(self):
    #        return self.DFRAME["gather"] 
#
    #    def AquGeom(self):
    #        return self.DFRAME["AquGeom"] 
    #    
    #    def dispCurve(self):
    #        return self.DFRAME["dispCurve"]  

    


    #def write(self, attr, value):
    #    attr = value
#
    #    #jsonobj = json.dumps()
    #    #with open(filename, "w") as f:
    #    #    f.wite(jsonobj)
    #    #    f.close
##
    #    pass
    
    def datade(self):
        return self.data

    def getrootdir(self):
        if self.ROOTDR is not None:
            return self.ROOTDR
        else:
            return "tmp" #os.path.expanduser('~')
    
    
    def setrootdir(self, fldr):
        self.data["gframe"]["rootdir"] = fldr
        #print(self.data, fldr)
        try:
            with open(filename, "w") as f:
                f.write(json.dumps(dict(self.data)))
                f.close()
                return 1
        except:
            return 0
        
    def setall(self, data):
        if isinstance(data, AttrDict):
            try:
                with open(filename, "w") as f:
                    f.write(json.dumps(dict(data)))
                    f.close()
                    return 1
            except:
                return 0
        else:
            return 0
        
    def reset(self):
        try:
            shutil.copyfile(default_settings_file, filename)
            return 1
        except:
            return 0