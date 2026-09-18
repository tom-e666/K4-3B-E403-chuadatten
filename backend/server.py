from __future__ import annotations

import os
import sys
from pathlib import Path
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
from backend.tools._shared import load_lessons_data, get_all_lessons, get_lesson_by_id

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
def get_lessons():
    """Lấy danh sách tất cả các bài giảng có sẵn (kèm metadata)."""
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

