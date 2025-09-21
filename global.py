import torch
import numpy as np
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

# pick device: MPS (Apple Silicon GPU), CUDA, or CPU
if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

print("Using device:", device)

model_path = '/app/models/RealESRGAN_x4plus.pth'
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
    tile=200,       # change this if RAM issues
    pre_pad=0,
    half=False,
    device=device
)

# load input
img = Image.open('/app/inputs/h.png').convert('RGB')
img = np.array(img)

# run inference
output, _ = upsampler.enhance(img, outscale=4) 
output = Image.fromarray(output)
output.save('/app/outputs/test_h_out.png')
