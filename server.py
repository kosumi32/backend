from src.app import app

# if we are running this script directly, we will run the server
if __name__ == "__main__":
    import uvicorn

    # Run this on localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)