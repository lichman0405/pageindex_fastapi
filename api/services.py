# api/services.py
import os
import json
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException # BackgroundTasks 会在 router 层传入

# 核心应用逻辑导入
from app.core.document_parser import page_index_main
from app.utils.config_utils import config # 确保导入路径正确

# --- 目录定义 ---
BASE_API_DIR = Path(__file__).resolve().parent # api/ 目录
PROJECT_ROOT_DIR = BASE_API_DIR.parent # 项目根目录

UPLOAD_DIR = PROJECT_ROOT_DIR / "uploads_api"
RESULTS_DIR = PROJECT_ROOT_DIR / "api_results"

# 确保目录存在 (在应用启动时创建一次可能更好，但这里为了服务独立性)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# --- 任务状态管理 (内存中) ---
# 生产环境建议使用 Redis 或数据库
tasks_status = {}

# --- 辅助函数 ---
def str_to_bool(value: str) -> bool:
    return value.lower() in ('yes', 'true', 't', '1')

# --- PDF 处理核心服务 ---
def run_pdf_processing_task(
    task_id: str,
    pdf_path: Path,
    original_filename: str,
    opt_params: dict # 包含已转换为布尔值的参数
):
    """
    在后台执行 PDF 处理。
    此函数由 BackgroundTasks 调用。
    """
    current_status = tasks_status.get(task_id, {})
    current_status.update({"status": "processing", "filename": original_filename, "details": "Initializing PDF processing..."})
    tasks_status[task_id] = current_status

    print(f"Task {task_id}: Starting processing for {original_filename} with options: {opt_params}")

    try:
        # 调用项目核心的 config 和 page_index_main
        processing_options = config(**opt_params)

        tasks_status[task_id]["details"] = "Core processing started..."
        toc_with_page_number = page_index_main(str(pdf_path), processing_options)

        tasks_status[task_id]["details"] = "Processing complete, saving results..."

        pdf_name_base = Path(original_filename).stem
        result_filename = f"{pdf_name_base}_structure.json"
        result_filepath = RESULTS_DIR / result_filename

        with open(result_filepath, 'w', encoding='utf-8') as f:
            json.dump(toc_with_page_number, f, indent=2, ensure_ascii=False)

        tasks_status[task_id].update({
            "status": "completed",
            "result_path": str(result_filepath),
            "details": "Results saved successfully."
        })
        print(f"Task {task_id}: Completed successfully. Result at {result_filepath}")

    except Exception as e:
        error_message = f"Error during PDF processing for task {task_id}: {str(e)}"
        tasks_status[task_id].update({"status": "failed", "error": error_message})
        print(error_message)

    finally:
        # 清理上传的临时文件
        if pdf_path.exists():
            try:
                os.remove(pdf_path)
                print(f"Task {task_id}: Cleaned up temporary file {pdf_path}")
            except OSError as e_remove:
                print(f"Task {task_id}: Error cleaning up temporary file {pdf_path}: {e_remove}")

async def create_processing_task(
    pdf_file, # UploadFile object
    opt_params_dict: dict # 包含 API 传入的原始参数
):
    """
    创建并初始化一个新的 PDF 处理任务。
    返回 task_id 和原始文件名。
    """
    task_id = str(uuid.uuid4())
    original_filename = pdf_file.filename if pdf_file.filename else "uploaded_file.pdf"

    safe_filename = f"{task_id}_{Path(original_filename).name}"
    temp_pdf_path = UPLOAD_DIR / safe_filename

    try:
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)
        print(f"File {original_filename} uploaded as {temp_pdf_path} for task {task_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save uploaded file: {str(e)}")
    finally:
        pdf_file.file.close()

    # 转换布尔参数
    processed_opt_params = {
        "model": opt_params_dict['model'],
        "toc_check_page_num": opt_params_dict['toc_check_pages'],
        "max_page_num_each_node": opt_params_dict['max_pages_per_node'],
        "max_token_num_each_node": opt_params_dict['max_tokens_per_node'],
        "if_add_node_id": str_to_bool(opt_params_dict['if_add_node_id']),
        "if_add_node_summary": str_to_bool(opt_params_dict['if_add_node_summary']),
        "if_add_doc_description": str_to_bool(opt_params_dict['if_add_doc_description']),
        "if_add_node_text": str_to_bool(opt_params_dict['if_add_node_text'])
    }

    # 初始化任务状态
    tasks_status[task_id] = {
        "status": "pending",
        "filename": original_filename,
        "details": "Task accepted, waiting for background processing to start."
    }

    return task_id, temp_pdf_path, original_filename, processed_opt_params

async def get_task_status_by_id(task_id: str):
    status_info = tasks_status.get(task_id)
    if not status_info:
        raise HTTPException(status_code=404, detail="Task not found.")
    return status_info

async def get_result_file_by_task_id(task_id: str):
    status_info = await get_task_status_by_id(task_id) # 复用状态获取逻辑

    if status_info["status"] == "completed":
        result_path = status_info.get("result_path")
        if result_path and Path(result_path).exists():
            pdf_name_base = Path(status_info["filename"]).stem
            download_filename = f"{pdf_name_base}_structure.json"
            return Path(result_path), download_filename # 返回路径和建议的文件名
        else:
            raise HTTPException(status_code=404, detail="Result file not found, though task marked completed.")
    elif status_info["status"] == "failed":
        raise HTTPException(status_code=500, detail=f"Processing failed: {status_info.get('error')}")
    else: # pending or processing
        raise HTTPException(status_code=202, detail=f"Processing not yet complete. Status: {status_info['status']}")