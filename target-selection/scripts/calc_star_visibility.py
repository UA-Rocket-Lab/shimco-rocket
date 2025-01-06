import numpy as np
import warnings
import astropy.units as u
from astropy.time import Time
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun

def calc_nighttime_fracs(GAL_LON, GAL_LAT):

    WHITE_SANDS_LOC = EarthLocation(lat=32.50 * u.deg, lon=-106.61 * u.deg, height=1460 * u.m)
    START_DATES = [Time('2026-10-01'),Time('2026-11-01'),Time('2026-12-01'),Time('2027-01-01'),Time('2027-02-01'),Time('2027-03-01')]
    END_DATES = [Time('2026-10-31'),Time('2026-11-30'),Time('2026-12-31'),Time('2027-01-31'),Time('2027-02-28'),Time('2027-03-31')]
    DAILY_SAMPLES = 24

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # star = SkyCoord.from_name(star_name)
        star = SkyCoord(l=GAL_LON * u.deg, b=GAL_LAT * u.deg, frame='galactic')

        night_fracs = []
        for start, end in zip(START_DATES, END_DATES):

            # Apply geometries
            dates = Time(np.linspace(Time(start).mjd, Time(end).mjd, int((end - start).jd * DAILY_SAMPLES)), format='mjd')
            altaz = AltAz(obstime=dates, location=WHITE_SANDS_LOC)
            staralt = star.transform_to(altaz).alt.deg
            sunalt = get_sun(dates).transform_to(altaz).alt.deg 

            # Create masks
            nighttime = (sunalt <= 0) # neglects curvature of the Earth; we don't want to observe that close to the horizon anyways
            visible = (staralt > 0)
            night_frac = np.sum(visible & nighttime) / np.sum(nighttime) * 100
            night_fracs.append(night_frac)

        return night_fracs

arr = np.genfromtxt('../ob_catalogue/ob_catalogue.csv', delimiter=',', dtype='str')[:,:-1]

nighttime_frac_arr = np.zeros((arr.shape[0],6))
for i in range(arr.shape[0]):
    nighttime_frac_arr[i,:] = calc_nighttime_fracs(float(arr[i,2]), float(arr[i,3]))

arr = np.column_stack((arr, nighttime_frac_arr.astype('int')))
np.savetxt('../ob_catalogue/temp_ob_catalogue.csv', arr, delimiter=',', fmt="%s")