# Py6s must be insatlled and the code must be run in its environment to execute properly
# 1. to install py6s run the following command in the anaconda prompt "conda create -n py6s-env -c conda-forge py6s"
# 2. then activate the environment with "py6s-env activate"
# 3. make sure the IDE uses this environment so that the 6S executable is avalible

import rasterio
import numpy as np
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, GroundReflectance
import os

# Set the path to the 6S executable
SixS.executable = r'C:\Users\bosquo\anaconda3\envs\py6s-env\Library\bin\sixs.exe'

# Load Sentinel-2 image using rasterio
input_file = r'C:\Studium\2. Semester\Application Development (GIS)\Python\Final_Project\L1C_Imagery\2024-06-18-00_00_2024-06-18-23_59_Sentinel-2_L1C_True_color.tiff'
output_file = r'C:\Studium\2. Semester\Application Development (GIS)\Python\Final_Project\L2A_Imagery\corrected_Image.tiff'

with rasterio.open(input_file) as src:
    # Read image bands
    bands = src.read()
    profile = src.profile

# Define a function for atmospheric correction using Py6S
def atmospheric_correction(band, wavelength, s):
    s.wavelength = Wavelength(wavelength)
    s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
    s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Maritime)
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.2)
    s.geometry = Geometry.User()
    s.geometry.solar_z = 30   # Example solar zenith angle
    s.geometry.solar_a = 0    # Example solar azimuth angle
    s.geometry.view_z = 0     # Example viewing zenith angle
    s.geometry.view_a = 0     # Example viewing azimuth angle

    s.run()
    
    # Get the atmospheric correction factor
    coeff = s.outputs.atmospheric_intrinsic_reflectance
    # Avoid divide by zero error
    coeff = np.where(coeff == 0, np.nan, coeff)
    corrected_band = band / coeff
    return corrected_band

# Initialize Py6S
s = SixS()

# Example wavelengths for Sentinel-2 bands (in micrometers)
wavelengths = [0.4966, 0.5600, 0.6645, 0.7045, 0.7402, 0.7825, 0.8351, 0.8648, 0.9450, 1.373, 1.6137, 2.2024]

# Correct each band
corrected_bands = []
for i, band in enumerate(bands):
    corrected_band = atmospheric_correction(band, wavelengths[i], s)
    corrected_bands.append(corrected_band)

# Convert corrected bands to a numpy array
corrected_bands = np.array(corrected_bands)

# Update the profile to match the corrected data type
profile.update(dtype=rasterio.float32)

# Save the corrected image
with rasterio.open(output_file, 'w', **profile) as dst:
    dst.write(corrected_bands.astype(rasterio.float32))

print(f'Atmospheric correction complete. Corrected image saved to {output_file}')