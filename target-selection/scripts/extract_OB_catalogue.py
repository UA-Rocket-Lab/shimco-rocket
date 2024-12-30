"""
Author: Cole Meyer

Description:
This script queries the SIMBAD astronomical database for O-type and B-type stars. It processes the retrieved data to include key stellar parameters such as coordinates, spectral type, and radial velocity, and saves the results to a CSV file.
"""

from astropy.table import vstack
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import re

# Configure Simbad settings
Simbad.add_votable_fields('sptype', 'plx', 'rvz_radvel', 'flux(V)', 'ids')
Simbad.ROW_LIMIT = 0  # Load all available rows
Simbad.TIMEOUT = 360  # Set a generous timeout to ensure large queries complete

# Query for O-type and B-type stars
print('Loading O-type stars...')
o_stars = Simbad.query_criteria("sptype='O*'")
print('Loading B-type stars...')
b_stars = Simbad.query_criteria("sptype='B*'")

temp_stars = np.genfromtxt('../ob_catalogue/extra_stars.csv', delimiter=',', dtype='str', encoding='utf-8-sig') # stars identified by Jo
extra_stars = Simbad.query_object(temp_stars[0][0])
for star in temp_stars[1:]:
    temp = Simbad.query_object(star[0])
    if temp is not None:
        extra_stars = vstack([extra_stars, temp])

# Combine and process star data
temp_stars = np.concatenate([a for a in (o_stars, b_stars) if a is not None])
temp_stars = np.concatenate((temp_stars, extra_stars))
stars = np.zeros((len(temp_stars), 9)).astype('str')

if temp_stars is not None:
    for i, star in enumerate(temp_stars):
        if star['SP_TYPE'] == 'O-rich' or not star['RA'] or not star['DEC'] or not star['SP_QUAL']:
            continue
        
        coord = SkyCoord(ra=star['RA'], dec=star['DEC'], unit=(u.hourangle, u.deg), frame='icrs')
        galactic = coord.galactic

        stars[i, :] = np.array([
            star['MAIN_ID'].replace('#', ''),  # Star ID
            star['FLUX_V'],                    # Apparent Magnitude
            galactic.l.value,                  # Galactic Longitude
            galactic.b.value,                  # Galactic Latitude
            star['SP_TYPE'],                   # Spectral Type
            star['SP_QUAL'],                   # Spectral Quality
            1 / (star['PLX_VALUE'] / 1000),    # Distance (pc)
            star['RVZ_RADVEL'],                # Radial Velocity
            star['SP_BIBCODE']                 # Bibliography Code
        ])

# Filter and clean data
stars = stars[stars[:, 0] != '0.0'].copy()
stars = stars[stars[:, 5].argsort()]
stars = stars[~np.isnan(stars[:, [1, 6, 7]].astype(float)).any(axis=1)]

print('Subbing for Gaia DR3 names...')

found_list = []
for i, name in enumerate(stars[:,0]):

    if name[:3] == 'GEN': # pound symbols are tough to include in CSVs
        name = 'GEN#' + name[3:]

    star = Simbad.query_object(name)

    alternative_names = star[0]['IDS']
    alt_name_list = [name.strip() for name in alternative_names.split('|')] if alternative_names else []

    found = False
    for alt_name in alt_name_list:
        if alt_name[:8] == 'Gaia DR3':
            found_list.append(alt_name)
            found = True

    if not found:
        found_list.append(name)

stars[:,0] = np.array(found_list)
stars[:,0] = [re.sub(r'\s+', ' ', name.strip()) for name in stars[:, 0]]  # Normalize star names

# Save the processed data
output_file = '../ob_catalogue/ob_catalogue.csv'
np.savetxt(output_file, stars, fmt='%s', delimiter=',')
print(f'Found {len(stars)} stars total. Data saved to {output_file}')