# %%
import numpy as np
import rasterio
from Py6S import *

# %%
def atmospheric_correction(band, wavelength, s):
    # Set the wavelength
    s.wavelength = Wavelength(wavelength)
    # Configure atmospheric profile, aerosol profile, and ground reflectance
    s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
    s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Maritime)
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.2)
    # Set geometry parameters
    s.geometry = Geometry.User()
    s.geometry.solar_z = 30  # Example solar zenith angle
    s.geometry.solar_a = 0   # Example solar azimuth angle
    s.geometry.view_z = 0    # Example viewing zenith angle
    s.geometry.view_a = 0    # Example viewing azimuth angle

    # Run the simulation
    s.run()

    # Retrieve the atmospheric correction factor
    coeff = s.outputs.transmittance_global_gas.total  # This is more reliable for atmospheric correction

    # Print debug information
    print("Transmittance Global Gas Total:", coeff)

    # Ensure valid coefficient
    coeff = np.where(coeff == 0, np.nan, coeff)
    
    # Apply atmospheric correction
    corrected_band = np.divide(band, coeff, out=np.zeros_like(band, dtype=float), where=coeff!=0)
    
    return corrected_band

# Load the Sentinel-2 image
input_file = r'C:\Studium\2. Semester\Application Development (GIS)\Python\Final_Project\L1C_Imagery\Florence.tiff'
output_file = r'C:\Studium\2. Semester\Application Development (GIS)\Python\Final_Project\L2A_Imagery\corrected_Image.tiff'

# Initialize the Py6S model
s = SixS()

# Wavelengths for Sentinel-2 bands (example wavelengths)
wavelengths = {
    1: 0.443,  # Band 1 - Coastal aerosol
    2: 0.490,  # Band 2 - Blue
    3: 0.560,  # Band 3 - Green
    4: 0.665,  # Band 4 - Red
    5: 0.705,  # Band 5 - Vegetation red edge
    6: 0.740,  # Band 6 - Vegetation red edge
    7: 0.783,  # Band 7 - Vegetation red edge
    8: 0.842,  # Band 8 - NIR
    9: 0.865,  # Band 8A - Narrow NIR
    10: 0.945, # Band 9 - Water vapour
    11: 1.373, # Band 10 - SWIR - Cirrus
    12: 1.610, # Band 11 - SWIR
    13: 2.190  # Band 12 - SWIR
}

# Read the input file
with rasterio.open(input_file) as src:
    profile = src.profile
    num_bands = src.count

    # Create an empty array to store corrected bands
    corrected_bands = np.zeros((num_bands, src.height, src.width), dtype=np.float32)

    # Apply atmospheric correction to each band
    for i in range(1, num_bands + 1):
        band = src.read(i).astype(float)
        if i in wavelengths:
            wavelength = wavelengths[i]
            corrected_band = atmospheric_correction(band, wavelength, s)
            corrected_bands[i - 1] = corrected_band
        else:
            print(f"Wavelength for band {i} not found. Skipping atmospheric correction for this band.")
            corrected_bands[i - 1] = band

# Ensure no NaN values are saved to the output
corrected_bands = np.nan_to_num(corrected_bands, nan=0.0, posinf=0.0, neginf=0.0)

# Update the profile to reflect the correct data type and format
profile.update(
    dtype=rasterio.float32,
    count=num_bands,
    compress='lzw'
)

# Save the corrected image
with rasterio.open(output_file, 'w', **profile) as dst:
    for i in range(num_bands):
        dst.write(corrected_bands[i], i + 1)

# Script for EO-Browser to downlead a tiff that contains all 12 Bands
'''
//VERSION=3
function setup() {
  return {
    input: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"],
    output: { bands: 12 }
  };
}

function evaluatePixel(sample) {
  return Object.values(sample);
}
'''