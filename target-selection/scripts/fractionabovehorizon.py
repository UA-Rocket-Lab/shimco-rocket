# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 10:54:02 2024

@author: Owner
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_sun

#set location, object, and y-axis entries
white_sands = EarthLocation(lat=32.50 * u.deg, lon=-106.61 * u.deg, height=1460 * u.m)
OBstar = 'HD 226868'
OB_star = SkyCoord.from_name(OBstar)
percentage = [] 

#set date range
start_date = Time('61345', format='mjd')
end_date = Time('61465', format='mjd')

#set up the loop
current_date = start_date
while current_date <= end_date:
    start_time = 0
    current_time = start_time
    end_time = 1
    ticks = 0
    sunticks = 0
    while current_time < end_time:
        
        #find the altitude of the OB star and the sun
        altaz = OB_star.transform_to(AltAz(obstime=(current_date + current_time), location=white_sands))
        sunposition = get_sun(current_date + current_time)
        sunaltitude = sunposition.transform_to(AltAz(obstime=(current_date+current_time),location = white_sands))        
        
        #check if it's night
        if sunaltitude.alt.degree < 0:
            #check if object is above the horizon
            if altaz.alt.degree > 0:
                ticks += 1
            sunticks += 1           
        #get a percentage for each date before resetting current_time 
        if current_time >= 0.99:
            percentage.append(100 * ticks / sunticks)         
        current_time += 0.01       
    current_date += 1
    
#get a list of all dates in our range, and convert to ymd format
datesmjd = np.linspace(61345, 61465, 120)
datesiso = []
for x in datesmjd:
    t = Time(x, format='mjd')
    datesiso.append(t.to_datetime())

#create and format the plot
plt.plot(datesiso, percentage)
plt.xticks(rotation = 45)
plt.xlim(20758,20878)
plt.ylim(0, 100)
plt.xlabel("Day in mjd format")
plt.ylabel("Percentage of time the star is up")
plt.xticks([20758, 20788, 20819, 20850, 20878]) 
plt.show()