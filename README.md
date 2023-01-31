# SurfWaver - a GUI for Multichannel Analysis of Surface Waves (Rayleigh waves).
<img src="https://github.com/Shanu911/SurfWaver/blob/main/surfwaver/icons/logo.png" width="48">
SurfWaveR is an open source project, initiated by SIIP lab IIT Bombay. It can perform dispersion and inversion (2D) of active and passive seismic data. 
I have used <code>pyQT5</code> to build the GUI, the <code>swprocess</code> module to generate dispersion curves using various transform methods, and the <code>evodcinv</code> and <code>srfpython</code> modules to do inversion with evolutionary and Monte-Carlo Markov Chain algorithms, respectively. <br>
It is not completed yet, but I'm working on it.

# Installation
#### Process 1 (Recomended)
Download the respository as zip from the green 'code' dropdown button. <br>
Extract all files to a working directory <br>
then open shell or command prompt in that working directory with activating a conda environment <br>
After that copy pest below codes
```
pip install .
cd surfwaver
python surfwaver.py
```

As the package is not fully completed, it will be better to choose this option.

#### Process 2  (PYPI version is not updated so use only Process 1)

one can install the package via PyPI 
```
pip install surfwaver
```
or clone this respository by
```
git clone https://github.com/Shanu911/SurfWaver.git
```
