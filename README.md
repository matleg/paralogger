# paralogger
Misc stuff about paraglider logger


#Creating environment:

```bash
conda create --name paralogger

conda install -n paralogger pip

conda install --name paralogger pylint

conda cativate paralogger

conda install -c conda-forge pyulog
conda install pandas
conda install -c bokeh bokeh
conda install -c anaconda scipy
conda install -c conda-forge matplotlib 
```

Misc ( to run PX4 preview):
```bash
conda install -c conda-forge pyfftw
conda install -c conda-forge simplekml
conda install -c mikesilva smopy
```

To check:

```bash
conda list -n paralogger
```