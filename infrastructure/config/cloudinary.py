import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_profile_image(file):
    result = cloudinary.uploader.upload(
        file.file,
        folder="profile_pictures"
    )

    return result["secure_url"]