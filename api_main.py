# api_main.py
from fastapi import FastAPI
from api.routers import pdf_processing
from api import services as api_services_module 

app = FastAPI(
    title="PDF Structure Extractor API - Refactored",
    description="API to upload a PDF, process it to extract structure, and return a JSON. Refactored structure.",
    version="1.1.0"
)

# 包含 PDF 处理相关的路由
app.include_router(pdf_processing.router)
# 如果有其他路由组，也在这里包含进来
# from api.routers import another_router
# app.include_router(another_router.router)


@app.get("/", summary="Health Check", tags=["General"])
async def read_root():
    """
    Simple health check endpoint.
    """
    return {"status": "API is running", "message": "Welcome to the PDF Processing API!"}

# (可选) 应用启动和关闭事件
@app.on_event("startup")
async def startup_event():
    print("Application startup: Ensuring necessary directories exist...")
    # 使用上面导入的 api_services_module 来访问其内部定义的变量
    api_services_module.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)   # <--- 修改处
    api_services_module.RESULTS_DIR.mkdir(parents=True, exist_ok=True)  # <--- 修改处
    print(f"Upload directory: {api_services_module.UPLOAD_DIR}")        # <--- 修改处
    print(f"Results directory: {api_services_module.RESULTS_DIR}")      # <--- 修改处
    print("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown.")

# 如果需要直接运行 (例如 uvicorn api_main:app --reload)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)