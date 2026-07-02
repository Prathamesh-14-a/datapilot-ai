import os
import cloudinary
import cloudinary.uploader
import streamlit as st
from uuid import uuid4
from pathlib import Path
import io

cloudinary.config(
    cloud_name=st.secrets["CLOUD_NAME"],
    api_key=st.secrets["CLOUDINARY_API_KEY"],
    api_secret=st.secrets["CLOUDINARY_API_SECRET"],
    secure=True,
)


def upload_resume(file_bytes, filename=None):
    """
    Upload a resume PDF to Cloudinary from raw bytes.

    Args:
        file_bytes: bytes of the PDF file
        filename: original filename (optional)

    Returns:
        secure_url, public_id
    """

    extension = Path(filename).suffix.lower() if filename else ".pdf"

    unique_filename = f"{uuid4()}"

    file_obj = io.BytesIO(file_bytes)
    # set a name attribute so Cloudinary can infer filename if needed
    file_obj.name = f"{unique_filename}{extension}"

    result = cloudinary.uploader.upload(
        file_obj,
        resource_type="raw",
        folder="datapilot_ai/resumes",
        public_id=unique_filename,
        overwrite=False,
    )

    return result["secure_url"], result["public_id"]