from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'SurfWaveR'
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

REQUIRES_PYTHON='>=3.6.0'

# Setting up
setup(
    name="surfwaver",
    version=VERSION,
    author="Shanu Biswas",
    author_email="shanubiswas119@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires=REQUIRES_PYTHON,
    py_modules=["surfwaver", "maswGui", "threads","surfwaver\res\mkcmpcc.py","surfwaver\res\mkcmp.py","surfwaver\res\gather_plot.py", "surfwaver\res\aquGeomPlot.py","surfwaver/modswpro/cmpccworkflows.py", "surfwaver/modswpro/modwavefieldtransforms.py","surfwaver/modswpro/modsensor1C.py", "surfwaver/modswpro/modmasw.py", "surfwaver/modswpro/modarray1D.py" ],             # Name of the python package
    package_dir={'':'surfwaver'},     # Directory of the source code of the package
    install_requires=["obspy", "PyQt5", "swprocess", "numpy", "scipy", "matplotlib"],
    keywords=['MASW', 'Multichannel Analysis of Surface Waves', 'Dispersion', 'Inversion', 'seismic', 'active and passive surface wave', "SurfWaveR" ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
