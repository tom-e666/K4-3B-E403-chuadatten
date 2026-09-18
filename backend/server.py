from __future__ import annotations

import base64
import binascii
import json
from datetime import datetime
import mimetypes
import time
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
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
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
from backend.lesson_ingest import (
    generate_lesson_from_pdf,
    generate_question_bank,
    save_lesson,
    lesson_json_path,
)

# Thư mục chứa các file PDF slide gốc — vừa là nguồn cho Agent 1 phân tích sinh checkpoint,
# vừa được mount tĩnh ở cuối file để khung PDF.js bên FE tải trực tiếp.
SLIDES_DIR = PROJECT_ROOT / "backend" / "data" / "vlearn-pack" / "slides"
MAX_UPLOAD_BYTES = 40 * 1024 * 1024  # trần kích thước file slide tải lên
# Nhật ký kết quả từng checkpoint (mỗi bài một file .jsonl) — nguồn cho báo cáo của giảng viên.
PROGRESS_DIR = PROJECT_ROOT / "backend" / "data" / "progress"

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
    # FE gửi kèm để nếu server vừa restart (phiên nằm trong RAM nên mất) thì mở lại đúng bài này,
    # thay vì rơi về lesson mặc định rồi chấm nhầm sang checkpoint của bài khác.
    lesson_id: str | None = None


# ----------------- API Endpoints -----------------
@app.get("/api/lessons")
def get_lessons(full: int = 0):
    """Danh sách bài giảng. full=1 -> trả nguyên vẹn cả slides + checkpoint (FE nạp 1 lần duy nhất)."""
    if full:
        lessons = []
        for lesson in get_full_lessons():
            pdf_file = lesson.get("pdf_file")
            lessons.append({
                **lesson,
                "pdf_missing": bool(pdf_file) and not (SLIDES_DIR / pdf_file).exists(),
            })
        return JSONResponse({"lessons": lessons})
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


@app.get("/api/report/lesson/{lesson_id}")
def lesson_report(lesson_id: str):
    """Báo cáo lớp cho một bài: checkpoint nào nhiều người hổng nhất, cần giảng lại trang nào."""
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bài học: '{lesson_id}'")

    path = PROGRESS_DIR / f"{lesson_id}.jsonl"
    records: list[dict[str, Any]] = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    by_cp: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        by_cp.setdefault(rec.get("checkpoint_id"), []).append(rec)

    items = []
    for idx, cp in enumerate(lesson.get("checkpoints", [])):
        rows = by_cp.get(cp["id"], [])
        attempts = len(rows)
        passed = sum(1 for r in rows if r.get("outcome") == "pass" and int(r.get("score", 0)) >= 80)
        gave_up = sum(1 for r in rows if r.get("outcome") == "gave_up")
        avg = int(round(sum(int(r.get("score", 0)) for r in rows) / attempts)) if attempts else 0

        missing_count: dict[str, int] = {}
        for r in rows:
            for concept in r.get("missing") or []:
                if concept:
                    missing_count[concept] = missing_count.get(concept, 0) + 1

        items.append({
            "index": idx,
            "checkpoint_id": cp["id"],
            "short": cp.get("short", f"CP{idx + 1}"),
            "title": cp.get("title", ""),
            "pdf_page": cp.get("pdf_page"),
            "attempts": attempts,
            "learners": len({r.get("session_id") for r in rows}),
            "passed": passed,
            "gave_up": gave_up,
            "pass_rate": int(round(passed / attempts * 100)) if attempts else None,
            "avg_score": avg,
            "top_missing": sorted(missing_count.items(), key=lambda kv: -kv[1])[:3],
        })

    ranked = sorted(
        [i for i in items if i["attempts"]],
        key=lambda i: (i["pass_rate"] if i["pass_rate"] is not None else 100, i["avg_score"]),
    )

    return JSONResponse({
        "lesson_id": lesson_id,
        "lesson_title": lesson.get("short_title") or lesson.get("topic", ""),
        "pdf_file": lesson.get("pdf_file"),
        "total_records": len(records),
        "learners": len({r.get("session_id") for r in records}),
        "items": items,
        "weakest": [i["checkpoint_id"] for i in ranked[:3]],
    })


@app.get("/api/report/lessons")
def lessons_with_progress():
    """Danh sách bài đã có người học, cho trang báo cáo của giảng viên chọn."""
    out = []
    for lesson in get_full_lessons():
        if not lesson.get("pdf_file"):
            continue
        path = PROGRESS_DIR / f"{lesson.get('id')}.jsonl"
        count = 0
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                count = sum(1 for line in f if line.strip())
        out.append({
            "lesson_id": lesson.get("id"),
            "title": lesson.get("short_title") or lesson.get("topic", ""),
            "checkpoints": len(lesson.get("checkpoints", [])),
            "records": count,
        })
    return JSONResponse({"lessons": out})


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

# Người học đang chat thì việc sinh câu hỏi nền phải nhường đường: cả hai dùng chung một API,
# chạy song song làm lượt trả lời chậm hẳn (và dễ dính rate limit).
_last_chat_at = 0.0
CHAT_PRIORITY_WINDOW = 25.0   # giây: im lặng đủ lâu thì việc nền mới chạy tiếp


def _mark_chat_activity() -> None:
    global _last_chat_at
    _last_chat_at = time.monotonic()


def _wait_while_user_is_chatting(label: str = "") -> None:
    waited = 0.0
    while time.monotonic() - _last_chat_at < CHAT_PRIORITY_WINDOW:
        if waited == 0.0 and label:
            print(f"⏸ Tạm dừng việc nền ({label}) vì người học đang hỏi bài...")
        time.sleep(2.0)
        waited += 2.0
    if waited and label:
        print(f"▶ Chạy tiếp việc nền ({label}) sau {waited:.0f}s chờ.")


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
            "questions_count": sum(len(cp.get("question_bank") or []) for cp in lesson.get("checkpoints", [])) if lesson else 0,
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

    # Lượt 2: mỗi checkpoint gọi LLM thêm một lần để sinh ngân hàng câu hỏi nhiều mức độ.
    # Tách khỏi lượt đọc PDF vì gộp chung làm JSON quá dài, model hay cắt bớt phần cuối.
    checkpoints = lesson.get("checkpoints", [])
    for idx, cp in enumerate(checkpoints, start=1):
        _wait_while_user_is_chatting(f"sinh câu hỏi {pdf_path.name}")
        _set_job(pdf_path.name, "running", f"Đang sinh câu hỏi cho {cp.get('short', f'CP{idx}')} ({idx}/{len(checkpoints)})...")
        try:
            cp["question_bank"] = generate_question_bank(cp, lesson_topic=lesson.get("topic", ""))
        except Exception as exc:
            # Thiếu ngân hàng câu hỏi thì checkpoint đó tự rơi về lối hỏi cũ (1 câu mở đầu, 3 lượt thử).
            print(f"   ⚠ Không sinh được câu hỏi cho {cp.get('id')}: {exc}")
            cp["question_bank"] = []
            warnings.append(f"{cp.get('short', f'CP{idx}')}: không sinh được ngân hàng câu hỏi ({exc}).")

    json_path = save_lesson(lesson)   # mỗi slide -> 1 file JSON checkpoint trong backend/data/lessons/
    lesson["_source_file"] = json_path.name
    invalidate_cache()

    # Bài học vừa đổi -> huỷ các phiên chat đang giữ checkpoint cũ của chính bài đó.
    for sid in [s_id for s_id, st in sessions.items() if st.lesson_id == lesson["id"]]:
        sessions.pop(sid, None)

    total_questions = sum(len(cp.get("question_bank") or []) for cp in lesson.get("checkpoints", []))
    _set_job(pdf_path.name, "ready",
             f"{len(lesson.get('checkpoints', []))} checkpoint · {total_questions} câu hỏi → {json_path.name}"
             + (" · " + "; ".join(warnings) if warnings else ""),
             lesson.get("id"))
    return lesson, warnings


def _lessons_missing_questions() -> list[dict[str, Any]]:
    """Bài học đã có checkpoint nhưng chưa có ngân hàng câu hỏi (vd sinh từ bản trước khi có tính năng này)."""
    result = []
    for lesson in get_full_lessons():
        cps = lesson.get("checkpoints") or []
        if not lesson.get("pdf_file") or not cps:
            continue
        if any(not cp.get("question_bank") for cp in cps):
            result.append(lesson)
    return result


def _backfill_question_banks() -> None:
    """Bổ sung ngân hàng câu hỏi cho bài học cũ — chỉ gọi LLM dạng text, KHÔNG đọc lại file PDF."""
    for lesson in _lessons_missing_questions():
        pdf_file = lesson.get("pdf_file")
        checkpoints = [cp for cp in lesson.get("checkpoints", []) if not cp.get("question_bank")]
        print(f"🤖 Bổ sung câu hỏi cho '{lesson.get('id')}' ({len(checkpoints)} checkpoint còn thiếu) ...")
        changed = False
        for idx, cp in enumerate(checkpoints, start=1):
            _wait_while_user_is_chatting(f"bổ sung câu hỏi {lesson.get('id')}")
            _set_job(pdf_file, "running",
                     f"Đang sinh câu hỏi cho {cp.get('short', f'CP{idx}')} ({idx}/{len(checkpoints)})...")
            try:
                cp["question_bank"] = generate_question_bank(cp, lesson_topic=lesson.get("topic", ""))
                changed = True
            except Exception as exc:
                print(f"   ⚠ {cp.get('id')}: {exc}")
                cp["question_bank"] = []

        if changed:
            save_lesson(lesson)
            invalidate_cache()
        total = sum(len(cp.get("question_bank") or []) for cp in lesson.get("checkpoints", []))
        _set_job(pdf_file, "ready",
                 f"{len(lesson.get('checkpoints', []))} checkpoint · {total} câu hỏi",
                 lesson.get("id"))


def _auto_ingest_worker() -> None:
    """Luồng nền: phân tích slide chưa có checkpoint, rồi bổ sung ngân hàng câu hỏi cho bài còn thiếu."""
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

    try:
        _backfill_question_banks()
    except Exception as exc:
        print(f"⚠ Lỗi khi bổ sung ngân hàng câu hỏi: {exc}")


def kick_auto_ingest() -> None:
    """Khởi động luồng tự phân tích nếu còn slide chưa có checkpoint và chưa có luồng nào đang chạy."""
    global _auto_thread
    if _auto_thread is not None and _auto_thread.is_alive():
        return
    if not SLIDES_DIR.exists():
        return
    has_new_pdf = any(not _lesson_for_pdf(p.name) for p in SLIDES_DIR.glob("*.pdf"))
    if not has_new_pdf and not _lessons_missing_questions():
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


def _log_checkpoint_result(state, result: dict[str, Any]) -> None:
    """Ghi lại kết quả một checkpoint vừa kết thúc, để giảng viên xem cả lớp hổng chỗ nào."""
    if not result.get("advance_checkpoint"):
        return
    ev = result.get("latest_evaluation") or {}
    try:
        PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "session_id": state.session_id,
            "lesson_id": state.lesson_id,
            "checkpoint_id": ev.get("checkpoint_id"),
            "checkpoint_title": ev.get("checkpoint_title"),
            "score": ev.get("mastery_score", 0),
            "outcome": ev.get("outcome"),
            "covered_count": ev.get("covered_count", 0),
            "rubric_total": ev.get("rubric_total", 0),
            "missing": [m.get("concept", "") for m in (ev.get("missing_points") or [])],
        }
        with open(PROGRESS_DIR / f"{state.lesson_id}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"⚠ Không ghi được nhật ký tiến độ: {exc}")


def _resolve_session(agent, session_id: str, lesson_id: str | None):
    """Lấy phiên đang có, hoặc mở phiên mới đúng bài. Lệch bài cũng mở lại cho khớp."""
    state = sessions.get(session_id)
    if state is None or (lesson_id and state.lesson_id != lesson_id):
        if state is not None and lesson_id:
            print(f"ℹ Phiên '{session_id}' đang ở '{state.lesson_id}' nhưng FE hỏi bài '{lesson_id}' -> mở lại phiên.")
        state, _ = agent.start_session(session_id, lesson_id) if lesson_id else agent.start_session(session_id)
        sessions[session_id] = state
    return state


@app.post("/api/chat")
def chat(req: ChatMessageRequest):
    """Gửi tin nhắn giải thích từ học viên đến Bot Ngu & nhận phản hồi."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập nội dung giải thích.")

    _mark_chat_activity()
    agent = get_or_create_agent()
    session_id = req.session_id or "default_session"
    state = _resolve_session(agent, session_id, req.lesson_id)

    result = agent.chat_step(state, req.message.strip())
    _log_checkpoint_result(state, result)
    return {
        "session_id": session_id,
        "assistant_text": result["assistant_text"],
        "professor_message": result.get("professor_message", ""),
        "latest_evaluation": result["latest_evaluation"],
        "advance_checkpoint": result["advance_checkpoint"],
        "next_checkpoint_title": result["next_checkpoint_title"],
        "next_question": result.get("next_question"),
        "current_question": result.get("current_question"),
        "completed": result["completed"],
        "current_checkpoint_index": state.current_checkpoint_index
    }


@app.post("/api/chat/stream")
def chat_stream(req: ChatMessageRequest):
    """Như /api/chat nhưng trả dần qua SSE: đẩy kết quả chấm trước, rồi stream lời thoại từng đoạn.

    Nhờ vậy người học thấy ngay mình đạt bao nhiêu ý trong khi câu nói của bạn học còn đang chảy ra,
    thay vì nhìn màn hình đứng im vài giây.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập nội dung giải thích.")

    _mark_chat_activity()
    agent = get_or_create_agent()
    session_id = req.session_id or "default_session"
    state = _resolve_session(agent, session_id, req.lesson_id)

    def event_source():
        try:
            for event, payload in agent.chat_step_stream(state, req.message.strip()):
                _mark_chat_activity()   # giữ nhịp: còn đang stream thì việc nền vẫn phải nhường
                if event == "done":
                    _log_checkpoint_result(state, payload)
                    payload = {**payload, "session_id": session_id,
                               "current_checkpoint_index": state.current_checkpoint_index}
                yield f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except Exception as exc:                      # nổ giữa chừng -> báo cho FE để rơi về /api/chat
            print(f"⚠️ Lỗi khi stream hội thoại: {exc}")
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/session/report")
def get_report(session_id: str = "default_session"):
    """Thẻ tổng kết cuối phiên: điểm từng checkpoint, chỗ cần học lại và thứ tự nên học lại."""
    state = sessions.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chưa có phiên học nào được bắt đầu.")

    lesson = get_lesson_by_id(state.lesson_id) or {}
    checkpoints = lesson.get("checkpoints", [])
    items = []
    for idx, cp in enumerate(checkpoints):
        res = state.checkpoint_results.get(cp["id"]) or {}
        outcome = (res.get("status") or "").lower()
        score = int(res.get("mastery_score", 0) or 0)
        done = bool(res)
        if not done:
            status = "chua_hoc"
        elif outcome == "pass" and score >= 80:
            status = "dat"
        else:
            status = "can_hoc_lai"
        items.append({
            "index": idx,
            "checkpoint_id": cp["id"],
            "short": cp.get("short", f"CP{idx + 1}"),
            "title": cp.get("title", ""),
            "pdf_page": cp.get("pdf_page"),
            "source_citation": cp.get("source_citation", ""),
            "score": score,
            "status": status,
            "outcome": outcome,
            "questions_used": res.get("questions_used", 0),
            "trials": res.get("trials", 0),
            "missing_points": [m.get("concept", "") for m in (res.get("missing_points") or [])],
        })

    scored = [i for i in items if i["status"] != "chua_hoc"]
    overall = int(round(sum(i["score"] for i in scored) / len(scored))) if scored else 0

    # Nên học lại phần nào trước: điểm thấp nhất trước, chưa học xếp cuối cùng vì còn nguyên cơ hội tự làm.
    priority = sorted(
        [i for i in items if i["status"] != "dat"],
        key=lambda i: (0 if i["status"] == "can_hoc_lai" else 1, i["score"], i["index"]),
    )

    return {
        "session_id": session_id,
        "lesson_id": state.lesson_id,
        "lesson_title": lesson.get("short_title") or lesson.get("topic", ""),
        "pdf_file": lesson.get("pdf_file"),
        "overall_score": overall,
        "total_checkpoints": len(items),
        "passed": sum(1 for i in items if i["status"] == "dat"),
        "need_review": sum(1 for i in items if i["status"] == "can_hoc_lai"),
        "items": items,
        "recommended": [i["index"] for i in priority[:3]],
        "completed": state.completed,
    }


class RestartCheckpointRequest(BaseModel):
    session_id: str | None = "default_session"
    lesson_id: str | None = None
    checkpoint_index: int


@app.post("/api/session/restart_checkpoint")
def restart_checkpoint(req: RestartCheckpointRequest):
    """Học lại đúng một checkpoint: xoá tiến trình cũ của nó và mở lại bằng câu hỏi dễ nhất."""
    agent = get_or_create_agent()
    session_id = req.session_id or "default_session"
    state = _resolve_session(agent, session_id, req.lesson_id)

    checkpoints = agent.get_lesson_checkpoints(state.lesson_id)
    idx = req.checkpoint_index
    if not (0 <= idx < len(checkpoints)):
        raise HTTPException(status_code=400, detail=f"Checkpoint không hợp lệ: {idx}")

    cp = checkpoints[idx]
    state.current_checkpoint_index = idx
    state.completed = False
    state.checkpoint_results.pop(cp["id"], None)
    _, opening = agent.start_checkpoint(state, cp)

    return {
        "session_id": session_id,
        "lesson_id": state.lesson_id,
        "checkpoint_index": idx,
        "checkpoint_id": cp["id"],
        "checkpoint_title": cp.get("title", ""),
        "opening_message": opening,
    }


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

    @app.get("/teacher")
    def serve_teacher_report():
        """Trang báo cáo lớp cho giảng viên."""
        page = FE_DIR / "teacher.html"
        if page.exists():
            return FileResponse(str(page))
        raise HTTPException(status_code=404, detail="Chưa có trang báo cáo giảng viên.")

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

