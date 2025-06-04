# api/routers/pdf_processing.py
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse

from api import services 

router = APIRouter(
    prefix="/pdf",  # add a prefix for all routes in this router
    tags=["PDF Processing"], # API add tags for better organization
)

@router.post("/upload/", summary="Upload PDF for Processing")
async def upload_pdf_for_processing_endpoint(
    background_tasks: BackgroundTasks,
    pdf_file: UploadFile = File(..., description="The PDF file to process."),
    model: str = Query('deepseek-chat', description="Model to use for processing."),
    toc_check_pages: int = Query(20, description="Number of pages to check for table of contents."),
    max_pages_per_node: int = Query(10, description="Maximum number of pages per node."),
    max_tokens_per_node: int = Query(20000, description="Maximum number of tokens per node."),
    if_add_node_id: str = Query('yes', description="Whether to add node id ('yes' or 'no')."),
    if_add_node_summary: str = Query('no', description="Whether to add summary to the node ('yes' or 'no')."),
    if_add_doc_description: str = Query('yes', description="Whether to add doc description ('yes' or 'no')."),
    if_add_node_text: str = Query('no', description="Whether to add text to the node ('yes' or 'no').")
):
    opt_params_dict = {
        "model": model,
        "toc_check_pages": toc_check_pages,
        "max_pages_per_node": max_pages_per_node,
        "max_tokens_per_node": max_tokens_per_node,
        "if_add_node_id": if_add_node_id,
        "if_add_node_summary": if_add_node_summary,
        "if_add_doc_description": if_add_doc_description,
        "if_add_node_text": if_add_node_text
    }

    task_id, temp_pdf_path, original_filename, processed_opt_params = await services.create_processing_task(
        pdf_file,
        opt_params_dict
    )

    # add the background task to process the PDF
    background_tasks.add_task(
        services.run_pdf_processing_task,
        task_id,
        temp_pdf_path,
        original_filename,
        processed_opt_params # pass the processed options
    )

    return {
        "message": "PDF processing started in the background.",
        "task_id": task_id,
        "filename": original_filename,
        "status_url": router.url_path_for("get_task_status_endpoint", task_id=task_id),
        "results_url": router.url_path_for("get_processing_result_endpoint", task_id=task_id)
    }

@router.get("/status/{task_id}", summary="Get Task Status", name="get_task_status_endpoint")
async def get_task_status_endpoint(task_id: str):
    status_info = await services.get_task_status_by_id(task_id)
    return status_info

@router.get("/results/{task_id}", summary="Get Processing Result", name="get_processing_result_endpoint")
async def get_processing_result_endpoint(task_id: str):
    try:
        result_file_path, download_filename = await services.get_result_file_by_task_id(task_id)
        return FileResponse(
            path=result_file_path,
            filename=download_filename,
            media_type='application/json'
        )
    except HTTPException as e:
        # error post-processing, such as file not found or task failed
        # feed the error back to the client
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})