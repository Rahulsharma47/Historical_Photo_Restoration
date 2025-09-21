from gfpgan import GFPGANer
import cv2

# Initialize GFPGAN
restorer = GFPGANer(
    model_path='/app/models/GFPGANv1.4.pth',
    upscale=1,        # keep scale 1 since you already upscaled earlier
    arch='clean',     
    channel_multiplier=2,
    bg_upsampler=None # set RealESRGAN if you want background too
)

# Load image
input_img = cv2.imread('/app/outputs/test1_out.png', cv2.IMREAD_COLOR)

# Enhance faces
cropped_faces, restored_faces, restored_img = restorer.enhance(
    input_img,
    has_aligned=False,
    only_center_face=False,
    paste_back=True
)

cv2.imwrite('/app/outputs/GFPGAN/enhanced_faces_2.png', restored_img)
