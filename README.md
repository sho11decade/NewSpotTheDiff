# NewSpotTheDiff - Next-Generation Spot the Difference Auto-Generator

**NewSpotTheDiff** is an AI-powered web application that automatically generates spot-the-difference puzzles from a single uploaded image. Using advanced computer vision techniques, it detects objects and creates multiple strategic modifications to generate engaging puzzle variations at multiple difficulty levels.

## ✨ Version 2.2.0 - Production Deployment Ready

**NEW:** Full production deployment support with SEO, OGP, and Google Analytics!

- 🚀 **Leapcell Deployment**: Complete deployment guide for Leapcell hosting
- 🔍 **SEO Optimization**: Meta tags, sitemap.xml, robots.txt for search engines
- 📱 **OGP Support**: Open Graph Protocol for social media sharing
- 📊 **Google Analytics**: Built-in GA4 integration for traffic tracking
- 🌐 **Custom Domain**: Ready for custom domain (spotthediff.ricezero.fun)
- ⚙️ **Environment Config**: Separate development and production configurations
- 📚 **Japanese Documentation**: Complete README_JP.md and deployment guide

[Read more about deployment features →](DEPLOYMENT.md)

## ✨ Version 2.1.1 - Security & Pages Update

**NEW:** Enhanced security measures and informational pages for production readiness!

- 🔒 **Security Headers**: CSP, HSTS, X-Frame-Options, and more via Flask-Talisman
- 🚦 **Rate Limiting**: DoS protection with configurable limits (10 uploads/min, 5 generations/min)
- 📋 **Privacy Policy**: Comprehensive data handling and privacy information
- ℹ️ **About Page**: Application features, tech stack, and version history
- ⚖️ **Terms of Service**: Usage terms, restrictions, and legal framework

[Read more about security improvements →](docs/SECURITY_IMPROVEMENTS_JP.md)

## ✨ Version 2.1 - Quality Improvements

**Enhanced quality evaluation system for more natural and polished results!**

- 🎯 **Quality Evaluator**: Automatic filtering of low-quality segments and modifications
- 📊 **31% Quality Improvement**: Better edge smoothness, natural colors, and placement
- 🔍 **Smart Retry Mechanism**: Automatically retries failed modifications with different approaches
- ⚡ **Minimal Performance Impact**: Only 0-2 seconds additional processing time

[Read more about quality improvements →](docs/QUALITY_IMPROVEMENT_JP.md)

## Features

### Core Capabilities
- **AI-Powered Object Detection**: Uses FastSAM (Segment Anything Model) for automated object segmentation
- **Intelligent Difference Generation**: Creates natural-looking differences through object deletion, color shifting, and duplication
- **Multi-Level Difficulty**: Generates puzzles at Easy, Medium, and Hard difficulty levels
- **Progress Tracking**: Real-time job status updates with progress notifications
- **Side-by-Side Comparison**: Interactive UI to compare original and modified images with reveal functionality

### Advanced Features (v2.0+)
- 🔴 **Answer Visualization**: Red circles highlight all differences automatically
- 📄 **A4 Layout Export**: Print-ready A4 landscape format (3508×2480px @ 300 DPI)
- 🎨 **Enhanced Image Processing**: Auto-quality evaluation for inpainting, color changes, and object additions
- ⚡ **Process Visualization**: Animated 5-step progress display with real-time updates
- 🌐 **Complete Japanese UI/UX**: Fully localized interface and documentation

### Security & Compliance (v2.1.1+)
- 🔒 **Security Headers**: Content Security Policy, HSTS, XSS protection
- 🚦 **Rate Limiting**: API throttling to prevent abuse (Flask-Limiter)
- 📋 **Legal Pages**: Privacy Policy, Terms of Service, About page
- 🛡️ **Input Validation**: File type, size, and dimension checks with magic byte verification

### Technical Highlights
- **Quality-First Processing**: Built-in quality evaluation system (v2.1+)
- **CPU-Only Processing**: Designed for notebooks and laptops without GPU acceleration
- **Responsive Web Interface**: Drag-and-drop image upload with real-time feedback
- **Asynchronous Job Processing**: Background task processing using ThreadPoolExecutor
- **Robust Image Validation**: File type, size, and dimension verification with magic byte checking
- **Clean Architecture**: Separated concerns between routes, services, models, and utilities for maintainability

## Quick Start

### Prerequisites
- Python 3.10 or later
- `uv` package manager (or pip)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NewSpotTheDiff
   ```

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the FastSAM model** (automatic or manual)

   Option A - Automatic (on first run):
   ```bash
   python scripts/download_model.py
   ```

   Option B - Manual:
   - Download `FastSAM-x.pt` from [Ultralytics Hub](https://hub.ultralytics.com)
   - Place it in `instance/models/` directory

4. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

   The application will be accessible at `http://localhost:5000`

## Usage

### Basic Workflow

1. **Upload Image**: Navigate to the home page and drag-and-drop or select an image
   - Supported formats: PNG, JPEG
   - Image dimensions: 512px - 4096px
   - File size limit: 10MB

2. **Select Difficulty**: Choose puzzle difficulty level
   - **Easy**: 3-4 differences (larger, more obvious changes)
   - **Medium**: 5-6 differences (mixed object sizes)
   - **Hard**: 7-8 differences (smaller, subtle changes)

3. **Generate Puzzle**: Submit for processing
   - Processing time: 8-15 seconds (primarily for object detection)

4. **View Results**: Compare original and modified images
   - Toggle "Show Differences" to reveal answer
   - Download both original and puzzle images

## Project Structure

```
NewSpotTheDiff/
├── run.py                          # Application entry point
├── pyproject.toml                  # Project configuration and dependencies
├── README.md                       # This file
├── IMPLEMENTATION_STATUS.md        # Current implementation status
├── ARCHITECTURE.md                 # System architecture and design details
├── plan.md                         # Original development plan (Japanese)
│
├── src/
│   ├── app.py                      # Flask application factory
│   ├── config.py                   # Configuration settings
│   ├── database.py                 # Database initialization and management
│   ├── exceptions.py               # Custom exceptions
│   │
│   ├── routes/                     # HTTP request handlers
│   │   ├── main.py                 # Page serving routes
│   │   ├── upload.py               # Image upload endpoint
│   │   └── generate.py             # Generation and status endpoints
│   │
│   ├── services/                   # Business logic and AI processing
│   │   ├── segmentation.py         # FastSAM wrapper for object detection
│   │   ├── saliency.py             # OpenCV visual attention analysis
│   │   ├── inpainting.py           # Object removal via inpainting
│   │   ├── color_changer.py        # HSV-based color shifting
│   │   ├── object_duplicator.py    # Object cloning and placement
│   │   ├── difference_generator.py # Main orchestration pipeline
│   │   └── job_manager.py          # Asynchronous job management
│   │
│   ├── models/                     # Data models
│   │   ├── segment.py              # Segment data structure
│   │   ├── difference.py           # Difference and result structures
│   │   └── job.py                  # Job status definition
│   │
│   ├── utils/                      # Utility functions
│   │   ├── validation.py           # File validation logic
│   │   ├── image_io.py             # Image reading/writing
│   │   └── file_manager.py         # Temporary file management
│   │
│   ├── static/
│   │   ├── css/style.css           # Responsive styling
│   │   └── js/
│   │       ├── upload.js           # Upload UI handling
│   │       ├── processing.js       # Progress monitoring
│   │       └── result.js           # Result comparison UI
│   │
│   └── templates/                  # HTML templates
│       ├── base.html               # Base layout
│       ├── index.html              # Upload page
│       ├── processing.html         # Progress page
│       └── result.html             # Results page
│
├── scripts/                        # Utility scripts
│   ├── download_model.py           # FastSAM model downloader
│   └── init_db.py                  # Database initializer
│
├── instance/                       # Runtime data (not in git)
│   ├── uploads/                    # Temporary uploaded images
│   ├── outputs/                    # Generated puzzle images
│   ├── models/                     # FastSAM model file
│   └── spotdiff.db                 # SQLite database
│
└── tests/                          # Test suite (in development)
```

## API Reference

### Upload Endpoint
**POST** `/api/upload`

Upload and validate an image for processing.

**Request:**
- Multipart form data with file field `image`

**Response:**
```json
{
  "upload_id": "uuid-string",
  "filename": "uploaded_image.png",
  "width": 1024,
  "height": 768
}
```

### Generate Endpoint
**POST** `/api/generate`

Submit an image for puzzle generation.

**Request:**
```json
{
  "upload_id": "uuid-string",
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "QUEUED"
}
```

### Status Endpoint
**GET** `/api/status/<job_id>`

Check the status of a generation job.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "PROCESSING",
  "progress": 0.45,
  "message": "Detecting objects..."
}
```

### Result Endpoint
**GET** `/api/result/<job_id>`

Retrieve completed puzzle results.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "COMPLETED",
  "original_image": "/outputs/job-id/original.png",
  "puzzle_image": "/outputs/job-id/puzzle.png",
  "differences": [
    {
      "object_id": 0,
      "type": "deletion",
      "location": {"x": 150, "y": 200}
    }
  ]
}
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Flask 3.x | HTTP request handling and routing |
| Object Detection | FastSAM (Ultralytics) | AI-powered object segmentation |
| Image Processing | OpenCV | Inpainting, saliency analysis, color manipulation |
| Image Library | Pillow | Image format compatibility |
| Numerical Computing | NumPy | Array operations and processing |
| Database | SQLite | Job and result persistence |
| Package Manager | UV | Python dependency management |

## Configuration

Key settings in `src/config.py`:

```python
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB upload limit
MIN_IMAGE_SIZE = 512                    # Minimum dimension
MAX_IMAGE_SIZE = 4096                   # Maximum dimension
PROCESSING_SIZE = 1024                  # Standard processing size
MAX_WORKERS = 4                         # Background processing threads
DIFFICULTY_LEVELS = {
    'easy': (3, 4, 0.7),               # (min_diffs, max_diffs, quality_threshold)
    'medium': (5, 6, 0.5),
    'hard': (7, 8, 0.3)
}
```

## Development

### Running Tests
```bash
pytest
```

### Code Quality
The project uses Ruff for linting with a target line length of 100 characters.

```bash
ruff check .
```

### Database Schema
The application automatically initializes SQLite with the following tables:
- `jobs` - Tracks generation job status and progress
- `results` - Stores completed puzzle results and difference information

## Performance Characteristics

- **Object Detection (FastSAM)**: 8-12 seconds per image (CPU)
- **Saliency Analysis**: ~0.1 seconds
- **Inpainting per Object**: 0.3-0.8 seconds
- **Color Shifting**: ~50-100ms per object
- **Total Processing**: 8-15 seconds depending on image complexity and difficulty

These times are based on typical notebook hardware without GPU acceleration.

## Design Principles

1. **Single Responsibility**: Each service handles one concern for easier testing and maintenance
2. **Dependency Injection**: Services are injected via Flask app factory for flexibility
3. **Progress Reporting**: Generation pipeline supports callbacks for UI updates
4. **Error Resilience**: Comprehensive validation and error handling at system boundaries
5. **Clean Architecture**: Clear separation between routes, services, models, and utilities

## Limitations & Future Improvements

### Current Limitations
- Object detection speed depends on CPU performance
- Large objects may use color change instead of deletion (OpenCV inpainting quality)
- Single image input (no batch processing)
- Differences are non-persistent (regenerated on each request)

### Planned Features
- Batch puzzle generation
- Persistent difference generation (same puzzle on revisit)
- User accounts and puzzle collections
- Multiplayer competitive mode
- GPU acceleration support
- Custom puzzle templates and difficulty fine-tuning

## Troubleshooting

### FastSAM Model Not Found
```
FileNotFoundError: FastSAM model not found
```
Solution: Run `python scripts/download_model.py`

### Image Upload Failed
- Verify image format is PNG or JPEG
- Check file size is under 10MB
- Ensure image dimensions are between 512px and 4096px

### Generation Timeout
- Processing typically takes 8-15 seconds
- Ensure browser doesn't close during processing
- Check browser console for errors

### Database Lock Error
- Ensure only one instance of the application is running
- Delete `instance/spotdiff.db` and reinitialize if corrupted

## Contributing

Contributions are welcome! Please:
1. Follow the existing code style and architecture
2. Add tests for new functionality
3. Update documentation as needed
4. Test thoroughly before submitting changes

## License

[License information to be added]

## Contact & Support

For questions, issues, or suggestions, please visit the project repository or contact the development team.