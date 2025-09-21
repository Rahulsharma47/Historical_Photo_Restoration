# Historical Photo Restoration

A web-based AI-powered photo restoration system that brings old, damaged, or low-quality images back to life using state-of-the-art deep learning models.

## Features

### Two-Stage Enhancement Process
- **Stage 1: Super Resolution** - 4x image upscaling using Real-ESRGAN
- **Stage 2: Face Enhancement** - Optional face restoration using GFPGAN
- **User Choice** - Decide whether to apply face enhancement based on your specific image

### Key Capabilities
- **Super Resolution**: Enhance image quality and increase resolution by 4x
- **Face Restoration**: Specialized enhancement for portraits and photos with people
- **Intelligent Processing**: Automatic fallback mechanisms if AI processing fails
- **Modern Web Interface**: Drag-and-drop file upload with real-time progress tracking
- **Flexible Workflow**: Stop after super resolution or continue with face enhancement

### Supported Formats
- Input: JPEG, JPG, PNG files up to 10MB
- Output: High-resolution enhanced images ready for download

## Technology Stack

### AI Models
- **Real-ESRGAN**: For super resolution and general image enhancement
- **GFPGAN**: For face-specific restoration and enhancement

### Backend
- **Flask**: Web framework for handling uploads and processing
- **Docker**: Containerized deployment for consistent environments
- **Python**: Core processing with PyTorch for AI model inference

### Frontend
- **Responsive HTML5/CSS3**: Modern, mobile-friendly interface
- **Progressive Enhancement**: Visual feedback and interactive elements
- **Real-time Progress**: Live updates during processing

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Processing     │    │   File Storage  │
│   Container     │──→ │   Container      │──→ │   Volumes       │
│   (Flask App)   │    │   (AI Models)    │    │   (I/O Files)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- NVIDIA GPU (recommended) or CPU processing
- At least 8GB RAM for optimal performance

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/historical-photo-restoration.git
cd historical-photo-restoration
```

2. **Download AI models**
```bash
# Create models directory
mkdir models

# Download Real-ESRGAN model
wget -O models/RealESRGAN_x4plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth

# Download GFPGAN model
wget -O models/GFPGANv1.4.pth https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

4. **Access the application**
Open your browser and navigate to `http://localhost:5001`

## Usage

### Basic Workflow

1. **Upload Image**: Drag and drop or select an image file
2. **Stage 1 Processing**: Automatic super resolution enhancement (5-10 minutes)
3. **Review Results**: Compare original vs enhanced image
4. **Optional Stage 2**: Choose to apply face enhancement for portraits (3-5 minutes)
5. **Download**: Save your enhanced image(s)

### Processing Times
- **Super Resolution**: 5-10 minutes depending on image size
- **Face Enhancement**: Additional 3-5 minutes
- **Total Time**: 8-15 minutes for complete enhancement

### Best Practices
- Use face enhancement for portraits, family photos, or historical photos with people
- Super resolution alone works well for landscapes, documents, and general photos
- Ensure good internet connection for upload/download of high-resolution results

## Configuration

### Environment Variables
- `UPLOAD_FOLDER`: Directory for input images (default: `/app/inputs`)
- `OUTPUT_FOLDER`: Directory for processed images (default: `/app/outputs/frontend`)
- `MAX_CONTENT_LENGTH`: Maximum file size for uploads

### Docker Volumes
```yaml
volumes:
  - ./inputs:/app/inputs      # Input images
  - ./outputs:/app/outputs    # Processed images  
  - ./models:/app/models      # AI model files
```

## File Structure

```
historical-photo-restoration/
├── frontend/
│   ├── frontend_app.py              # Main Flask application
│   ├── process_realesrgan_only.py   # Real-ESRGAN processing
│   ├── process_gfpgan_only.py       # GFPGAN processing
│   └── docker_processing_script.py  # Processing orchestrator
├── Docker/
│   ├── Dockerfile.frontend          # Frontend container
│   └── Dockerfile.processing        # Processing container
├── docker-compose.yml               # Multi-container setup
├── models/                          # AI model files
├── inputs/                          # Upload directory
└── outputs/                         # Results directory
```

## Performance Optimization

### Hardware Recommendations
- **GPU**: NVIDIA GPU with 6GB+ VRAM for fastest processing
- **CPU**: Multi-core processor for CPU-only processing (slower)
- **RAM**: 8GB+ recommended for large images
- **Storage**: SSD for faster file I/O

### Processing Optimizations
- **Tile Processing**: Large images are processed in tiles to manage memory
- **Automatic Scaling**: Output scaling optimized for quality vs speed
- **Fallback Processing**: CPU fallback when GPU unavailable

## Troubleshooting

### Common Issues

**Processing takes too long**
- Check GPU availability and VRAM
- Reduce image size before upload
- Ensure sufficient system RAM

**Container fails to start**
- Verify Docker installation and permissions
- Check model files are downloaded correctly
- Ensure ports 5001 is available

**Poor enhancement quality**
- Original image quality affects results
- Some images may not benefit from AI enhancement
- Try different combinations of processing stages

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 frontend/ --max-line-length=100
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - Super resolution model
- [GFPGAN](https://github.com/TencentARC/GFPGAN) - Face restoration model
- [BasicSR](https://github.com/XPixelGroup/BasicSR) - Image processing framework

## Citation

If you use this project in your research, please cite:

```bibtex
@software{historical_photo_restoration,
  title={Historical Photo Restoration: AI-Powered Image Enhancement},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/historical-photo-restoration}
}
```

---

**Note**: This project is for educational and personal use. Processing times may vary based on hardware capabilities and image complexity.
