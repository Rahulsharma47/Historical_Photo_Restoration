# LaMa Inpainting for Scratch Removal {Approach 1} {not working}

import cv2
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import os

import sys
sys.path.append('/app/model_repo/lama')

# Import LaMa (assuming you cloned lama repo and installed)
from saicinpainting.evaluation.data import pad_tensor_to_modulo
from saicinpainting.training.trainers import load_checkpoint

# Paths
image_path = '/app/inputs/old_w_scratch/a.png'
mask_path = '/app/outputs/mask/mask.png'
checkpoint_path = '/app/models/big-lama.pt'
output_path = '/app/outputs/lama_out.png'

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
train_config = {'strict': False}
model = load_checkpoint(checkpoint_path, strict=False, map_location=device)
model.eval().to(device)

# Load image + mask
image = Image.open(image_path).convert('RGB')
mask = Image.open(mask_path).convert('L')  # grayscale

transform = transforms.ToTensor()
img_tensor = transform(image).unsqueeze(0).to(device)
mask_tensor = transform(mask).unsqueeze(0).to(device)

# Pad for compatibility
img_tensor = pad_tensor_to_modulo(img_tensor, 8)
mask_tensor = pad_tensor_to_modulo(mask_tensor, 8)

# Inpaint
with torch.no_grad():
    inpainted = model({'image': img_tensor, 'mask': mask_tensor})['inpainted']

result = (inpainted[0].permute(1,2,0).cpu().numpy() * 255).astype(np.uint8)
Image.fromarray(result).save(output_path)

print(f"Saved scratch-removed image to {output_path}") 



# Simple OpenCV Inpainting for comparison {Approach 2} {too blurry after inpainting}
'''
import cv2

# Paths
image_path = "/Users/rahulsharma/ML_project/historical_photo_restoration/inputs/old_w_scratch/b.png"
mask_path = "/Users/rahulsharma/ML_project/historical_photo_restoration/outputs/mask/mask2.png"
output_path = "/Users/rahulsharma/ML_project/historical_photo_restoration/outputs/lama-fixes/restored.png"

# Load image and mask
img = cv2.imread(image_path, cv2.IMREAD_COLOR)
mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

# Inpainting (try both methods)
restored_telea = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
restored_ns = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_NS)

# Save outputs
cv2.imwrite(output_path.replace("restored.png", "restored_telea.png"), restored_telea)
cv2.imwrite(output_path.replace("restored.png", "restored_ns.png"), restored_ns)

print("Restored images saved as restored_telea.png and restored_ns.png")

'''
#  Stable Diffusion Inpainting for comparison {Approach 3} {currently used}

'''
from diffusers import StableDiffusionInpaintPipeline
import torch
from PIL import Image

# Select device (MPS for Apple Silicon, fallback to CPU)
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"[INFO] Using device: {DEVICE}")

# Load the pipeline
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",
    torch_dtype=torch.float16
).to(DEVICE)

# Load input image & mask
image = Image.open("/Users/rahulsharma/ML_project/historical_photo_restoration/inputs/old_w_scratch/a.png").convert("RGB")
mask_image = Image.open("/Users/rahulsharma/ML_project/historical_photo_restoration/outputs/mask/mask.png").convert("RGB")

# Inpaint
result = pipe(
    prompt="restore old photo, remove scratches, realistic restoration",
    image=image,
    mask_image=mask_image,
    guidance_scale=7.5,      # prompt adherence
    strength=0.75,           # how much to replace
    num_inference_steps=30   # diffusion steps (quality vs speed)
).images[0]

# Save
result.save("/Users/rahulsharma/ML_project/historical_photo_restoration/outputs/lama-fixes/restored.png")
print("[INFO] Restored image saved!")

'''