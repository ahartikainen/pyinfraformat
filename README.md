![pyinfraformat](https://github.com/ahartikainen/pyinfraformat/workflows/pyinfraformat/badge.svg?branch=master) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![codecov](https://codecov.io/gh/ahartikainen/pyinfraformat/branch/master/graph/badge.svg)](https://codecov.io/gh/ahartikainen/pyinfraformat)


# pyinfraformat
Python library for reading, writing and analyzing Finnish borehole format Infraformat (version 2.5). 
Well suited for scientific and research applications.

## Installation

Latest (stable) `pyinfraformat` can be installed with pip

    python -m pip install pyinfraformat

The latest (unstable) version can be installed from git with pip (needs git-tools).

    python -m pip install git+https://github.com/ahartikainen/pyinfraformat

Library can be installed also by `git clone` / downloading zip.

    git clone https://github.com/ahartikainen/pyinfraformat
    cd pyinfraformat
    python -m pip install .

To install inplace for development work, use `-e` command.

    python -m pip install -e .

## Quickstart
#### Basic usage
```python
import pyinfraformat as pif
pif.set_logger_level(50) # Suppress non-critical warnings, recommended for large files
holes = pif.from_infraformat("*.tek")
holes = holes.project("TM35FIN")
bounds = holes.bounds
holes.to_infraformat("holes_tm35fin.tek")

bounds = [6672242-200 ,  385795-200, 6672242 +200,  385795+200]
gtk_holes = pif.from_gtk_wfs(bounds, "TM35Fin")
print(gtk_holes) # View holes object
#Infraformat Holes -object:
#  Total of 203 holes
#    - PO ......... 161
#    - HP .........  13
#    - PA .........  12
#    - NO .........   2
#    - NE .........   1
#    - KE .........   5
#    - KR .........   9


html_map = gtk_holes.plot_map()
html_map.save("soundings.html")
html_map # View map in jupyter
```
![image](https://github.com/user-attachments/assets/a463e181-4ab4-479d-94f6-edcb19c0f598)

```python
hole_figure = gtk_holes[10].plot()
hole_figure # View hole in jupyter
```

![image](https://github.com/user-attachments/assets/33b9c797-b084-44b2-88c8-dadd15fc540f)

#### Plot histograms from labratory tests
```python
import pandas as pd
bounds = [6672242-2000 ,  385795-2000, 6672242 +2000,  385795+2000]
gtk_holes = pif.from_gtk_wfs(bounds, "TM35FIN", maxholes=25_000)
labratory_tests = gtk_holes.filter_holes(hole_type=["NO", "NE"], start="1990-01-01")
df = labratory_tests.get_dataframe()
df['data_Soil type'] = df['data_Soil type'].astype("string")
clay_samples = df[df['data_Soil type'].str.endswith("Sa", na=False)].reset_index()
clay_samples['data_Laboratory w'] = pd.to_numeric(clay_samples['data_Laboratory w'])
fig = clay_samples['data_Laboratory w'].plot.hist(bins='fd')
fig.set_title("Clay samples water content, %")
fig
```
![image](https://github.com/user-attachments/assets/e3e6030b-ccfc-4c59-9929-40a7f9900fa4)
