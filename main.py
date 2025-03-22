from app.main import app

# This is for Gunicorn to import directly
# The variable name 'app' is what Gunicorn looks for by default

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)