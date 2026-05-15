import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(input_path, output_path, quality=50):
    with Image.open(input_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(output_path, "JPEG", optimize=True, quality=quality)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'fileToUpload' not in request.files:
        return redirect(request.url)
    
    file = request.files['fileToUpload']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Define output filename
        output_filename = "reduced_" + filename.rsplit('.', 1)[0] + ".jpg"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Compress
        compress_image(input_path, output_path)
        
        # Get sizes for display
        original_size = os.path.getsize(input_path)
        reduced_size = os.path.getsize(output_path)
        
        return render_template('index.html', 
                               original_file=filename,
                               reduced_file=output_filename,
                               original_size=f"{original_size / 1024:.2f} KB",
                               reduced_size=f"{reduced_size / 1024:.2f} KB",
                               reduction_percent=f"{100 - (reduced_size / original_size * 100):.1f}%")
    
    return "File type not supported. Please upload an image (png, jpg, jpeg, webp).", 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
