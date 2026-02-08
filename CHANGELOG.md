# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-02-08

### Added - Production Deployment Features

#### Deployment Support
- **Leapcell Deployment**: Complete configuration and guide for Leapcell hosting service
- **requirements.txt**: Production dependencies with gunicorn WSGI server
- **Environment Configuration**: Separate development and production configs
- **.env.example**: Template for environment variables

#### SEO & Marketing
- **Meta Tags**: Comprehensive SEO meta tags in all pages
- **Open Graph Protocol**: Full OGP support for social media sharing
- **Twitter Cards**: Twitter card meta tags for rich sharing
- **sitemap.xml**: Dynamic sitemap generation for search engines
- **robots.txt**: Search engine crawler configuration
- **Canonical URLs**: Proper canonical URL tags on all pages
- **OG Image**: Custom Open Graph image for social sharing

#### Analytics & Monitoring
- **Google Analytics**: Built-in GA4 integration with configuration support
- **Conditional Loading**: GA only loads when ID is configured

#### Documentation
- **README_JP.md**: Complete Japanese version of README
- **DEPLOYMENT.md**: Comprehensive Leapcell deployment guide
- **TESTING.md**: Testing procedures and pre-deployment checklist
- **CHANGELOG.md**: This changelog file

#### Configuration Improvements
- **DevelopmentConfig**: Optimized settings for local development
- **ProductionConfig**: Security-hardened settings for production
- **Environment Detection**: Automatic config selection based on FLASK_ENV
- **Site Settings**: Centralized site configuration (domain, name, description)

#### Security Enhancements
- **CSP Updates**: Content Security Policy updated for Google Analytics
- **Environment-based HTTPS**: Conditional HTTPS enforcement
- **Production-ready Security**: Enhanced security headers for production

### Changed
- **app.py**: Updated to support environment-based configuration
- **run.py**: Modified to auto-detect environment configuration
- **config.py**: Restructured with Config base class and environment-specific classes
- **base.html**: Enhanced with full SEO, OGP, and GA support
- **index.html**: Added specific meta tags for home page
- **pages.py**: Added sitemap.xml and robots.txt endpoints
- **README.md**: Updated with v2.2.0 features
- **pyproject.toml**: Version bumped to 2.2.0

### Fixed
- **CSP Violations**: Removed inline event handlers that violated CSP
- **Favicon 404**: Added proper favicon configuration

### Technical Details
- Gunicorn configured with 2 workers and 120s timeout
- Redis optional for rate limiting in production
- Static folder properly configured for serving assets
- Database path configurable via environment

## [2.1.1] - 2026-02-08

### Added
- Security headers (CSP, HSTS, X-Frame-Options) via Flask-Talisman
- Rate limiting with Flask-Limiter
- Privacy Policy page
- About page
- Terms of Service page

### Security
- Content Security Policy implemented
- Rate limiting: 10 uploads/min, 5 generations/min
- X-Content-Type-Options, X-Frame-Options headers

## [2.1.0] - 2026-02-07

### Added
- Quality Evaluator system for automatic filtering
- Smart retry mechanism for failed modifications
- Enhanced edge smoothness evaluation
- Natural color change validation
- Better object placement quality checks

### Improved
- 31% overall quality improvement
- Minimal performance impact (0-2s additional processing)
- More reliable difference generation

## [2.0.0] - 2026-02-06

### Added
- Answer visualization with red circles
- A4 layout export (3508×2480px @ 300 DPI)
- Auto-quality evaluation for all modifications
- Animated 5-step progress display
- Complete Japanese UI/UX

### Changed
- Enhanced image processing pipeline
- Improved progress tracking
- Better error handling

## [1.0.0] - 2026-02-05

### Initial Release
- AI-powered object detection with FastSAM
- Intelligent difference generation (deletion, color change, duplication)
- Multi-level difficulty (Easy, Medium, Hard)
- Progress tracking and status updates
- Side-by-side comparison UI
- Drag-and-drop image upload
- Responsive web interface
- Asynchronous job processing
- SQLite database for job tracking

---

For upgrade instructions and migration guides, see [DEPLOYMENT.md](DEPLOYMENT.md).
