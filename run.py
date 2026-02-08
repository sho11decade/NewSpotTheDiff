"""Application entry point."""

import os
from src.app import create_app

# Create app with environment-based configuration
config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
