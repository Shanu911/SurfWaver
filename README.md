# SurfWaver - a GUI for Multichannel Analysis of Surface Waves (Rayleigh waves).
<img src="https://github.com/Shanu911/SurfWaver/blob/main/surfwaver/icons/logo.png" width="48">
SurfWaveR is an open source project, initiated by SIIP lab IIT Bombay. It can perform dispersion and inversion (2D) of active and passive seismic data. 
I have used `pyQT5` to build the GUI, the `swprocess` module to generate dispersion curves using various transform methods, and the `evodcinv` and `srfpython` modules to do inversion with evolutionary and Monte-Carlo Markov Chain algorithms, respectively. <br>
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

#### Process 2  

one can install the package via PyPI 
```
pip install surfwaver
```
or clone this respository by
```
git clone https://github.com/Shanu911/SurfWaver.git
```
