import sys
import torch
import numpy as np
import cv2
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

def process_image_realesrgan_only(input_filename, output_filename):
    """Process image using only Real-ESRGAN for super resolution"""
    # Device selection
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    print(f"Using device: {device}")

    # Real-ESRGAN for super resolution
    print("Applying Real-ESRGAN for super resolution...")
    model_path = '/app/models/RealESRGAN_x4plus.pth'
    
    try:
        state_dict = torch.load(model_path, map_location=device)['params_ema']

        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4
        ).to(device)
        model.load_state_dict(state_dict, strict=True)

        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=200,
            pre_pad=0,
            half=False,
            device=device
        )

        # Load and process with Real-ESRGAN
        img = Image.open(f'/app/inputs/{input_filename}').convert('RGB')
        img = np.array(img)
        
        print(f"Input image shape: {img.shape}")
        
        # Run Real-ESRGAN inference
        esrgan_output, _ = upsampler.enhance(img, outscale=4)
        print(f"Enhanced image shape: {esrgan_output.shape}")
        print("Real-ESRGAN processing complete")

        # Convert RGB to BGR for OpenCV saving
        esrgan_output_bgr = cv2.cvtColor(esrgan_output, cv2.COLOR_RGB2BGR)
        
        # Save result
        cv2.imwrite(f'/app/outputs/{output_filename}', esrgan_output_bgr)
        print(f"Real-ESRGAN processing complete - saved as {output_filename}")
        
    except Exception as e:
        print(f"Error during Real-ESRGAN processing: {e}")
        # Fallback: just copy and resize the original image
        img = Image.open(f'/app/inputs/{input_filename}').convert('RGB')
        width, height = img.size
        img_resized = img.resize((width * 4, height * 4), Image.LANCZOS)
        img_resized.save(f'/app/outputs/{output_filename}')
        print(f"Fallback processing complete - saved as {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_realesrgan_only.py <input_filename> <output_filename>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_image_realesrgan_only(input_file, output_file)