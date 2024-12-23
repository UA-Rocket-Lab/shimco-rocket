# SHIMCO Project Repository

Welcome to the SHIMCO (Spatial Heterodyne Interferometric Molecular Cloud Observer) project repository. This repository contains resources, data, and scripts designed to support the development, analysis, and visualization of data related to SHIMCO's mission: observing molecular hydrogen (H2) emission from molecular clouds to understand star formation processes and cloud evolution.

---

## Directory Contents

### **Data Files**
1. **`ob_catalogue.csv`**
   - Contains cataloged data of OB stars used for SHIMCO target selection.
   - Includes:
     - Star IDs
     - Spectral types
     - Apparent magnitudes
     - Galactic coordinates
     - Radial velocities

2. **`uncor_100K.peaks`, `uncor_500K.peaks`, `uncor_1000K.peaks`, `uncor_2000K.peaks`, `uncor_3000K.peaks`**
   - Theoretical spectra for molecular hydrogen fluorescence emission at various temperatures.
   - Used for generating synthetic spectra and comparing them to observed data.

---

### **Scripts**
1. **`extract_OB_catalogue.py`**
   - Extracts and processes data from Simbad for OB stars by spectral type.
   - Outputs a cleaned CSV file containing star properties for plotting and further analysis.

2. **`plot_OB_catalogue.py`**
   - Visualizes OB star distributions in galactic coordinates.
   - Generates interactive plots for selecting and analyzing stars of interest.

3. **`get_integrated_flux.py`**
   - Computes integrated flux and surface brightness for theoretical spectra.
   - Includes convolution with the resolving power of SHIMCO and FIMS spectrographs.

---

### **Project Goals**
1. **Scientific Objectives**:
   - Examine molecular hydrogen transitions to explore the HI/H2 boundary layers in the molecular clouds.
   - Investigate star formation efficiency and molecular cloud dispersal mechanisms.

2. **Technology Development**:
   - Demonstrate the capabilities of SHIMCO's Spatial Heterodyne Spectroscopy system for future space-based missions.

3. **Educational Outcomes**:
   - Train graduate students and postdoctoral researchers in advanced UV spectroscopy techniques and sounding rocket operations.

---

### Getting Started

1. **Data Analysis**:
   - Use `extract_OB_catalogue.py` to refine star data for specific spectral types.
   - Run `plot_OB_catalogue.py` for interactive visualization and selection of observation targets.
   - Employ `get_integrated_flux.py` for analyzing synthetic and observational spectra.

2. **Resources**:
   - TBD

---

### Contributing
We welcome contributions and collaboration from the community! Please follow the standard fork-and-pull model and ensure code and data contributions are thoroughly documented.

---

For questions or concerns about the SHIMCO project codebase, contact cmmeyer@arizona.edu.
