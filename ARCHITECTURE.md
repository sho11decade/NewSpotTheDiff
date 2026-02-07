# Architecture

## System Design Overview

NewSpotTheDiff follows a **clean architecture** pattern with clear separation of concerns across multiple layers. This document describes the system design, data flow, and architectural patterns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client (Browser)                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────────────┐
│                   Flask Web Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ routes/main  │  │ routes/upload│  │ routes/generate       │  │
│  │ (Page routes)│  │ (File upload)│  │ (API endpoints)       │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Service Layer
┌─────────────────────▼───────────────────────────────────────────┐
│              Business Logic & Processing                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │          DifferenceGenerator (Orchestrator)                 ││
│  │  • Coordinates all services                                 ││
│  │  • Manages processing pipeline                              ││
│  │  • Reports progress                                         ││
│  └──────┬──────────────────────────────────────────────────┬───┘│
│         │                                                  │     │
│  ┌──────▼────────────┐    ┌──────────────────────────┐   │     │
│  │ Segmentation      │    │ Saliency Analysis        │   │     │
│  │ (FastSAM)         │    │ (OpenCV Spectral        │   │     │
│  │ • Object detection│    │  Residual)              │   │     │
│  │ • Mask generation │    │ • Attention mapping     │   │     │
│  └───────────────────┘    └──────────────────────────┘   │     │
│                                                           │     │
│  ┌──────────────────┐  ┌──────────────┐  ┌────────────┐ │     │
│  │ Inpainting       │  │ Color        │  │ Object     │ │     │
│  │ (OpenCV NS)      │  │ Changer      │  │ Duplicator │ │     │
│  │ • Object removal │  │ (HSV Shift)  │  │ • Cloning  │─┘     │
│  │ • Blending       │  │ • Blending   │  │ • Placement│       │
│  └──────────────────┘  └──────────────┘  └────────────┘       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          JobManager (Async Processing)                   │ │
│  │  • ThreadPoolExecutor backend                           │ │
│  │  • Job state management                                 │ │
│  │  • Queue processing                                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Persistence & Utilities
┌─────────────────────▼───────────────────────────────────────────┐
│                    Data Layer                                    │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐ │
│  │ Database         │  │ File System                          │ │
│  │ (SQLite)         │  │ • Temporary uploads                  │ │
│  │ • Jobs table     │  │ • Output images                      │ │
│  │ • Results table  │  │ • FastSAM model cache                │ │
│  └──────────────────┘  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Layered Architecture

### 1. Presentation Layer (`routes/`)
Handles HTTP requests and responses.

**Files:**
- `routes/main.py` - Serves HTML pages (upload, processing, results)
- `routes/upload.py` - Image upload endpoint with validation
- `routes/generate.py` - Puzzle generation and status API

**Responsibilities:**
- Request validation and parameter extraction
- Response formatting (JSON/HTML)
- Error handling and HTTP status codes
- Basic security checks

### 2. Business Logic Layer (`services/`)
Core AI and image processing services.

**Service Diagram:**
```
DifferenceGenerator (Main Orchestrator)
    ├── calls → SegmentationService
    ├── calls → SaliencyService
    ├── calls → InpaintingService
    ├── calls → ColorChangerService
    ├── calls → ObjectDuplicatorService
    └── uses → JobManager (for async execution)

JobManager
    ├── manages → ThreadPoolExecutor
    ├── tracks → Job states
    └── persists → Database
```

**Service Descriptions:**

#### SegmentationService
- **Purpose**: Detect objects in images using FastSAM AI model
- **Input**: Image array
- **Output**: List of Segment objects (masks, bounding boxes, labels)
- **Processing Time**: 8-12 seconds per image
- **Key Methods**:
  - `segment(image)` - Runs FastSAM on image
  - Model cached after first load

#### SaliencyService
- **Purpose**: Identify visually prominent areas
- **Input**: Image array
- **Output**: Saliency map (grayscale heatmap)
- **Algorithm**: OpenCV Spectral Residual
- **Processing Time**: ~0.1 seconds
- **Use Case**: Identifies which objects are most visually important

#### InpaintingService
- **Purpose**: Remove objects by filling with context
- **Input**: Image, mask, inpaint radius
- **Output**: Inpainted image (object removed)
- **Algorithm**: OpenCV Navier-Stokes
- **Processing Time**: 0.3-0.8 seconds per object
- **Trade-off**: Works better on smaller objects; large objects may show artifacts

#### ColorChangerService
- **Purpose**: Modify object colors naturally
- **Input**: Image, mask, hue shift amount
- **Output**: Color-modified image
- **Algorithm**: HSV space hue rotation with Gaussian blur blending
- **Processing Time**: 50-100 ms per object
- **Benefits**: Preserves texture, looks natural

#### ObjectDuplicatorService
- **Purpose**: Clone objects and place them nearby
- **Input**: Image, mask, target location
- **Output**: Image with duplicated object
- **Strategy**: Smart placement to avoid overlaps with existing objects
- **Processing Time**: ~100 ms per object
- **Constraint**: Stays within image bounds and respects existing content

#### DifferenceGeneratorService (Orchestrator)
- **Purpose**: Coordinates all services to create puzzle differences
- **Workflow**:
  1. Segment image → get objects
  2. Analyze saliency → identify important objects
  3. Select objects based on difficulty
  4. Apply modifications (deletion, color change, addition)
  5. Save result images
- **Progress Reporting**: Callback mechanism for UI updates
- **Smart Selection**:
  - Easy: Larger objects, more obvious changes
  - Medium: Mixed sizes
  - Hard: Smaller objects, subtle changes
- **Modification Logic**:
  - Prefers deletion for small objects (good inpainting results)
  - Prefers color change for medium objects (safer, faster)
  - Prefers addition for large objects (avoids inpainting complexity)

#### JobManager
- **Purpose**: Asynchronous background task processing
- **Mechanism**: ThreadPoolExecutor with configurable workers (default: 4)
- **Job States**: QUEUED → PROCESSING → COMPLETED (or FAILED)
- **Features**:
  - Thread-safe queue management
  - Progress tracking with callbacks
  - Database persistence
  - State retrieval by job ID

### 3. Data Layer (`models/`, `database.py`, `utils/`)

**Data Models:**
```python
@dataclass
class Segment:
    """Detected object"""
    id: int
    mask: np.ndarray  # Binary mask
    bbox: tuple        # (x, y, width, height)
    area: int         # Pixel count
    label: str        # Object class if available

@dataclass
class Difference:
    """One puzzle difference"""
    object_id: int
    type: str          # 'deletion', 'color_change', 'addition'
    location: dict     # {'x': int, 'y': int}

@dataclass
class GenerationResult:
    """Completed puzzle"""
    job_id: str
    original_image: np.ndarray
    puzzle_image: np.ndarray
    differences: List[Difference]
    timestamp: datetime
```

**Database Schema:**
```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    status TEXT,
    progress REAL,
    message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE results (
    id INTEGER PRIMARY KEY,
    job_id TEXT UNIQUE,
    original_path TEXT,
    puzzle_path TEXT,
    differences_json TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

**File Management:**
- Temporary uploads: `instance/uploads/{upload_id}/`
- Generated outputs: `instance/outputs/{job_id}/`
- Model cache: `instance/models/FastSAM-x.pt`

### 4. Frontend Layer (`templates/`, `static/`)

**Page Flow:**
```
index.html (Upload)
    ↓ [Drag-drop or select image]
    ↓ /api/upload → validation
    ↓
processing.html (Progress)
    ↓ [2s polling to /api/status]
    ↓ /api/generate → async processing begins
    ↓
result.html (Results)
    ↓ [Compare images, toggle reveal]
    ↓ Download original and puzzle
```

**Static Assets:**
- `css/style.css` - Responsive design with CSS variables
- `js/upload.js` - Drag-drop, preview, form submission
- `js/processing.js` - Status polling, progress bar updates
- `js/result.js` - Image comparison toggle, downloads

## Data Flow

### Complete Puzzle Generation Flow

```
1. User uploads image
   ├─ POST /api/upload
   ├─ Validation (format, size, dimensions)
   ├─ Magic byte verification
   └─ Returns upload_id

2. User submits generation request
   ├─ POST /api/generate {upload_id, difficulty}
   ├─ JobManager enqueues job
   └─ Returns job_id

3. Background processing (DifferenceGenerator)
   ├─ Load image
   ├─ [progress: 10%] SegmentationService.segment()
   │  └─ FastSAM detects objects (8-12 seconds)
   ├─ [progress: 20%] SaliencyService.analyze()
   │  └─ Find important regions (~0.1 seconds)
   ├─ [progress: 30%] Select objects based on difficulty
   ├─ [progress: 40-90%] Apply modifications
   │  ├─ InpaintingService.inpaint() (deletion)
   │  ├─ ColorChangerService.shift_color() (color change)
   │  └─ ObjectDuplicatorService.duplicate() (addition)
   ├─ [progress: 95%] Save images
   ├─ [progress: 100%] Update database
   └─ Job status: COMPLETED

4. Status polling
   ├─ GET /api/status/{job_id}
   ├─ Returns current progress and status
   └─ Frontend updates UI

5. Result retrieval
   ├─ GET /api/result/{job_id}
   ├─ Returns images and difference metadata
   └─ Frontend displays puzzle
```

## Design Patterns

### 1. Service Layer Pattern
Each processing component is a separate service with single responsibility.

**Benefits:**
- Easy to test (mock external dependencies)
- Easy to replace (swap implementation)
- Future GPU migration simplified

### 2. Dependency Injection (DI)
Services are created in `app.py` factory and passed to route handlers.

```python
# In app.py
segmentation_service = SegmentationService()
generator_service = DifferenceGenerator(...)
job_manager = JobManager()

# In routes
@generate_bp.route('/api/generate', methods=['POST'])
def generate(generator_service, job_manager):
    job_id = job_manager.submit(generator_service.generate, ...)
```

**Benefits:**
- Loose coupling between components
- Easy testing with mock objects
- Flexible configuration

### 3. Progress Callback Pattern
Long-running operations report progress to UI via callbacks.

```python
def generate(image, progress_callback=None):
    if progress_callback:
        progress_callback(0.1, "Detecting objects...")

    segments = segmentation_service.segment(image)

    if progress_callback:
        progress_callback(0.2, "Analyzing saliency...")
```

**Benefits:**
- Real-time UI feedback
- Non-blocking async operations
- Better user experience

### 4. Strategy Pattern
Different modification types (deletion, color change, addition) implemented as strategies.

```python
class DifferenceStrategy:
    def apply(image, segment) -> image

class DeletionStrategy(DifferenceStrategy): ...
class ColorChangeStrategy(DifferenceStrategy): ...
class AdditionStrategy(DifferenceStrategy): ...
```

### 5. Factory Pattern
Flask app factory pattern for configuration and service initialization.

```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize services
    services = ServiceContainer()

    # Register blueprints
    app.register_blueprint(routes.main_bp)
    app.register_blueprint(routes.upload_bp)
    app.register_blueprint(routes.generate_bp)

    return app
```

## Error Handling Strategy

### Validation Layer (Boundaries)
- Input validation at HTTP endpoints
- File type and size checks
- Magic byte verification
- Dimension constraints

### Processing Layer
- Graceful degradation for segmentation failures
- Fallback difference types
- Timeout handling for long operations

### User Feedback
- Clear error messages in JSON responses
- User-friendly HTML error pages
- Logging for debugging

## Performance Considerations

### Bottleneck: FastSAM Detection (8-12 seconds)
- Model loaded once and cached
- Cannot be parallelized (single image)
- CPU-only design is intentional

### Optimization: Lazy Loading
- FastSAM model loaded on first request
- Subsequent requests reuse cached model

### Threading
- ThreadPoolExecutor isolates processing
- Multiple puzzles can generate simultaneously
- UI remains responsive during processing

## Testing Strategy (Pending)

### Unit Tests (target)
- Services independently tested with mocks
- Utility functions for image operations
- Configuration validation

### Integration Tests
- API endpoint testing
- End-to-end workflow
- Database operations

### Marked Tests
```python
@pytest.mark.slow
def test_fastsam_segmentation():
    """Skipped in CI without --slow flag"""
```

## Deployment Considerations

### Current State
- Development server (Flask debug mode)
- Single-threaded for HTTP (ThreadPoolExecutor for processing)
- In-memory session management

### Production Readiness
- Replace with Gunicorn WSGI server
- Use environment variables for config
- Add proper logging system
- Set up reverse proxy (Nginx)
- Implement request rate limiting
- Add health check endpoints

## Future Architecture Improvements

### 1. GPU Support
Current architecture supports adding GPU variants:
```python
class SegmentationService:
    def __init__(self, device='cpu'):
        self.device = device  # 'cpu' or 'cuda'
```

### 2. Caching Layer
Add Redis for job results:
```python
class ResultCache:
    def get(self, image_hash): ...
    def set(self, image_hash, result): ...
```

### 3. Persistent Storage
Current: Regenerates on each request
Future: Store puzzles, replay feature

### 4. Microservices
Separate components:
- API server (FastAPI)
- Processing workers (separate Docker containers)
- Database (PostgreSQL)
- Cache (Redis)

### 5. Queue System
Replace ThreadPoolExecutor with Celery/RQ:
- Better job tracking
- Distributed processing
- Better failure recovery

## Configuration Management

All settings in `src/config.py`:
- Image size constraints
- Difficulty parameters
- Processing configuration
- Database path
- Temporary file locations

Environment-specific configs can be added:
```python
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

## Conclusion

NewSpotTheDiff uses a clean, modular architecture that prioritizes:
- **Simplicity**: Single responsibility for each component
- **Maintainability**: Clear data flow and dependencies
- **Testability**: Isolated services with clear interfaces
- **Extensibility**: Easy to add features or replace implementations

The architecture scales from laptop to cloud deployment with minimal changes.
