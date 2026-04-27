import os

from backend.app import app


if __name__ == "__main__":
    print("DHMB API server starting...")
    print("Dashboard: http://localhost:5000")
    print("Health: http://localhost:5000/api/health")
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", host="0.0.0.0", port=5000)
