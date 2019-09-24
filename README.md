# paralogger
Misc stuff about paraglider logger

## Goals:
* Exploring data-loggers possibilities for an application in the EN flight test norm.
* Testing and judging the reliabilyty of the dataloggers , and assess theirs adavantges and their limits.
* Collect datas in view to propose criteria for the norm.

## Project road:
1. **Hardware selection**
2. **Validations indoor:**

    feature|  validation method | description
    ------------ | ------------- | ------------- 
    Quaternions - pitch, roll | pendulum |overlaying a animation based on data and a video recording the experience
    Quaternions - yaw| Slow rotating table |overlaying a animation based on data and a video recording the experience
    Horizon level stability | Fast rotating table |check that the artificial horizon is not tilled under roation acceleration
    Sync GPS between devices | shock table |needed to link data from pilot and wing
    position-orientation reconstruction | -  |reconstruction of the travel and oriention on the screen.

3. **Validation in the air:**

    feature|  validation method | description
    ------------ |  ------------- | ------------- 
    Position in the harness  | ? |check the IMU  mesurement and the GPS reception
    Position in the glider | ? |check the sensibility to glider deformation
    number of device  | ? |check if two device are really needed

4. **Test in the air:**

    * From simple measure 
        * g force []
        * altitude lost [m]
        * recovery time [s]
        * speed ( need pitot) [m/s]
    * Medium one:
        * course change [°]
        * sink rate at point [m/s]
        * g force at point []
    * to hard one 
        * angle [°]
        * angle speed [°/s]
        * angle acceleration [°/s2]
        * angle jerk [°/s3]

**5. final specs**




## Creating environment:
Working on :
* Linux Mint : 18.3 - 19.1
* python : 3.7
* anaconda : 4.7.11

**Setting up the python env**
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
## Organisation of the code
So far just a bunch of scripts.


## Sharing
More infos will be shared, better  it will be.

So far this repo issues section will be used  and the significant info/progress will be collected in this repo wiki.

## Dead line:

![](https://imgs.xkcd.com/comics/estimating_time.png)

[https://xkcd.com/1658/]: https://xkcd.com/1658/

