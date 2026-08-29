"""
RevMatrix AI - Runner Script
Starts the FastAPI application on http://localhost:8000
"""
import uvicorn

if __name__ == "__main__":
    print("===================================================================")
    print("  🚀 Starting RevMatrix AI (Razorpay Buildathon - Track 03)  ")
    print("  🌐 Dashboard: http://localhost:8000                             ")
    print("  📄 API Docs:  http://localhost:8000/docs                        ")
    print("===================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
