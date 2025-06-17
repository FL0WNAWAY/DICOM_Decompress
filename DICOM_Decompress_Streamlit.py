import os
import pydicom
import streamlit as st
from pydicom.uid import ExplicitVRLittleEndian
from tempfile import TemporaryDirectory
from io import BytesIO
import zipfile


st.set_page_config(page_title="DICOM Decompressor", layout="centered")
st.title("📦 DICOM Decompression Tool")

# File uploader
uploaded_files = st.file_uploader(
    "Upload compressed DICOM files (.dcm):",
    # type=["dcm"],
    accept_multiple_files=True
)

# Decompress button
if st.button("Decompress"):
    if not uploaded_files:
        st.warning("Please upload at least one DICOM file.")

    else:
        with TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "decompressed")
            os.makedirs(output_dir, exist_ok=True)

            for uploaded_file in uploaded_files:
                try:
                    # Save uploaded file temporarily
                    file_path = os.path.join(tmpdir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # Read and decompress
                    ds = pydicom.dcmread(file_path)
                    pixel_array = ds.pixel_array  # trigger decompression
                    ds.PixelData = pixel_array.tobytes()

                    # Set uncompressed format
                    ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
                    ds.is_implicit_VR = False
                    ds.is_little_endian = True

                    # Save with -decomp suffix
                    name, ext = os.path.splitext(uploaded_file.name)
                    new_name = f"{name}-decomp{ext or '.dcm'}"
                    save_path = os.path.join(output_dir, new_name)
                    ds.save_as(save_path)

                    st.success(f"✅ Decompressed: {new_name}")
                except Exception as e:
                    st.error(f"❌ Failed: {uploaded_file.name} — {e}")

            # Create in-memory zip of decompressed files
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for root, _, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, arcname=file)
            zip_buffer.seek(0)

            st.download_button(
                label="📁 Download All Decompressed Files as ZIP",
                data=zip_buffer,
                file_name="decompressed_dicoms.zip",
                mime="application/zip"
            )