from flask import Flask, jsonify, send_from_directory, request, send_file
import os

from utils.file_utils import ensure_folder
from utils.image_utils import download_and_save_image
from image_to_ansi import image_to_ansi, create_html, generate_simple_effect
from utils.validation import validate_brightness, validate_resolution, validate_effect_type, validate_url, ValidationError

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Ensure folders exist
ensure_folder(UPLOAD_FOLDER)
ensure_folder(STATIC_FOLDER)


@app.route('/images')
def list_images():
    """
    List all images in the 'images' directory.
    """
    image_dir = os.path.join(os.path.dirname(__file__), 'images')
    files = [f for f in os.listdir(image_dir)
             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return jsonify(files)


@app.route('/uploads')
def list_uploads():
    """
    List all uploaded images in the 'uploads' directory.
    """
    image_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    files = [f for f in os.listdir(image_dir)
             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return jsonify(files)


@app.route('/images/<path:filename>')
def serve_image(filename):
    """
    Serve an image file from the 'images' directory.
    """
    return send_from_directory('images', filename)


@app.route('/')
def serve_index():
    """
    Serve the main HTML page for the image browser.
    """
    return send_from_directory('views', 'imageBrowser.html')


@app.route('/<path:path>')
def serve_static(path):
    """
    Serve static files (e.g., JavaScript, CSS) from the root directory.
    """
    return send_from_directory('.', path)


@app.route('/static/<path:filename>')
def serve_static_files(filename):
    """
    Serve static files (e.g., favicon, images) from the static directory.
    """
    return send_from_directory(STATIC_FOLDER, filename)


@app.route('/convert/<path:filename>')
def convert_image(filename):
    """
    Convert an uploaded or stored image to ANSI art and return as HTML.
    """
    try:
        # Validate filename to prevent path traversal
        if '..' in filename or filename.startswith('/'):
            return "Invalid filename", 400

        # Validate parameters
        brightness = validate_brightness(request.args.get('brightness', '1.0'))
        resolution = validate_resolution(request.args.get('resolution', '160'))
        effect = validate_effect_type(request.args.get('effect', '-1'))

        # Find the image (sanitized paths)
        image_path = os.path.join('images', filename)
        if not os.path.exists(image_path):
            image_path = os.path.join('uploads', filename)
            if not os.path.exists(image_path):
                return "Image not found", 404

        # Ensure the path is within allowed directories
        abs_image_path = os.path.abspath(image_path)
        abs_images_dir = os.path.abspath('images')
        abs_uploads_dir = os.path.abspath('uploads')

        if not (abs_image_path.startswith(abs_images_dir) or abs_image_path.startswith(abs_uploads_dir)):
            return "Access denied", 403

        output_path = os.path.join('converted', f'{filename}.html')
        ensure_folder('converted')

        # Convert image to ANSI art with validated parameters
        ansi_art = image_to_ansi(image_path, max_width=resolution, brightness=brightness)

        # Apply effect if specified
        if effect >= 0:
            ansi_art = generate_simple_effect(ansi_art, effect)

        create_html(ansi_art, output_path, image_path)
        return send_file(output_path)

    except ValidationError as e:
        return f"Validation error: {str(e)}", 400
    except Exception as e:
        # Log error but don't expose internal details
        app.logger.error(f"Error converting image: {str(e)}")
        return "Internal server error", 500


@app.route('/update_ansi')
def update_ansi():
    """
    Generate ANSI art from an image with adjustable parameters.
    """
    try:
        image = request.args.get('image')
        if not image:
            return "Image parameter required", 400

        # Validate parameters
        brightness = validate_brightness(request.args.get('brightness', '1.0'))
        effect = validate_effect_type(request.args.get('effect', '-1'))
        max_width = validate_resolution(request.args.get('resolution', '80'))

        # Validate image path
        if '..' in image or image.startswith('/'):
            return "Invalid image path", 400

        ansi_art = image_to_ansi(image, max_width=max_width, brightness=brightness)

        if effect >= 0:
            ansi_art = generate_simple_effect(ansi_art, effect)

        return ansi_art

    except ValidationError as e:
        return f"Validation error: {str(e)}", 400
    except Exception as e:
        app.logger.error(f"Error updating ANSI: {str(e)}")
        return "Internal server error", 500


@app.route('/add_image_url', methods=['POST'])
def add_image_url():
    """
    Add an image from a URL by downloading it and saving it to the server.
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        # Validate URL
        url = validate_url(data['url'])

        filename, file_url = download_and_save_image(
            url, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
        )
        return jsonify({
            'success': True,
            'filename': filename,
            'url': file_url
        })
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error adding image from URL: {str(e)}")
        return jsonify({'error': 'Failed to add image'}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve an uploaded image file from the 'uploads' directory.
    """
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
