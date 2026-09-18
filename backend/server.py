from __future__ import annotations

import base64
import binascii
import mimetypes
import os
import sys
import threading
from pathlib import Path

# Python (nhất là trên Windows) không tự biết .mjs là JavaScript -> StaticFiles trả về
# content-type: text/plain, khiến trình duyệt từ chối nạp <script type="module">/import
# (bắt buộc phải là text/javascript). Đăng ký tay trước khi mount StaticFiles bên dưới.
mimetypes.add_type("text/javascript", ".mjs")
from typing import Any, Dict
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Nạp path và biến môi trường
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

from backend.env_loader import load_lab_env
load_lab_env(PROJECT_ROOT)

from backend.providers import make_provider
from backend.agent import FeynmanAgent, SessionState
from backend.tools.reporter import generate_session_report
from backend.tools._shared import (
    load_lessons_data,
    get_all_lessons,
    get_lesson_by_id,
    get_full_lessons,
    invalidate_cache,
)
from backend.lesson_ingest import generate_lesson_from_pdf, save_lesson, lesson_json_path

# Thư mục chứa các file PDF slide gốc — vừa là nguồn cho Agent 1 phân tích sinh checkpoint,
# vừa được mount tĩnh ở cuối file để khung PDF.js bên FE tải trực tiếp.
SLIDES_DIR = PROJECT_ROOT / "backend" / "data" / "vlearn-pack" / "slides"
MAX_UPLOAD_BYTES = 40 * 1024 * 1024  # trần kích thước file slide tải lên

app = FastAPI(title="Feynman AI — Reverse Tutoring API", version="1.0.0")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quản lý agent & sessions in-memory
sessions: dict[str, SessionState] = {}
agent_instance: FeynmanAgent | None = None


def get_or_create_agent() -> FeynmanAgent:
    global agent_instance
    if agent_instance is not None:
        return agent_instance

    # Tự động chọn provider dựa theo biến môi trường
    provider_name = os.getenv("LLM_PROVIDER")
    if not provider_name:
        if os.getenv("GEMINI_API_KEY"):
            provider_name = "gemini"
        elif os.getenv("OPENROUTER_API_KEY"):
            provider_name = "openrouter"
        elif os.getenv("OPENAI_API_KEY"):
            provider_name = "openai"
        else:
            provider_name = "gemini"  # mặc định

    model_name = os.getenv("LLM_MODEL")
    try:
        provider = make_provider(provider_name)
        print(f"✅ Đã khởi tạo Provider: '{provider_name}' (Model: {model_name or 'mặc định'})")
    except Exception as exc:
        print(f"⚠️ Không thể khởi tạo Provider '{provider_name}': {exc}. Chạy fallback OpenRouter/Gemini.")
        # Nếu thiếu key, provider sẽ raise lỗi khi gọi complete
        provider = make_provider("gemini")

    agent_instance = FeynmanAgent(provider=provider, model=model_name)
    return agent_instance


# ----------------- Request / Response Models -----------------
class StartSessionRequest(BaseModel):
    session_id: str | None = "default_session"
    lesson_id: str | None = "lesson_02"


class ChatMessageRequest(BaseModel):
    session_id: str | None = "default_session"
    message: str


# ----------------- API Endpoints -----------------
@app.get("/api/lessons")
def get_lessons(full: int = 0):
    """Danh sách bài giảng. full=1 -> trả nguyên vẹn cả slides + checkpoint (FE nạp 1 lần duy nhất)."""
    if full:
        return JSONResponse({"lessons": get_full_lessons()})
    return JSONResponse({"lessons": get_all_lessons()})


@app.get("/api/lessons/{lesson_id}")
def get_lesson(lesson_id: str):
    """Lấy chi tiết bài giảng bao gồm slides, transcript excerpts và checkpoints."""
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bài học: '{lesson_id}'")
    return JSONResponse(lesson)


@app.get("/api/checkpoints")
def get_checkpoints(lesson_id: str | None = None):
    """Lấy danh sách các Checkpoints bài học (mặc định lesson_02)."""
    data = load_lessons_data(lesson_id)
    return JSONResponse({
        "lesson_id": data.get("id"),
        "topic": data.get("topic"),
        "checkpoints": [
            {
                "id": cp["id"],
                "order": cp.get("order", 1),
                "short": cp.get("short", f"CP{cp.get('order', 1)}"),
                "title": cp["title"],
                "citation": cp.get("source_citation", "")
            }
            for cp in data.get("checkpoints", [])
        ]
    })


# ----------------- Agent 1: đọc slide PDF -> tự sinh checkpoint -----------------
# Mỗi lượt gọi LLM đọc trọn file PDF khá tốn thời gian và token -> chỉ cho phép đúng MỘT
# lượt phân tích chạy tại một thời điểm, các file còn lại xếp hàng đợi.
_generate_lock = threading.Lock()

# Trạng thái phân tích của từng file slide, để FE biết "AI đang đọc bài nào" mà hiển thị:
#   pending  — đã xếp hàng, chờ tới lượt
#   running  — LLM đang đọc file này
#   ready    — đã có checkpoint
#   error    — chạy hỏng, kèm lý do
slide_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _set_job(pdf_file: str, status: str, message: str = "", lesson_id: str | None = None) -> None:
    with _jobs_lock:
        slide_jobs[pdf_file] = {"status": status, "message": message, "lesson_id": lesson_id}


def _get_job(pdf_file: str) -> dict[str, Any]:
    with _jobs_lock:
        return dict(slide_jobs.get(pdf_file, {}))


def _pdf_page_count(pdf_path: Path) -> int | None:
    """Số trang thật của file PDF — dùng để chặn trường hợp LLM trả về pdf_page vượt quá số trang."""
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf_path)).pages)
    except Exception:
        return None


def _lesson_for_pdf(pdf_file: str) -> dict[str, Any] | None:
    """Tìm bài học đã sinh sẵn từ đúng file PDF này (nếu có) để khỏi gọi lại LLM."""
    for lsn in get_full_lessons():
        if lsn.get("pdf_file") == pdf_file:
            return lsn
    return None


def _safe_slide_path(pdf_file: str) -> Path:
    """Chỉ cho phép đọc file nằm ngay trong SLIDES_DIR (chặn ../ leo thư mục)."""
    name = Path(pdf_file).name
    if not name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .pdf")
    path = SLIDES_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy file slide: '{name}'")
    return path


@app.get("/api/slides")
def list_slides():
    """Liệt kê các file PDF slide có sẵn + trạng thái đã được Agent 1 phân tích hay chưa."""
    if not SLIDES_DIR.exists():
        return JSONResponse({"slides": []})

    kick_auto_ingest()  # còn file chưa phân tích (vd vừa copy thêm PDF) -> chạy tiếp, không cần bấm gì

    items = []
    for path in sorted(SLIDES_DIR.glob("*.pdf")):
        lesson = _lesson_for_pdf(path.name)
        job = _get_job(path.name)
        status = "ready" if lesson else job.get("status", "pending")
        items.append({
            "file": path.name,
            "size_mb": round(path.stat().st_size / (1024 * 1024), 1),
            "pages": _pdf_page_count(path),
            "lesson_id": lesson.get("id") if lesson else None,
            "short_title": lesson.get("short_title") if lesson else None,
            "checkpoints_count": len(lesson.get("checkpoints", [])) if lesson else 0,
            "status": status,
            "status_message": job.get("message", ""),
            "json_file": (lesson.get("_source_file") or lesson_json_path(lesson).name) if lesson else None,
        })
    return JSONResponse({"slides": items, "analyzing": any(i["status"] in ("pending", "running") for i in items)})


class UploadSlideRequest(BaseModel):
    filename: str
    data_base64: str
    overwrite: bool = False


@app.post("/api/slides/upload")
def upload_slide(req: UploadSlideRequest):
    """Nhận file PDF slide người dùng tải lên, lưu vào thư mục slides rồi cho Agent 1 phân tích ngay.

    Gửi dạng base64 trong JSON để không cần thêm phụ thuộc python-multipart.
    Trả về ngay lập tức; việc đọc slide bằng LLM chạy ở luồng nền, FE theo dõi qua GET /api/slides.
    """
    name = Path(req.filename or "").name
    if not name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ nhận file .pdf")

    try:
        raw = base64.b64decode(req.data_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Dữ liệu file không hợp lệ: {exc}") from exc

    if not raw.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File tải lên không phải PDF hợp lệ.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File quá lớn (giới hạn {MAX_UPLOAD_BYTES // (1024 * 1024)}MB).")

    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    target = SLIDES_DIR / name

    # Trùng tên mà không cho ghi đè -> tự thêm hậu tố để không đè slide của người khác.
    if target.exists() and not req.overwrite:
        stem, suffix, counter = target.stem, target.suffix, 2
        while target.exists():
            target = SLIDES_DIR / f"{stem}-{counter}{suffix}"
            counter += 1

    target.write_bytes(raw)
    _set_job(target.name, "pending", "Vừa tải lên, đang chờ AI đọc")
    kick_auto_ingest()

    return JSONResponse({
        "file": target.name,
        "size_mb": round(len(raw) / (1024 * 1024), 2),
        "pages": _pdf_page_count(target),
        "status": "pending",
        "message": f"Đã nhận '{target.name}'. AI đang đọc slide để sinh file checkpoint JSON.",
    })


class GenerateLessonRequest(BaseModel):
    pdf_file: str
    lesson_id: str | None = None
    video_title: str | None = None
    video_duration: str | None = "45 phút"
    force: bool = False


def _ingest_slide(pdf_path: Path, *, lesson_id: str | None = None, video_title: str | None = None,
                  video_duration: str | None = None) -> tuple[dict[str, Any], list[str]]:
    """Chạy Agent 1 trên 1 file PDF rồi chốt dữ liệu: gắn pdf_file, kiểm lại pdf_page, ghi lessons.json.

    Dùng chung cho cả luồng tự động chạy nền lúc khởi động lẫn lượt gọi lại tay từ FE.
    """
    with _generate_lock:  # xếp hàng: mỗi lúc chỉ 1 file được LLM đọc
        _set_job(pdf_path.name, "running", "AI đang đọc slide...")
        lesson = generate_lesson_from_pdf(
            pdf_path,
            lesson_id=lesson_id,
            video_title=video_title or pdf_path.stem,
            video_duration=video_duration or "45 phút",
        )

    lesson["pdf_file"] = pdf_path.name
    lesson.setdefault("video_title", video_title or lesson.get("short_title") or pdf_path.stem)

    # Chốt lại pdf_page: LLM có thể trả số trang không tồn tại -> ép về khoảng hợp lệ và báo rõ cho FE.
    total_pages = _pdf_page_count(pdf_path)
    warnings: list[str] = []
    for idx, cp in enumerate(lesson.get("checkpoints", []), start=1):
        page = cp.get("pdf_page")
        if not isinstance(page, int) or page < 1:
            warnings.append(f"{cp.get('short', f'CP{idx}')}: thiếu pdf_page hợp lệ -> tạm trỏ trang 1.")
            cp["pdf_page"] = 1
        elif total_pages and page > total_pages:
            warnings.append(f"{cp.get('short', f'CP{idx}')}: pdf_page={page} vượt quá {total_pages} trang -> ép về trang cuối.")
            cp["pdf_page"] = total_pages
        cp.setdefault("short", f"CP{idx}")
        cp.setdefault("order", idx)

    json_path = save_lesson(lesson)   # mỗi slide -> 1 file JSON checkpoint trong backend/data/lessons/
    lesson["_source_file"] = json_path.name
    invalidate_cache()

    # Bài học vừa đổi -> huỷ các phiên chat đang giữ checkpoint cũ của chính bài đó.
    for sid in [s_id for s_id, st in sessions.items() if st.lesson_id == lesson["id"]]:
        sessions.pop(sid, None)

    _set_job(pdf_path.name, "ready",
             f"{len(lesson.get('checkpoints', []))} checkpoint → {json_path.name}"
             + (" · " + "; ".join(warnings) if warnings else ""),
             lesson.get("id"))
    return lesson, warnings


def _auto_ingest_worker() -> None:
    """Luồng nền: lần lượt phân tích mọi file slide chưa có checkpoint, không chặn lúc server khởi động."""
    if not SLIDES_DIR.exists():
        return

    pending = [p for p in sorted(SLIDES_DIR.glob("*.pdf")) if not _lesson_for_pdf(p.name)]
    for path in pending:
        _set_job(path.name, "pending", "Đang chờ tới lượt phân tích")

    for path in pending:
        try:
            print(f"🤖 Agent 1 tự phân tích slide: {path.name} ...")
            lesson, warns = _ingest_slide(path)
            print(f"   -> {lesson['id']}: {len(lesson.get('checkpoints', []))} checkpoint"
                  + (f" (cảnh báo: {'; '.join(warns)})" if warns else ""))
        except Exception as exc:
            print(f"   ⚠ Không phân tích được {path.name}: {exc}")
            _set_job(path.name, "error", str(exc))


def kick_auto_ingest() -> None:
    """Khởi động luồng tự phân tích nếu còn slide chưa có checkpoint và chưa có luồng nào đang chạy."""
    global _auto_thread
    if _auto_thread is not None and _auto_thread.is_alive():
        return
    if not SLIDES_DIR.exists():
        return
    if not any(not _lesson_for_pdf(p.name) for p in SLIDES_DIR.glob("*.pdf")):
        return
    _auto_thread = threading.Thread(target=_auto_ingest_worker, name="auto-ingest", daemon=True)
    _auto_thread.start()


_auto_thread: threading.Thread | None = None


@app.on_event("startup")
def _on_startup() -> None:
    kick_auto_ingest()


@app.post("/api/lessons/generate")
def generate_lesson_endpoint(req: GenerateLessonRequest):
    """Phân tích lại một file slide theo yêu cầu (bình thường server đã tự chạy sẵn lúc khởi động)."""
    pdf_path = _safe_slide_path(req.pdf_file)
    existing = _lesson_for_pdf(pdf_path.name)

    if existing and not req.force:
        return JSONResponse({"lesson": existing, "cached": True, "warnings": []})

    if _generate_lock.locked():
        raise HTTPException(status_code=409, detail="Đang có một lượt phân tích slide khác chạy, vui lòng đợi.")

    try:
        lesson, warnings = _ingest_slide(
            pdf_path,
            lesson_id=req.lesson_id or (existing.get("id") if existing else None),
            video_title=req.video_title,
            video_duration=req.video_duration,
        )
    except Exception as exc:
        _set_job(pdf_path.name, "error", str(exc))
        raise HTTPException(status_code=502, detail=f"Agent 1 phân tích slide thất bại: {exc}") from exc

    return JSONResponse({"lesson": lesson, "cached": False, "warnings": warnings})


@app.post("/api/session/start")
def start_session(req: StartSessionRequest):
    """Khởi tạo phiên luyện tập Feynman mới cho bài học được chọn."""
    agent = get_or_create_agent()
    session_id = req.session_id or "default_session"
    lesson_id = req.lesson_id or "lesson_02"
    state, starter_msg = agent.start_session(session_id=session_id, lesson_id=lesson_id)
    sessions[session_id] = state

    current_cp = agent.get_current_checkpoint(state)
    checkpoints = agent.get_lesson_checkpoints(lesson_id)
    return {
        "session_id": session_id,
        "lesson_id": lesson_id,
        "starter_message": starter_msg,
        "current_checkpoint": {
            "id": current_cp["id"] if current_cp else None,
            "title": current_cp["title"] if current_cp else None,
            "index": state.current_checkpoint_index
        },
        "total_checkpoints": len(checkpoints)
    }


@app.post("/api/chat")
def chat(req: ChatMessageRequest):
    """Gửi tin nhắn giải thích từ học viên đến Bot Ngu & nhận phản hồi."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập nội dung giải thích.")

    agent = get_or_create_agent()
    session_id = req.session_id or "default_session"
    state = sessions.get(session_id)

    if not state:
        state, _ = agent.start_session(session_id)
        sessions[session_id] = state

    result = agent.chat_step(state, req.message.strip())
    return {
        "session_id": session_id,
        "assistant_text": result["assistant_text"],
        "latest_evaluation": result["latest_evaluation"],
        "advance_checkpoint": result["advance_checkpoint"],
        "next_checkpoint_title": result["next_checkpoint_title"],
        "completed": result["completed"],
        "current_checkpoint_index": state.current_checkpoint_index
    }


@app.get("/api/session/report")
def get_report(session_id: str = "default_session"):
    """Lấy báo cáo đánh giá tổng kết (% Mastery Report)."""
    state = sessions.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chưa có phiên học nào được bắt đầu.")

    eval_results = list(state.checkpoint_results.values())
    report = generate_session_report(eval_results)
    return report


# Phục vụ file PDF slide gốc (dùng trực tiếp cho khung slide-stage bên FE)
if SLIDES_DIR.exists():
    app.mount("/slides", StaticFiles(directory=str(SLIDES_DIR)), name="slides")

# Phục vụ thư mục Frontend
FE_DIR = PROJECT_ROOT / "FE" / "mock-cp2"
if FE_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FE_DIR)), name="static")
    assets_dir = FE_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    def serve_frontend():
        index_file = FE_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Feynman AI API đang chạy. Vui lòng kiểm tra FE/mock-cp2."}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Khởi chạy Feynman AI Server tại: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

