import biometric_sdk

# Initialize the biometric device
device = biometric_sdk.Device()

# Capture fingerprint image
fingerprint_image = device.capture_fingerprint()

# Convert image to .tif using Pillow
from PIL import Image
image_pil = Image.fromarray(fingerprint_image)  # Convert to a suitable format
tif_path = 'fingerprint.tif'
image_pil.save(tif_path, format='TIFF')

# Clean up
device.close()

