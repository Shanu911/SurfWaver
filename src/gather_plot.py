import matplotlib.pyplot as plt
import numpy as np

class GraphBox:

    def __init__(self, tracedata, offset, spaceList) -> None:
        self.trcdata = tracedata
        self.cdp = offset
        self.spaces = spaceList
        self.plot()

    def scaleUp(self):
        pass

    def scaleDown(self):
        pass

    def plot(self, ww=5, hh=3, type=0):
        """
        type:   gather type 0 -> CMPCC   |
                            1 -> Shot
        """
        fig, ax = plt.subplots(figsize=(ww, hh), dpi=150)

        ax.plot(self.trcdata, self.spaces)
        ax.set_xlabel()
        ax.set_ylabel()
        if type==0:
            ax.set_title("")

        fig.savefig()
        pass

    def setImage(self):
        pass
