import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


def upload_profile_image(file, user_id: str):
    result = cloudinary.uploader.upload(
        file.file,
        folder="kaira/profile-images",
        public_id=f"user-{user_id}",
        overwrite=True,
        resource_type="image",
        transformation=[
            {
                "width": 400,
                "height": 400,
                "crop": "fill",
                "gravity": "face",
            }
        ],
    )

    return result["secure_url"]