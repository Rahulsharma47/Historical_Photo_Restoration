import sys
import os
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

        # Load the Real-ESRGAN enhanced image - FIXED PATH
        input_path = f'/app/outputs/frontend/{input_filename}'
        print(f"Loading image from: {input_path}")
        
        img = cv2.imread(input_path)
        if img is None:
            raise Exception(f"Could not load image from: {input_path}")
        
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

        # Save final result - FIXED PATH
        output_path = f'/app/outputs/frontend/{output_filename}'
        cv2.imwrite(output_path, final_output)
        print(f"GFPGAN processing complete - saved as {output_path}")
        
    except Exception as e:
        print(f"Error during GFPGAN processing: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback: just copy the input file if GFPGAN fails
        import shutil
        input_path = f'/app/outputs/frontend/{input_filename}'
        output_path = f'/app/outputs/frontend/{output_filename}'
        
        if os.path.exists(input_path):
            shutil.copy(input_path, output_path)
            print(f"Fallback: copied {input_filename} as {output_filename}")
        else:
            print(f"Error: Input file not found at {input_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_gfpgan_only.py <input_filename> <output_filename>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    import os
    print(f"Current working directory: {os.getcwd()}")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    process_image_gfpgan_only(input_file, output_file)