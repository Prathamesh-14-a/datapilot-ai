import os
import cloudinary
import cloudinary.uploader
import streamlit as st
from uuid import uuid4
from pathlib import Path

cloudinary.config(
    cloud_name=st.secrets["CLOUD_NAME"],
    api_key=st.secrets["CLOUDINARY_API_KEY"],
    api_secret=st.secrets["CLOUDINARY_API_SECRET"],
    secure=True,
)


def upload_resume(uploaded_file):
    """
    Upload a resume PDF to Cloudinary.

    Returns:
        secure_url
        public_id
    """

    extension = Path(uploaded_file.name).suffix.lower()

    unique_filename = f"{uuid4()}{extension}"

    result = cloudinary.uploader.upload(
        uploaded_file,
        resource_type="raw",
        folder="datapilot_ai/resumes",
        public_id=unique_filename,
        overwrite=False,
    )

    return result["secure_url"], result["public_id"]