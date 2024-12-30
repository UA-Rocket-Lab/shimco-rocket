"""
Author: Cole Meyer

Description:
This script queries the MAST archive for archival IUE spectra of OB stars using SiMBAD. It retrieves and processes SWP observations, extracts wavelength and flux data, and saves the spectra to CSV files.
"""

import argparse
from astropy.coordinates import SkyCoord
from astroquery.mast import Observations
from astropy import units as u
from astropy.io import fits
import numpy as np
import time

ob_stars = np.genfromtxt('../ob_catalogue/ob_catalogue.csv', delimiter=',', dtype='str')

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Query IUE spectra for OB stars.")
parser.add_argument('--start_target', type=str, help='Specific target name to process (optional)', default=None)
args = parser.parse_args()

if args.start_target:
    ob_stars = ob_stars[np.where(ob_stars[:,0] == args.start_target.replace('_',' '))[0][0]:,:]

print('NOTE: takes awhile to run due to MAST query response time')
t0 = time.time()

for i, (target_name, gal_lon, gal_lat) in enumerate(zip(ob_stars[:,0], ob_stars[:,2], ob_stars[:,3])):
    if target_name[:3] == 'GEN': # pound symbols are tough to include in CSVs
        target_name = 'GEN#' + target_name[3:]

    obs_table = Observations.query_criteria(objectname=target_name,
                                          obs_collection="IUE")

    if np.array(obs_table).shape[0] == 0:
        time_left = (time.time() - t0) * (1 / ((i+1) / len(ob_stars[:,0])) - 1)
        print('failed',target_name,str(int(1000*i/len(ob_stars[:,0])/10))+'%','ETA:',str(int(time_left)),'s')
        continue

    data_products = Observations.get_product_list(obs_table)
    swp_products = data_products[np.char.startswith(np.array(data_products['obs_id']), 'swp')]

    if np.array(swp_products).shape[0] == 0:
        time_left = (time.time() - t0) * (1 / ((i+1) / len(ob_stars[:,0])) - 1)
        print('failed',target_name,str(int(1000*i/len(ob_stars[:,0])/10))+'%','ETA:',str(int(time_left)),'s')
        continue

    manifest = Observations.download_products(swp_products,
                                              productType='SCIENCE',
                                              extension=".fits")

    if manifest is None:
        time_left = (time.time() - t0) * (1 / ((i+1) / len(ob_stars[:,0])) - 1)
        print('failed',target_name,str(int(1000*i/len(ob_stars[:,0])/10))+'%','ETA:',str(int(time_left)),'s')
        continue

    filenames = manifest['Local Path']

    wav = []
    flux = []
    for filename in filenames:
        with fits.open(filename) as hdulist:
            spectrum = hdulist[1].data

        wav.append(spectrum[0][0])
        flux.append(spectrum[0][1])

    ### SAVE DATA
    data = np.column_stack((np.array(wav), np.array(flux)))
    fmt_name = target_name.replace(' ','_')
    np.savetxt(f'../ob_catalogue/ob_catalogue_spectra/{fmt_name}.csv', data, delimiter=',')

    time_left = (time.time() - t0) * (1 / ((i+1) / len(ob_stars[:,0])) - 1)
    print('succeeded',target_name,str(int(1000*i/len(ob_stars[:,0])/10))+'%','ETA:',str(int(time_left)),'s')