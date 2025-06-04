# api_main.py
from fastapi import FastAPI

from api.routers import pdf_processing

app = FastAPI(
    title="PDF Structure Extractor API - Refactored",
    description="API to upload a PDF, process it to extract structure, and return a JSON. Refactored structure.",
    version="1.1.0"
)

# add the pdf_processing router to the main app
app.include_router(pdf_processing.router)


@app.get("/", summary="Health Check", tags=["General"])
async def read_root():
    """
    Simple health check endpoint.
    """
    return {"status": "API is running", "message": "Welcome to the PDF Processing API!"}

# (optional) if you want to add more general endpoints, you can do so here
@app.on_event("startup")
async def startup_event():
    print("Application startup: Ensuring necessary directories exist...")
    # 可以在这里集中创建目录，而不是在 services.py 中每次都检查
    services_module = getattr(__import__("api.services", fromlist=["services"]), "services")
    services_module.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    services_module.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Upload directory: {services_module.UPLOAD_DIR}")
    print(f"Results directory: {services_module.RESULTS_DIR}")
    print("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown.")
