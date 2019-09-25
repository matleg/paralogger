# paralogger
Misc stuff about paraglider logger

## Goals:
* Exploring data-loggers possibilities for an application in the EN flight test norm.
* Testing and judging the reliabilyty of the dataloggers , and assess theirs adavantges and their limits.
* Collect datas in view to propose criteria for the norm.

## Project road:
1. **Hardware selection**

    * IMU
    * Gps
    * battery and power board
    * plastic case
    * pitot tube (if needed)
    * keyboard (or input method , to tag specific manoeuvre in the log  and to discard the badly executed ones)
    * telemetry (if needed?  to send live data to ground.)

2. **Validations indoor:**
    Before going in the air some points needed to be validate to trust the recorded data.

    feature|  validation method | description
    ------------ | ------------- | ------------- 
    Quaternions - pitch, roll | pendulum | Overlaying a animation based on data and a video recording the experience.
    Quaternions - yaw| Slow rotating table | Overlaying a animation based on data and a video recording the experience.
    Horizon level stability | Fast rotating table | Check that the artificial horizon is not tilted under rotation acceleration.
    Sync GPS between devices | shock table | Needed to link data from pilot and wing.
    Position-orientation reconstruction | -  | Reconstruction of the travel and orientation on the screen.
    Sync with camera | - |Check the possibility to sync the data with video recording (using camera with gps), useful to debug in air.


3. **Validation in the air:**
    Before trusting the data for interpreting the manoeuvre, we need to confirm different points, to be sure we recorded the good stuff.

    feature|  validation method | description
    ------------ |  ------------- | ------------- 
    Position in the harness  | ? |Check the best placement in the harness for IMU measurement and the GPS reception.
    Position in the glider | ? |Check the sensibility to glider deformation.
    Number of devices  | ? |Check if two device are really needed.


4. **Possible outputs:**
Here a list of possible pertinent output, that should be tested for their revelancy .

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

