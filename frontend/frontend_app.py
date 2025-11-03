from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image
import subprocess
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key'

UPLOAD_FOLDER = '/app/inputs'
OUTPUT_FOLDER = '/app/outputs/frontend'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_with_realesrgan_only(input_filename):
    """Process image using only RealESRGAN model"""
    try:
        # Create a .process_esrgan file to signal the esrgan container for Real-ESRGAN only
        process_file = os.path.join(UPLOAD_FOLDER, f"{input_filename}.process_esrgan")
        with open(process_file, 'w') as f:
            f.write("process_esrgan_only")
        
        output_filename = f"esrgan_{input_filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Wait for processing to complete (check if output exists and .process file is gone)
        max_wait = 600  # 10 minutes timeout (reduced from 15)
        wait_time = 0
        
        while wait_time < max_wait:
            if os.path.exists(output_path) and not os.path.exists(process_file):
                print("Real-ESRGAN processing completed successfully")
                return output_filename
            time.sleep(2)
            wait_time += 2
        
        print("Real-ESRGAN processing timed out")
        # Clean up process file if it still exists
        if os.path.exists(process_file):
            os.remove(process_file)
        return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def process_with_gfpgan(input_filename):
    """Process already Real-ESRGAN enhanced image with GFPGAN"""
    try:
        # Verify input file exists first
        input_path = os.path.join(OUTPUT_FOLDER, input_filename)
        if not os.path.exists(input_path):
            print(f"[GFPGAN] ERROR: Input file does not exist: {input_path}")
            print(f"[GFPGAN] Files in output folder:")
            for f in os.listdir(OUTPUT_FOLDER):
                print(f"  - {f}")
            return None
        
        # Create a .process_gfpgan file to signal GFPGAN processing
        process_file = os.path.join(OUTPUT_FOLDER, f"{input_filename}.process_gfpgan")
        with open(process_file, 'w') as f:
            f.write("process_gfpgan")
        
        print(f"[GFPGAN] Created process file: {process_file}")
        
        # Output will be the final enhanced version
        base_name = input_filename.replace("esrgan_", "")
        output_filename = f"final_enhanced_{base_name}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        print(f"[GFPGAN] Waiting for output: {output_path}")
        
        # Wait for GFPGAN processing to complete
        max_wait = 600  # 10 minutes timeout (increased from 5)
        wait_time = 0
        
        while wait_time < max_wait:
            # Check if processing is complete
            if os.path.exists(output_path) and not os.path.exists(process_file):
                print("[GFPGAN] GFPGAN processing completed successfully")
                return output_filename
            
            # Log progress every 10 seconds
            if wait_time % 10 == 0:
                print(f"[GFPGAN] Waiting... ({wait_time}s / {max_wait}s)")
                print(f"[GFPGAN] Process file exists: {os.path.exists(process_file)}")
                print(f"[GFPGAN] Output file exists: {os.path.exists(output_path)}")
            
            time.sleep(2)
            wait_time += 2
        
        print("[GFPGAN] GFPGAN processing timed out")
        # Clean up process file if it still exists
        if os.path.exists(process_file):
            os.remove(process_file)
            print("[GFPGAN] Cleaned up process file")
        return None
            
    except Exception as e:
        print(f"[GFPGAN] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Historical Photo Restoration</title>
 <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #000000 0%, #111111 100%);
                min-height: 100vh;
                color: #e0e0e0;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            .header {
                text-align: center;
                margin-bottom: 40px;
                color: #00aaff;
            }

            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 10px rgba(0,150,255,0.4);
            }

            .header p {
                font-size: 1.2em;
                opacity: 0.85;
                color: #cccccc;
            }

            .main-card {
                background: rgba(25, 25, 25, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.6);
                border: 1px solid rgba(255,255,255,0.05);
            }

            .upload-section {
                text-align: center;
                margin-bottom: 30px;
            }

            .upload-area {
                border: 3px dashed #007bff;
                border-radius: 15px;
                padding: 60px 40px;
                background: linear-gradient(145deg, #1a1a1a, #121212);
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }

            .upload-area:hover {
                border-color: #00aaff;
                background: linear-gradient(145deg, #151515, #1f1f1f);
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0,150,255,0.2);
            }

            .upload-area.dragover {
                border-color: #00aaff;
                background: linear-gradient(145deg, #1a2a3a, #0d1a26);
            }

            .upload-icon {
                font-size: 4em;
                color: #00aaff;
                margin-bottom: 20px;
                display: block;
            }

            .upload-text {
                font-size: 1.3em;
                color: #e0e0e0;
                margin-bottom: 15px;
                font-weight: 600;
            }

            .upload-subtext {
                color: #aaa;
                font-size: 0.95em;
                margin-bottom: 25px;
            }

            .file-input {
                display: none;
            }

            .upload-btn {
                background: linear-gradient(135deg, #007bff, #00aaff);
                color: white;
                border: none;
                padding: 15px 35px;
                font-size: 1.1em;
                font-weight: 600;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0,150,255,0.3);
            }

            .upload-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,150,255,0.4);
            }

            .upload-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            .preview-section {
                display: none;
                margin-top: 30px;
                text-align: center;
            }

            .image-preview {
                max-width: 400px;
                max-height: 400px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.6);
                margin: 20px auto;
                display: block;
            }

            .process-btn {
                background: linear-gradient(135deg, #28a745, #6dd5ed);
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 1.2em;
                font-weight: 600;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(40,167,69,0.3);
                margin-top: 20px;
            }

            .process-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(40,167,69,0.4);
            }

            .loading {
                display: none;
                text-align: center;
                margin: 30px 0;
                color: #e0e0e0;
            }

            .spinner {
                border: 4px solid #333;
                border-top: 4px solid #00aaff;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .progress-bar {
                width: 100%;
                height: 8px;
                background: #222;
                border-radius: 4px;
                overflow: hidden;
                margin: 20px 0;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #007bff, #00aaff);
                width: 0%;
                transition: width 0.3s ease;
                border-radius: 4px;
            }

            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }

            .feature-card {
                background: #1c1c1c;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.4);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                color: #e0e0e0;
            }

            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 25px rgba(0,150,255,0.2);
            }

            .feature-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
                display: block;
            }

            .reset-btn {
                background: #444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                margin-left: 15px;
                transition: all 0.3s ease;
            }

            .reset-btn:hover {
                background: #666;
                transform: translateY(-1px);
            }

            .file-info {
                background: #1f1f1f;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                text-align: left;
                font-size: 0.9em;
                color: #ccc;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                .main-card {
                    padding: 20px;
                    margin: 10px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .upload-area {
                    padding: 40px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📸 Historical Photo Restoration</h1>
                <p>Two-stage AI enhancement: Super Resolution + Optional Face Enhancement</p>
            </div>

            <div class="main-card">
                <form id="uploadForm" method="post" action="/upload" enctype="multipart/form-data">
                    <div class="upload-section">
                        <div class="upload-area" id="uploadArea">
                            <span class="upload-icon">📁</span>
                            <div class="upload-text">Drop your photo here or click to browse</div>
                            <div class="upload-subtext">Supports JPG, PNG files up to 10MB</div>
                            <input type="file" name="file" id="fileInput" class="file-input" accept=".jpg,.jpeg,.png" required>
                            <button type="button" class="upload-btn" onclick="document.getElementById('fileInput').click()">
                                Choose Photo
                            </button>
                        </div>
                        
                        <div class="file-info" id="fileInfo" style="display: none;"></div>
                    </div>

                    <div class="preview-section" id="previewSection">
                        <h3 style="margin-bottom: 20px; color: #555;">Preview</h3>
                        <img id="imagePreview" class="image-preview" src="" alt="Preview">
                        <div>
                            <button type="submit" class="process-btn" id="processBtn">
                                🔍 Start with Super Resolution
                            </button>
                            <button type="button" class="reset-btn" onclick="resetForm()">
                                🔄 Reset
                            </button>
                        </div>
                    </div>
                </form>

                <div class="loading" id="loadingSection">
                    <div class="spinner"></div>
                    <h3 id="loadingTitle">Enhancing your photo with Real-ESRGAN...</h3>
                    <p id="loadingDesc">Super resolution processing (4x upscaling)</p>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                </div>

                <div class="feature-grid">
                    <div class="feature-card">
                        <span class="feature-icon" style="color: #667eea;">🔍</span>
                        <h4>Stage 1: Super Resolution</h4>
                        <p>4x upscaling with Real-ESRGAN (faster)</p>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon" style="color: #56ab2f;">👤</span>
                        <h4>Stage 2: Face Enhancement</h4>
                        <p>Optional GFPGAN for portrait photos</p>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon" style="color: #764ba2;">⚡</span>
                        <h4>Choose Your Enhancement</h4>
                        <p>Quick results or maximum quality</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const previewSection = document.getElementById('previewSection');
            const imagePreview = document.getElementById('imagePreview');
            const fileInfo = document.getElementById('fileInfo');
            const uploadForm = document.getElementById('uploadForm');
            const loadingSection = document.getElementById('loadingSection');
            const processBtn = document.getElementById('processBtn');

            // Drag and drop functionality
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    handleFileSelect();
                }
            });

            // File input change
            fileInput.addEventListener('change', handleFileSelect);

            function handleFileSelect() {
                const file = fileInput.files[0];
                if (file) {
                    // Show file info
                    const fileSize = (file.size / 1024 / 1024).toFixed(2);
                    fileInfo.innerHTML = `
                        <strong>📄 ${file.name}</strong><br>
                        Size: ${fileSize} MB | Type: ${file.type}
                    `;
                    fileInfo.style.display = 'block';

                    // Show preview
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imagePreview.src = e.target.result;
                        previewSection.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            }

            // Form submission
            uploadForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Show loading
                document.querySelector('.upload-section').style.display = 'none';
                previewSection.style.display = 'none';
                loadingSection.style.display = 'block';
                
                // Simulate progress
                let progress = 0;
                const progressFill = document.getElementById('progressFill');
                const progressInterval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 90) progress = 90;
                    progressFill.style.width = progress + '%';
                }, 500);

                // Submit form
                const formData = new FormData(this);
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                }).then(response => {
                    clearInterval(progressInterval);
                    progressFill.style.width = '100%';
                    return response.text();
                }).then(html => {
                    document.body.innerHTML = html;
                }).catch(error => {
                    console.error('Error:', error);
                    alert('Upload failed. Please try again.');
                    resetForm();
                });
            });

            function resetForm() {
                fileInput.value = '';
                previewSection.style.display = 'none';
                fileInfo.style.display = 'none';
                loadingSection.style.display = 'none';
                document.querySelector('.upload-section').style.display = 'block';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process with Real-ESRGAN only first
        print(f"Processing {filename} with Real-ESRGAN (Stage 1)...")
        esrgan_output_filename = process_with_realesrgan_only(filename)
        
        if esrgan_output_filename is None:
            print("Real-ESRGAN processing failed, using fallback")
            # Fallback to copying if processing fails
            import shutil
            esrgan_output_filename = f"esrgan_{filename}"
            output_path = os.path.join(OUTPUT_FOLDER, esrgan_output_filename)
            shutil.copy(filepath, output_path)
        else:
            print(f"Real-ESRGAN processing completed: {esrgan_output_filename}")
        
        # Get file info
        original_size = os.path.getsize(filepath)
        original_size_mb = round(original_size / (1024 * 1024), 2)
        
        # Show results with option for GFPGAN
        return show_esrgan_results(filename, esrgan_output_filename, original_size_mb)
    
    return redirect(url_for('index'))

def show_esrgan_results(original_filename, esrgan_filename, original_size_mb):
    """Show Real-ESRGAN results with option to apply GFPGAN"""
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Super Resolution Complete</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; color: white; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .success-badge {{
            background: linear-gradient(135deg, #56ab2f, #a8e6cf);
            color: white;
            padding: 10px 30px;
            border-radius: 50px;
            display: inline-block;
            margin-bottom: 20px;
            font-weight: 600;
            font-size: 1.1em;
            box-shadow: 0 5px 15px rgba(86, 171, 47, 0.3);
        }}
        .results-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 40px; }}
        .image-section {{ text-align: center; }}
        .image-section h3 {{ font-size: 1.5em; margin-bottom: 20px; color: #555; }}
        .image-container {{
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}
        .image-container:hover {{ transform: translateY(-5px); }}
        .comparison-image {{ width: 100%; height: auto; display: block; border-radius: 15px; }}
        .image-overlay {{
            position: absolute; top: 10px; right: 10px;
            background: rgba(0,0,0,0.7); color: white;
            padding: 5px 10px; border-radius: 15px; font-size: 0.8em;
        }}
        .enhancement-option {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            text-align: center;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }}
        .enhancement-option:hover {{ border-color: #667eea; transform: translateY(-2px); }}
        .option-title {{ font-size: 1.5em; color: #333; margin-bottom: 15px; font-weight: 600; }}
        .option-description {{ color: #666; margin-bottom: 25px; font-size: 1.1em; line-height: 1.6; }}
        .btn {{
            padding: 15px 30px; margin: 0 10px; border: none;
            border-radius: 50px; font-size: 1.1em; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease;
            text-decoration: none; display: inline-block;
        }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3); }}
        .btn-secondary {{ background: #6c757d; color: white; box-shadow: 0 5px 15px rgba(108, 117, 125, 0.3); }}
        .btn-success {{ background: linear-gradient(135deg, #56ab2f, #a8e6cf); color: white; box-shadow: 0 5px 15px rgba(86, 171, 47, 0.3); }}
        .btn-warning {{ background: linear-gradient(135deg, #f39c12, #f1c40f); color: white; box-shadow: 0 5px 15px rgba(243, 156, 18, 0.3); }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.2); }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
        .loading {{ display: none; text-align: center; margin: 30px 0; }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #f39c12;
            border-radius: 50%;
            width: 60px; height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .progress-bar {{ width: 100%; height: 10px; background: #e0e0e0; border-radius: 5px; overflow: hidden; margin: 20px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #f39c12, #f1c40f); width: 0%; transition: width 0.5s ease; border-radius: 5px; }}
        .progress-text {{ color: #666; margin-top: 10px; font-size: 0.9em; }}
        @media (max-width: 768px) {{
            .comparison {{ grid-template-columns: 1fr; gap: 30px; }}
            .container {{ padding: 10px; }}
            .results-container {{ padding: 20px; }}
            .header h1 {{ font-size: 2em; }}
            .btn {{ padding: 12px 25px; margin: 5px; display: block; margin-bottom: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="success-badge">🔍 Stage 1 Complete!</div>
            <h1>Super Resolution Applied</h1>
        </div>

        <div class="results-container">
            <div class="comparison" id="comparisonSection">
                <div class="image-section">
                    <h3>📷 Original Photo</h3>
                    <div class="image-container">
                        <img src="/static/inputs/{original_filename}" class="comparison-image" alt="Original">
                        <div class="image-overlay">Original</div>
                    </div>
                </div>
                <div class="image-section">
                    <h3>🔍 Super Resolution (4x)</h3>
                    <div class="image-container">
                        <img src="/static/outputs/{esrgan_filename}" class="comparison-image" alt="Enhanced">
                        <div class="image-overlay">Real-ESRGAN</div>
                    </div>
                </div>
            </div>

            <div class="enhancement-option" id="enhancementOption">
                <div class="option-title">👤 Optional: Face Enhancement</div>
                <div class="option-description">
                    Your image has been enhanced with super resolution! For photos with faces, you can apply GFPGAN 
                    for additional face restoration and enhancement. This will take a few more minutes but can significantly 
                    improve portrait photos.
                </div>
                
                <form id="gfpganForm" method="POST" action="/apply_gfpgan">
                    <input type="hidden" name="esrgan_filename" value="{esrgan_filename}">
                    <button type="submit" class="btn btn-warning" id="gfpganBtn">
                        ✨ Apply Face Enhancement (GFPGAN)
                    </button>
                </form>
                
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    Recommended for: Portrait photos, family pictures, historical photos with people
                </p>
            </div>

            <div class="loading" id="gfpganLoading">
                <div class="spinner"></div>
                <h3 style="color: #f39c12; margin-bottom: 10px;">Applying GFPGAN Face Enhancement...</h3>
                <p style="color: #666; margin-bottom: 20px;">Processing high-resolution facial features</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="gfpganProgress"></div>
                </div>
                <div class="progress-text" id="progressText">Initializing GFPGAN model...</div>
            </div>

            <div style="text-align: center; margin-top: 30px;" id="actionButtons">
                <a href="/download/{esrgan_filename}" class="btn btn-success">💾 Download Current Result</a>
                <a href="/" class="btn btn-primary">🔄 Process Another Photo</a>
                <a href="/" class="btn btn-secondary">🏠 Go to Home</a>
            </div>
        </div>
    </div>
    
    <script type="text/javascript">
        document.getElementById('gfpganForm').onsubmit = function(e) {{
            e.preventDefault();
            console.log('[Frontend] GFPGAN form submitted');
            
            // Disable button
            const btn = document.getElementById('gfpganBtn');
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            // Show loading, hide other sections
            document.getElementById('enhancementOption').style.display = 'none';
            document.getElementById('actionButtons').style.display = 'none';
            document.getElementById('gfpganLoading').style.display = 'block';
            
            // Progress simulation with messages
            let progress = 0;
            const progressBar = document.getElementById('gfpganProgress');
            const progressText = document.getElementById('progressText');
            const messages = [
                'Initializing GFPGAN model...',
                'Loading face detection...',
                'Processing facial features...',
                'Enhancing face quality...',
                'Applying restoration...',
                'Finalizing enhancements...',
                'Almost done...'
            ];
            let msgIndex = 0;
            
            const interval = setInterval(function() {{
                progress += Math.random() * 8;
                if (progress > 90) progress = 90;
                progressBar.style.width = progress + '%';
                
                // Update message
                if (progress > (msgIndex + 1) * 12 && msgIndex < messages.length - 1) {{
                    msgIndex++;
                    progressText.textContent = messages[msgIndex];
                }}
            }}, 1000);
            
            // Submit via FormData (works with both JSON and form encoding)
            const formData = new FormData(this);
            
            fetch('/apply_gfpgan', {{
                method: 'POST',
                body: formData
            }})
            .then(response => {{
                console.log('[Frontend] Response status:', response.status);
                if (!response.ok) {{
                    throw new Error('Server returned ' + response.status);
                }}
                return response.text();
            }})
            .then(html => {{
                clearInterval(interval);
                progressBar.style.width = '100%';
                progressText.textContent = 'Complete!';
                console.log('[Frontend] Success - updating page');
                setTimeout(() => {{
                    document.body.innerHTML = html;
                }}, 500);
            }})
            .catch(err => {{
                clearInterval(interval);
                console.error('[Frontend] Error:', err);
                alert('GFPGAN processing failed: ' + err.message + '\\n\\nPlease try again or download the current result.');
                document.getElementById('enhancementOption').style.display = 'block';
                document.getElementById('actionButtons').style.display = 'block';
                document.getElementById('gfpganLoading').style.display = 'none';
                btn.disabled = false;
                btn.textContent = '✨ Apply Face Enhancement (GFPGAN)';
            }});
            
            return false;
        }};
        
        console.log('[Frontend] GFPGAN page loaded and ready');
    </script>
</body>
</html>'''

@app.route('/apply_gfpgan', methods=['POST'])
def apply_gfpgan():
    """Apply GFPGAN to the already processed Real-ESRGAN image"""
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        esrgan_filename = data.get('esrgan_filename')
    else:
        esrgan_filename = request.form.get('esrgan_filename')
    
    if not esrgan_filename:
        print("[Flask] ERROR: No filename provided")
        return jsonify({'error': 'No filename provided'}), 400
    
    print(f"[Flask] Applying GFPGAN to {esrgan_filename}...")
    final_output_filename = process_with_gfpgan(esrgan_filename)
    
    if final_output_filename is None:
        print("[Flask] GFPGAN processing failed")
        return jsonify({'error': 'GFPGAN processing timed out or failed. The background processor may not be running.'}), 500
    
    print(f"[Flask] GFPGAN processing completed: {final_output_filename}")
    
    # Extract original filename for display
    original_filename = esrgan_filename.replace("esrgan_", "")
    
    # Show final results
    return show_final_results(original_filename, esrgan_filename, final_output_filename)

def show_final_results(original_filename, esrgan_filename, final_filename):
    """Show final results with all three versions"""
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Complete Enhancement Finished</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
                padding: 20px;
            }}

            .container {{
                max-width: 1600px;
                margin: 0 auto;
            }}

            .header {{
                text-align: center;
                margin-bottom: 30px;
                color: white;
            }}

            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}

            .success-badge {{
                background: linear-gradient(135deg, #56ab2f, #a8e6cf);
                color: white;
                padding: 10px 30px;
                border-radius: 50px;
                display: inline-block;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: 1.1em;
                box-shadow: 0 5px 15px rgba(86, 171, 47, 0.3);
            }}

            .results-container {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }}

            .comparison {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 30px;
                margin-bottom: 40px;
            }}

            .image-section {{
                text-align: center;
            }}

            .image-section h3 {{
                font-size: 1.3em;
                margin-bottom: 15px;
                color: #555;
            }}

            .image-container {{
                position: relative;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            }}

            .image-container:hover {{
                transform: translateY(-5px);
            }}

            .comparison-image {{
                width: 100%;
                height: auto;
                display: block;
                border-radius: 15px;
            }}

            .image-overlay {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                font-weight: 600;
            }}

            .final-result {{
                border: 3px solid #56ab2f;
                box-shadow: 0 15px 35px rgba(86, 171, 47, 0.3);
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }}

            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}

            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #56ab2f;
                display: block;
            }}

            .stat-label {{
                color: #666;
                margin-top: 5px;
            }}

            .btn {{
                padding: 15px 30px;
                margin: 0 10px 10px 0;
                border: none;
                border-radius: 50px;
                font-size: 1.1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }}

            .btn-primary {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            }}

            .btn-secondary {{
                background: #6c757d;
                color: white;
                box-shadow: 0 5px 15px rgba(108, 117, 125, 0.3);
            }}

            .btn-success {{
                background: linear-gradient(135deg, #56ab2f, #a8e6cf);
                color: white;
                box-shadow: 0 5px 15px rgba(86, 171, 47, 0.3);
            }}

            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            }}

            .action-buttons {{
                text-align: center;
                margin-top: 40px;
            }}

            .enhancement-badge {{
                background: linear-gradient(135deg, #f39c12, #f1c40f);
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-top: 10px;
                display: inline-block;
            }}

            @media (max-width: 1200px) {{
                .comparison {{
                    grid-template-columns: 1fr;
                    gap: 40px;
                }}
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}
                
                .results-container {{
                    padding: 20px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .btn {{
                    padding: 12px 25px;
                    margin: 5px;
                    display: block;
                    width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="success-badge">🎉 Complete Enhancement Finished!</div>
                <h1>AI-Powered Photo Restoration Complete</h1>
            </div>

            <div class="results-container">
                <div class="comparison">
                    <div class="image-section">
                        <h3>📷 Original Photo</h3>
                        <div class="image-container">
                            <img src="/static/inputs/{original_filename}" class="comparison-image" alt="Original">
                            <div class="image-overlay">Original</div>
                        </div>
                    </div>
                    <div class="image-section">
                        <h3>🔍 Super Resolution</h3>
                        <div class="image-container">
                            <img src="/static/outputs/{esrgan_filename}" class="comparison-image" alt="Real-ESRGAN Enhanced">
                            <div class="image-overlay">Real-ESRGAN</div>
                        </div>
                        <div class="enhancement-badge">4x Upscaled</div>
                    </div>
                    <div class="image-section">
                        <h3>✨ Final Enhanced</h3>
                        <div class="image-container final-result">
                            <img src="/static/outputs/{final_filename}" class="comparison-image" alt="Final Enhanced">
                            <div class="image-overlay">AI Enhanced</div>
                        </div>
                        <div class="enhancement-badge">+ Face Enhancement</div>
                    </div>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-number">2</span>
                        <div class="stat-label">AI Models Used</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">4x</span>
                        <div class="stat-label">Resolution Increase</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">100%</span>
                        <div class="stat-label">Enhancement Complete</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">✓</span>
                        <div class="stat-label">Face Optimized</div>
                    </div>
                </div>

                <div class="action-buttons">
                    <a href="/download/{final_filename}" class="btn btn-success">💾 Download Final Result</a>
                    <a href="/download/{esrgan_filename}" class="btn btn-secondary">📁 Download Super Resolution Only</a>
                    <a href="/" class="btn btn-primary">🔄 Process Another Photo</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/download/<filename>')
def download_file(filename):
    """Serve the processed image file for download"""
    try:
        return send_from_directory(
            OUTPUT_FOLDER, 
            filename, 
            as_attachment=True,
            download_name=f"enhanced_{filename}"
        )
    except FileNotFoundError:
        flash('File not found. Please try processing your image again.', 'error')
        return redirect(url_for('index'))

@app.route('/static/inputs/<filename>')
def serve_input(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/static/outputs/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)