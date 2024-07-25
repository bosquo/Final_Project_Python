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

# Load the Sentinel-2 image band
input_file = r'C:\Studium\2. Semester\Application Development (GIS)\Python\Final_Project\L1C_Imagery\2024-06-18-00_00_2024-06-18-23_59_Sentinel-2_L1C_True_color.tiff'
output_file = r'C:\Studium\2. Semester\Application Development (GIS)\Python\Final_Project\L2A_Imagery\corrected_Image.tiff'

with rasterio.open(input_file) as src:
    band = src.read(1).astype(float)
    profile = src.profile

# Initialize the Py6S model
s = SixS()

# Example wavelength for band 4 (Red)
wavelength = 0.664

# Apply atmospheric correction
corrected_band = atmospheric_correction(band, wavelength, s)

# Ensure no NaN values are saved to the output
corrected_band = np.nan_to_num(corrected_band, nan=0.0, posinf=0.0, neginf=0.0)

# Update the profile to reflect the correct data type and format
profile.update(
    dtype=rasterio.float32,
    count=1,
    compress='lzw'
)

# Save the corrected image
with rasterio.open(output_file, 'w', **profile) as dst:
    dst.write(corrected_band, 1)

# %%
