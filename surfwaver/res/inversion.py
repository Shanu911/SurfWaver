from evodcinv import EarthModel, Layer, Curve
import matplotlib.pyplot as plt
import numpy as np
import json
# Initialize model

class Inversion:
    def __init__(self, fname, method="cpso", nlayer=3, maxrun=1):
        """
        fname: target file or surf96 file containing frequency and velocity
        method : cpso, pso
        
        """

        
        self.model = EarthModel()


        # Build model search boundaries from top to bottom
        # First argument is the bounds of layer's thickness [km]
        # Second argument is the bounds of layer's S-wave velocity [km/s]
        with open("file", "r") as f:
            mddict = json.load(f)
        z = mddict["Z"]
        vs = mddict["vs"]
        for i in range(nlayer):
            self.model.add(Layer(z[i], vs[i]))

        # Configure model
        self.model.configure(
            optimizer=method,  # Evolutionary algorithm
            misfit="rmse",  # Misfit function type
            optimizer_args={
                "popsize": 10,  # Population size
                "maxiter": 100,  # Number of iterations
                "workers": -1,  # Number of cores
                "seed": 0,
            },
        )

        file = open(fname)
        jsonobj = json.load(file)
        listloc = list(jsonobj.keys())
        self.vels = []
        self.pers = []

        for l in listloc:
            d = jsonobj[l]
            if 0 not in d['frequency']:
                per = np.round([1/x for x in d['frequency']], 7)
                period = per[::-1]
                vel = np.round(d['velocity'], 7)
                velocity = vel[::-1]/1000
            else:
                per = np.round([1/x for x in d['frequency'][1:]], 7)
                period = per[::-1]
                vel = np.round(d['velocity'][1:], 7)
                velocity = vel[::-1]/1000
            self.vels.append(velocity)
            self.pers.append(period)


        # Define the dispersion curves to invert

        # period and velocity are assumed to be data arrays
        self.curves = []
        for period, velocity in zip(self.pers, self.vels):
            self.curves.append(Curve(period, velocity, 0, "rayleigh", "phase"))
        
        self.res = self.model.invert(self.curves, split_results=True, maxrun=maxrun)

    def plot(self, ax=None, fig=None, param='vp'):
        if ax == None:
            fig, ax = plt.subplots()
        for res in self.res:
            res.plot_model(parameter = param, ax=ax)
        ax.plot()
        if ax== None:
            return (fig, ax)
        else:
            return None

    def plt_misfit(self, ax=None, fig=None):
        if ax == None:            
            fig, ax = plt.subplots()
        for res in self.res:
            res.plot_misfit(ax=ax)
        if ax== None:
            return (fig, ax)
        else:
            return None

    def plt_crv(self, ax=None, fig=None):
        if ax == None:            
            fig, ax = plt.subplots()
        ax.set_xscale("log")
        ax.plot(1/self.pers[0], self.vels[0], 'k')
        for res in self.res:
            for period in self.pers:
                res.plot_curve(period, 0, "rayleigh", "phase", ax=ax, plot_args={"xaxis": "frequency","type": "semilogx"})
            
        if ax== None:
            return (fig, ax)
        else:
            return None

    def result(self):
        return self.res
