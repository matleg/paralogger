#! /usr/bin/env python

import pandas as pd
import os.path
import time
import string
import random
import hashlib
import datetime, time

import logging
logger = logging.getLogger("model")

#Local imports:

from model.list_param import Device,Position
from model.import_ulog import ulog_to_df , ulog_list_data , ulog_param

############################# DECORATOR #############################

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()       
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logger.info('%r  %2.2f s' % \
                  (method.__name__, (te - ts) ))
        return result    
    return timed

############################# DEFINITIONS #############################

def id_generator(msize=6, chars=string.ascii_uppercase + string.digits):  
    """ Generate a random ID .

    Parameters:
        msize (str): length of the random string.
        chars (list of string): the list of the possible characters

    :Returns:
        id_str(str): the random string   
    """

    id_str = ''.join(random.choice(chars) for _ in range(int(msize)))
    return id_str

def sha256sum(filename):
    """ Compute the sha256 of the a file.
    Usefull to refind source file , or detect duplicate one

    Parameters:
        filename (str):The file path.

    :Returns:
        sha(str): tHe sha256 hars string   
    """
    # compute the SH256 of the file  to identify possible duplicated source file.
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


############################# MAIN MODEL #############################

        
class Flight():
    def __repr__(self):
        return str(self.__dict__)


    def __init__(self):
        logger.info("initialise_flight ")
        
        self.id = id_generator()
        self.createdDate = time.time()

        self.manufacturer = None
        self.glider = None
        self.modif = None
        self.pilot = None
        self.weight = None
        self.location = None

        self.data = []

        self.Sections = []

        self.version = 1 # version of the data model

    @timeit
    def add_data_file(self, mfilePath , mdevice , mposition ):
        mData_File= Data_File( mfilePath , mdevice , mposition)
        mData_File.populate_df()
        mData_File.populated_device_param()

        self.data.append(mData_File)

    def add_info(self,mmanufacturer,mglider,mmodif,mpilot,mweight,mlocation):
        self.manufacturer = mmanufacturer
        self.glider = mglider
        self.modif = mmodif
        self.pilot = mpilot
        self.weight = mweight
        self.location = mlocation


    def get_df_by_position(self,mposition):
        df_to_return=[]
        for dataf in self.data:
            if dataf.position == mposition:
                df_to_return.append(dataf.df)
        return df_to_return


class Sections():
    def __repr__(self):
        return str(self.__dict__)

    def __init__(self):

        self.id = id_generator()
        self.type = None
        self.start = None
        self.end = None
        self.version = 1 # version of the Sections model


class Data_File():
    def __repr__(self):
        return str(self.__dict__)

    def __init__(self ,mfilePath , mdevice , mposition):
        logger.info("Data_File ")

        self.version = 1 # version of the Data_File model
        self.file_path = mfilePath
        self.file_date = None
        self.file_sha1 = None
        self.device = mdevice
        self.device_sn = None       # serial number of the devices
        self.device_param = None
        self.position = mposition       # serial number of the devices
        
        self.df = None

        self.file_sha1 = sha256sum(self.file_path)

        self.file_date = time.ctime(os.path.getctime(self.file_path))

    def populate_df(self):
        logger.info("populate_df ")
        if self.device == Device.PIXRACER:
           self.df = ulog_to_df(self.file_path)

    def list_avalable_data(self):
        if self.device == Device.PIXRACER:
           return ulog_list_data(self.file_path)

    def populated_device_param(self):
        if self.device == Device.PIXRACER:
            self.device_param = ulog_param(self.file_path)

