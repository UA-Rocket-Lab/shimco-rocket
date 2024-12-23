"""
Author: Cole Meyer

Description:
This script generates and analyzes simulated astronomical spectra, including Doppler broadening corrections, 
scaling factor fitting, integrated flux calculations, and interactive plotting with toggles for data visibility and offsets.
"""

# Constants
THEOR_TEMP = '1000K'
FIMS_RESOLVING_POWER = 2000
SHIMCO_RESOLVING_POWER = 115000
noise_level = 0.3
offset = 1

is_offset_added = False
is_SHIMCO_visible = True

# Imports
import numpy as np
import matplotlib.pyplot as plt
from astropy.modeling import models
from scipy.optimize import minimize
from matplotlib.widgets import Button
from scipy.ndimage import gaussian_filter1d

# Functions
def generate_spectrum(wavelength, line_center, line_height, line_fwhm, resolving_power):
    instrument_fwhm = np.mean(line_center) / resolving_power
    combined_fwhm = np.sqrt(line_fwhm**2 + instrument_fwhm**2)
    sigma = [f / (2 * np.sqrt(2 * np.log(2))) for f in combined_fwhm]
    flux = np.zeros_like(wavelength)
    for center, sig, height in zip(line_center, sigma, line_height):
        flux += models.Gaussian1D(amplitude=height, mean=center, stddev=sig)(wavelength)
    sigma_instrument = instrument_fwhm / (2 * np.sqrt(2 * np.log(2)))
    return gaussian_filter1d(flux, sigma=sigma_instrument / (wavelength[1] - wavelength[0]))

def fit_scaling_factor(wavelength1, wavelength2, real_data1, real_data2, line_center1, line_height1, line_fwhm1, line_center2, line_height2, line_fwhm2):
    def residuals(factor):
        scaled_flux1 = generate_spectrum(wavelength1, line_center1, factor * line_height1, line_fwhm1, FIMS_RESOLVING_POWER)
        scaled_flux2 = generate_spectrum(wavelength2, line_center2, factor * line_height2, line_fwhm2, FIMS_RESOLVING_POWER)
        return np.sum((scaled_flux1 - real_data1)**2) + np.sum((scaled_flux2 - real_data2)**2)
    result = minimize(residuals, x0=1.0, method='Nelder-Mead')
    return result.x[0]

def reset_y_limits(axis):
    y_data = [line.get_ydata() for line in axis.lines if line.get_visible()]
    if y_data:
        all_y = [y for sublist in y_data for y in sublist]
        axis.set_ylim([1.25 * min(all_y), 1.1 * max(all_y)])
        fig.canvas.draw()

def toggle_offset(event):
    global is_offset_added
    for j in range(2):
        for line in line_list[j]:
            updated_flux = line.get_ydata() + offset if not is_offset_added else line.get_ydata() - offset
            line.set_ydata(updated_flux)
    is_offset_added = not is_offset_added
    offset_button.label.set_text('Remove Offset' if is_offset_added else 'Add Offset')
    reset_y_limits(ax[0])
    reset_y_limits(ax[1])

def toggle_SHIMCO(event):
    global is_SHIMCO_visible
    for j in range(2):
        line_list[j][2].set_visible(not line_list[j][2].get_visible())
    is_SHIMCO_visible = not is_SHIMCO_visible
    shimco_button.label.set_text('Hide SHIMCO' if is_SHIMCO_visible else 'Show SHIMCO')
    reset_y_limits(ax[0])
    reset_y_limits(ax[1])

# Main Workflow
data = np.column_stack(np.genfromtxt(f'../theoretical_spectra/uncor_{THEOR_TEMP}.peaks', dtype='str')[:, [2, 3, 5]]).astype(float).T
data = np.delete(data, np.where(np.abs(data[:, 0]) > 1e5), axis=0)
chan1, chan2 = data[data[:, 0] < 1500], data[data[:, 0] > 1500]

# Correct for Doppler broadening
kb, m0, c = 1.381e-23, 3.347725e-27, 3e8
chan1[:, 2] = 2 * chan1[:, 0] * np.sqrt(2 * np.log(2) * kb * float(THEOR_TEMP[:-1]) / (m0 * c**2))
chan2[:, 2] = 2 * chan2[:, 0] * np.sqrt(2 * np.log(2) * kb * float(THEOR_TEMP[:-1]) / (m0 * c**2))

# Generate wavelength grids and noisy data
wavelength1, wavelength2 = np.linspace(np.min(chan1[:, 0]), np.max(chan1[:, 0]), 10000), np.linspace(np.min(chan2[:, 0]), np.max(chan2[:, 0]), 10000)
real_data1 = generate_spectrum(wavelength1, chan1[:, 0], chan1[:, 1], chan1[:, 2], FIMS_RESOLVING_POWER)
real_data2 = generate_spectrum(wavelength2, chan2[:, 0], chan2[:, 1], chan2[:, 2], FIMS_RESOLVING_POWER)
real_data1 += np.random.normal(0, noise_level * np.max(real_data1), len(wavelength1))
real_data2 += np.random.normal(0, noise_level * np.max(real_data2), len(wavelength2))

# Fit scaling factor
scal_factor = fit_scaling_factor(wavelength1, wavelength2, real_data1, real_data2, chan1[:, 0], chan1[:, 1], chan1[:, 2], chan2[:, 0], chan2[:, 1], chan2[:, 2])

# Generate fitted and SHIMCO data
fitted_flux1 = generate_spectrum(wavelength1, chan1[:, 0], scal_factor * chan1[:, 1], chan1[:, 2], FIMS_RESOLVING_POWER)
fitted_flux2 = generate_spectrum(wavelength2, chan2[:, 0], scal_factor * chan2[:, 1], chan2[:, 2], FIMS_RESOLVING_POWER)
shimco_flux1 = generate_spectrum(wavelength1, chan1[:, 0], scal_factor * chan1[:, 1], chan1[:, 2], SHIMCO_RESOLVING_POWER)
shimco_flux2 = generate_spectrum(wavelength2, chan2[:, 0], scal_factor * chan2[:, 1], chan2[:, 2], SHIMCO_RESOLVING_POWER)

# Integrate specific flux density
integrated_flux1 = np.trapz(fitted_flux1, wavelength1)
integrated_flux2 = np.trapz(fitted_flux2, wavelength2)
total_integrated_flux = integrated_flux1 + integrated_flux2

# Create interactive plot

fig, ax = plt.subplots(2, 1, figsize=(13, 8), sharex=False)

flux_scale_fac = 1 / (4*np.pi*(4.255e10)) * 1e15 # divide flux density by 4pi steradians to obtain surface brightness, then convert to arcsec^-2

fitted_area1 = np.trapz(fitted_flux1, wavelength1)
shimco_area1 = np.trapz(shimco_flux1, wavelength1)
line1, = ax[0].plot(wavelength1, flux_scale_fac*real_data1, c='k', alpha=0.6, label=f'Simulated FIMS Spectrum (R={FIMS_RESOLVING_POWER})')
line2, = ax[0].plot(wavelength1, flux_scale_fac*fitted_flux1, c='b', label=f'Fitted Theoretical Spectrum (R={FIMS_RESOLVING_POWER})')
line3, = ax[0].plot(wavelength1, flux_scale_fac*shimco_flux1 * (fitted_area1 / shimco_area1), c='r', linestyle='-', label='Noiseless SHIMCO Spectrum (R=115000)')
ax[0].set_title(f"Channel 1, T = {THEOR_TEMP}, Integrated Surface Brightness$={int(flux_scale_fac*integrated_flux1*1e1)/1e1}\\times10^{{-15}}$ erg s$^{{-1}}$ cm$^{{-2}}$ arcsec$^{{-2}}$ ")
ax[0].set_ylabel("Surface Brightness\n($\\times10^{-15}$ erg s$^{{-1}}$ cm$^{{-2}}$ arcsec$^{-2}$ $\\rm\AA^{{-1}}$)")
ax[0].legend(loc=1, fontsize=10)
line_list = [[line1, line2, line3]]

fitted_area2 = np.trapz(fitted_flux2, wavelength2)
shimco_area2 = np.trapz(shimco_flux2, wavelength2)
line1, = ax[1].plot(wavelength2, flux_scale_fac*real_data2, c='k', alpha=0.6, label=f'Simulated FIMS Spectrum (R={FIMS_RESOLVING_POWER})')
line2, = ax[1].plot(wavelength2, flux_scale_fac*fitted_flux2, c='b', label=f'Fitted Theoretical Spectrum (R={FIMS_RESOLVING_POWER})')
line3, = ax[1].plot(wavelength2, flux_scale_fac*shimco_flux2 * (fitted_area2 / shimco_area2), c='r', linestyle='-', label='Noiseless SHIMCO Spectrum (R=115000)')
ax[1].set_title(f"Channel 2, T = {THEOR_TEMP}, Integrated Surface Brightness$={int(flux_scale_fac*integrated_flux2*1e1)/1e1}\\times10^{{-15}}$ erg s$^{{-1}}$ cm$^{{-2}}$ arcsec$^{{-2}}$ ")
ax[1].set_xlabel(r"Wavelength ($\rm\AA$)")
ax[1].set_ylabel("Surface Brightness\n($\\times10^{-15}$ erg s$^{{-1}}$ cm$^{{-2}}$ arcsec$^{-2}$ $\\rm\AA^{{-1}}$)")
ax[1].legend(loc=1, fontsize=10)
line_list.append([line1, line2, line3])

ax_button = plt.axes([0.8, 0.8, 0.15, 0.075])
offset_button = Button(ax_button, 'Add Offset')
offset_button.label.set_fontsize(16)
offset_button.color = 'lightcoral'
offset_button.hovercolor = 'tomato'
offset_button.on_clicked(toggle_offset)

ax_button = plt.axes([0.8, 0.7, 0.15, 0.075])
shimco_button = Button(ax_button, 'Hide SHIMCO')
shimco_button.label.set_fontsize(16)
shimco_button.color = 'lightblue'
shimco_button.hovercolor = 'blue'
shimco_button.on_clicked(toggle_SHIMCO)

reset_y_limits(ax[0])
reset_y_limits(ax[1])

plt.suptitle(f"Total Integrated Surface Brightness$={int(flux_scale_fac*total_integrated_flux*1e1)/1e1}\\times10^{{-15}}$ erg s$^{{-1}}$ cm$^{{-2}}$ arcsec$^{{-2}}$ ")
plt.subplots_adjust(bottom=0.1, right=0.75)
plt.show()