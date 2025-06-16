# %% install required packages
pip install pydicom pylibjpeg pylibjpeg-libjpeg pylibjpeg-openjpeg

# %% DICOM decompression
import os
import pydicom
from pydicom.uid import ExplicitVRLittleEndian
from tkinter import Tk, filedialog

# Hide the root Tk window
Tk().withdraw()

# Ask user to select the compressed DICOM file
input_paths = filedialog.askopenfilenames(
    title="Select compressed DICOM files",
    filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
)

if not input_paths:
    print("No file selected. Exiting.")
    exit()

# Ask user to select output directory
output_dir = filedialog.askdirectory(
    title="Select folder to save decompressed DICOM files"
)

if not output_dir:
    print("No output folder selected. Exiting.")
    exit()

for input_path in input_paths:
    try:
        # Read the compressed DICOM file
        ds=pydicom.dcmread(input_path)

        # Trigger decompression
        pixel_array = ds.pixel_array

        # Replace compressed pixel data with decompressed raw data
        ds.PixelData = pixel_array.tobytes()

        # Update required fields for uncompressed data
        ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.is_implicit_VR = False
        ds.is_little_endian = True

        # Prepare output file path using original file name with "-decomp" appended at the end
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}-decomp{ext}"
        output_path = os.path.join(output_dir, new_name)

        # Save the decompressed DICOM
        ds.save_as(output_path)
        print(f"Saved: {output_path}")
    
    except Exception as e:
        print(f"Failed to decompress {input_path}: {e}")

print("All selected files processed.")


