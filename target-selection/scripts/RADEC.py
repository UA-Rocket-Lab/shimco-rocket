# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 11:04:00 2024

@author: Owner
"""

import pandas as pd
import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import AltAz, EarthLocation, SkyCoord  # High-level coordinates




#add returned value to each column

def Nov1pm(target, location):
    time = Time("2026-11-02 03:00:00")
    altaz = OB_star.transform_to(AltAz(obstime=time, location=white_sands))
    return altaz.alt

def Nov2am(target, location):
    time = Time("2026-11-02 10:00:00")
    altaz = OB_star.transform_to(AltAz(obstime=time, location=white_sands))
    return altaz.alt

def Feb1pm(target, location):
    time = Time("2027-02-02 02:00:00")
    altaz = OB_star.transform_to(AltAz(obstime=time, location=white_sands))
    return altaz.alt

def Feb2am(target, location):
    time = Time("2027-02-02 09:00:00")
    altaz = OB_star.transform_to(AltAz(obstime=time, location=white_sands))
    return altaz.alt
    


OBlist = pd.read_excel('C:\\Users\\Owner\\Documents\\internship 2 (science part)\\OBstars\\OBlist.xlsx')
white_sands = EarthLocation(lat=32.50 * u.deg, lon=-106.61 * u.deg, height=1460 * u.m)

#iterate through each column

for index, row in OBlist.iterrows():
    
    #read name of object
    OBstar = 'GAIA DR3 ' + str(row['DR3 ID'])
    
    #search up object in database and create a skycoord object
    OB_star = SkyCoord.from_name(OBstar)
    
    #execute four functions
    OBlist.at[index, 'Altitude at 9PM, 11/1'] = Nov1pm(OB_star, white_sands).degree
    OBlist.at[index, 'Altitude at 4AM, 11/2'] = Nov2am(OB_star, white_sands).degree
    OBlist.at[index, 'Altitude at 9PM, 2/1'] = Feb1pm(OB_star, white_sands).degree
    OBlist.at[index, 'Altitude at 4AM, 2/2'] = Feb2am(OB_star, white_sands).degree

OBlist.to_excel('C:\\Users\\Owner\\Documents\\internship 2 (science part)\\OBstars\\OBstarlist.xlsx')

    




