# run.py
from app import create_app

# load environment variables
app = create_app()


if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
