import os
import requests
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from .file_utils import allowed_file

def download_and_save_image(url, upload_folder, allowed_extensions):
    """
    Download an image from a URL and save it to the upload folder.
    Returns the filename and the URL to access the uploaded file.
    """
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))
    ext = img.format.lower()
    if ext not in allowed_extensions:
        ext = 'png'
    filename = secure_filename(os.path.basename(url).split('?')[0])
    if not allowed_file(filename, allowed_extensions):
        filename = f"image_{abs(hash(url))}.{ext}"
    save_path = os.path.join(upload_folder, filename)
    img.save(save_path)
    return filename, f'/uploads/{filename}'
