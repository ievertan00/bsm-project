import os
from app import app

if __name__ == "__main__":
    # Get the port from the environment variable, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)