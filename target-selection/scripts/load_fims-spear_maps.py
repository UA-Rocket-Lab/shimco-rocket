import os
import numpy as np
import healpy as hp
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.table import Table
from astroquery.mast import Observations

download_data = True
map_name = 'mccm_fims-spear_fims-ap100-n064_sky-starless_long_v1.0_hp-map-hsi.fits.gz'

if download_data:
    uri = 'mast:MCCM/fims-spear/fims/hp-map-hsi/'+map_name
    Observations.download_file(uri)
    file_highres = os.path.basename(uri)

######################

fims_map = Table.read(map_name, 
                    hdu=1).filled(np.nan)

with fits.open(map_name) as hdul:
    crval = hdul[1].header['CRVAL1']
    cdelt = hdul[1].header['CDELT1']
    bins = len(fims_map['INTEN_BSUB'][0])
    lwave = np.arange(0, bins)*cdelt+crval

mask = ((lwave > 1395) & (lwave < 1405)) | ((lwave > 1605) & (lwave < 1615))
integrated_map = np.sum(fims_map['INTEN_BSUB'][:,mask], axis=1)

#######################

def get_healpy_map_value(lat, lon, map_array, coord_order='G'):
    """
    Retrieves the value from a HEALPix map at the specified latitude and longitude.

    Parameters:
    - lat (float): Latitude in degrees (-90 to 90).
    - lon (float): Longitude in degrees (0 to 360).
    - map_array (array-like): 1D array representing the HEALPix map.
    - coord_order (str): Coordinate system of the map ('G' for Galactic, 'C' for Celestial).

    Returns:
    - float: The value from the map at the specified coordinates.

    Raises:
    - ValueError: If the map length is not compatible with a valid nside.
    """
    # Calculate nside from the length of the map
    npix = len(map_array)
    nside_float = np.sqrt(npix / 12)
    nside = int(nside_float)

    if not hp.isnsideok(nside):
        raise ValueError(f"Invalid nside calculated from map length {npix}. Ensure the length is 12*nside^2 with nside as a power of 2.")

    # Convert latitude and longitude to theta and phi in radians
    theta = np.radians(90.0 - lat)  # colatitude
    phi = np.radians(lon)            # longitude

    # Get the pixel index
    pix = hp.ang2pix(nside, theta, phi, nest=False)

    # Return the map value at the pixel
    return map_array[pix]

PIX_PER_DEG = 1
regrid = np.zeros((PIX_PER_DEG*180,PIX_PER_DEG*360))
lats = np.linspace(-90,90,regrid.shape[0])
lons = np.linspace(0,360,regrid.shape[1])
for lat in range(regrid.shape[0]):
    for lon in range(regrid.shape[1]):
        regrid[lat,lon] = get_healpy_map_value(lats[lat],lons[lon],integrated_map)

hp.mollview(integrated_map, coord='G', max=5e5, unit='photon cm-2 s-1 sr-1', title='') # Galactic coordinates
plt.show()

plt.imshow(regrid, vmin=-4900, vmax=5e5, origin='lower')
plt.colorbar()
plt.show()

np.savetxt('../bp_integrated_h2.csv', regrid, delimiter=',')