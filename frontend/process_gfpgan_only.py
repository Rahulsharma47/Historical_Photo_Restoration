import sys
import torch
import numpy as np
import cv2
from PIL import Image
from gfpgan import GFPGANer

def process_image_gfpgan_only(input_filename, output_filename):
    """Process already enhanced image using only GFPGAN for face enhancement"""
    # Device selection
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    print(f"Using device: {device}")

    # GFPGAN for face enhancement
    print("Applying GFPGAN for face enhancement...")
    
    try:
        # Initialize GFPGAN
        face_restorer = GFPGANer(
            model_path='/app/models/GFPGANv1.4.pth',
            upscale=1,  # Don't upscale since image is already enhanced by Real-ESRGAN
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=None  # We already enhanced with Real-ESRGAN
        )

        # Load the Real-ESRGAN enhanced image
        img = cv2.imread(f'/app/outputs/{input_filename}')
        if img is None:
            raise Exception(f"Could not load image: {input_filename}")
        
        print(f"Input image shape: {img.shape}")
        
        # Enhance faces with GFPGAN
        cropped_faces, restored_faces, final_output = face_restorer.enhance(
            img,
            has_aligned=False,
            only_center_face=False,
            paste_back=True
        )
        
        print("GFPGAN processing complete")
        print(f"Final output shape: {final_output.shape}")

        # Save final result
        cv2.imwrite(f'/app/outputs/{output_filename}', final_output)
        print(f"GFPGAN processing complete - saved as {output_filename}")
        
    except Exception as e:
        print(f"Error during GFPGAN processing: {e}")
        # Fallback: just copy the input file if GFPGAN fails
        import shutil
        shutil.copy(f'/app/outputs/{input_filename}', f'/app/outputs/{output_filename}')
        print(f"Fallback: copied {input_filename} as {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_gfpgan_only.py <input_filename> <output_filename>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_image_gfpgan_only(input_file, output_file)