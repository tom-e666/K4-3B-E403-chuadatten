from __future__ import annotations

import os
import re
from typing import Any
from ._shared import get_checkpoint_by_id


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def match_keyword(kw: str, text: str) -> bool:
    if len(kw) <= 2:
        return bool(re.search(rf"\b{re.escape(kw)}\b", text))
    return kw in text


# Từ khóa khái niệm đặc trưng cho từng rubric point của các bài học
CONCEPT_KEYWORDS: dict[str, list[list[str]]] = {
    # --- Lesson 2 (Transformer Architecture) ---
    "q_k_v_roles": [
        ["query", "q"],
        ["key", "k"],
        ["value", "v", "giá trị", "nội dung"]
    ],
    "attention_score": [
        ["dot product", "tích vô hướng", "nhân", "tương đồng", "score", "điểm số", "liên quan"]
    ],
    "softmax_value": [
        ["softmax", "chuẩn hóa", "xác suất", "trọng số"],
        ["value", "v", "giá trị"]
    ],
    "subspace_representation": [
        ["không gian", "subspace", "nhiều khía cạnh", "khác nhau", "góc nhìn", "ngữ pháp", "ngữ nghĩa"]
    ],
    "prevent_averaging": [
        ["trung bình", "average", "averaging", "lu mờ", "triệt tiêu", "mất thông tin", "đè lên nhau"]
    ],
    "concat_linear": [
        ["ghép", "nối", "concat", "concatenate"],
        ["chiếu", "linear", "ma trận", "w_o", "kích thước", "chiều"]
    ],
    "permutation_invariance": [
        ["song song", "bất biến", "hoán vị", "permutation", "không có thứ tự", "cùng lúc", "tuần tự"]
    ],
    "inject_order": [
        ["vị trí", "thứ tự", "position", "positional", "cộng", "cung cấp", "bổ sung"]
    ],
    "sin_cos_patterns": [
        ["sin", "cos", "tần số", "hàm", "vector vị trí", "khoảng cách"]
    ],

    # --- Lesson 1 (Foundation & LLM Context) ---
    "next_token_prediction": [
        ["dự đoán", "predict", "tiếp theo", "next token", "next-token", "xác suất", "probability"]
    ],
    "hallucination_cause": [
        ["ảo giác", "hallucination", "bịa", "sai", "thuận tai", "mượt", "nối từ", "tự tin", "mạch lạc"]
    ],
    "token_streaming": [
        ["token", "chẻ nhỏ", "đơn vị", "streaming", "tuần tự", "vòng lặp", "append"]
    ],
    "context_window_def": [
        ["cửa sổ", "context window", "bối cảnh", "ngữ cảnh", "bàn làm việc", "giới hạn"]
    ],
    "context_rot": [
        ["context rot", "quên", "loãng", "chú ý sai", "phân tán", "kém đi", "overload"]
    ],
    "context_management": [
        ["chọn lọc", "quản lý", "tinh gọn", "compact", "ghi lại", "plan", "chất lượng", "less is more"]
    ],
    "rnn_sequential_bottleneck": [
        ["rnn", "tuần tự", "từng chữ", "word by word", "quên", "chậm", "cổ chai", "bottleneck"]
    ],
    "attention_parallel": [
        ["attention", "toàn bộ", "song song", "ma trận", "liên kết", "quan hệ", "cùng lúc"]
    ],
    "gpu_parallel_advantage": [
        ["gpu", "song song", "tận dụng", "nhanh", "huấn luyện", "tính toán"]
    ],

    # --- Lesson 3 (AI Product & Problem Definition) ---
    "jumping_to_solution": [
        ["nhảy vào", "giải pháp", "solution", "quán tính", "vội vàng", "lãnh đạo", "sếp", "jumping"]
    ],
    "pain_point_discovery": [
        ["pain point", "nỗi đau", "vấn đề", "5 whys", "hỏi", "gốc rễ", "root cause", "thực sự", "insight"]
    ],
    "simple_alternatives": [
        ["đơn giản", "thay thế", "thủ công", "quy trình", "chưa cần ai", "script", "tối ưu"]
    ],
    "project_manager_role": [
        ["project", "tiến độ", "ngân sách", "budget", "spec", "bàn giao", "điều phối", "đúng hạn"]
    ],
    "product_manager_role": [
        ["product", "người dùng", "user", "thị trường", "bài toán", "đáng làm", "tính năng", "user-centered"]
    ],
    "ai_product_uniqueness": [
        ["xác suất", "kỳ vọng", "thay đổi", "cải tiến", "liên tục", "chi phí chuyển đổi", "lỗi", "đo lường"]
    ],
    "dogfooding_definition": [
        ["dogfood", "dogfooding", "tự dùng", "chính mình", "ăn thức ăn", "user đầu tiên", "người dùng"]
    ],
    "dogfooding_benefits": [
        ["tester", "phản hồi", "feedback loop", "cảm nhận", "nhanh chóng", "tối ưu", "phát hiện"]
    ],
    "dogfooding_examples": [
        ["jira", "slack", "claude code", "anthropic", "ví dụ", "atlassian"]
    ]
}


def grade_explanation(checkpoint_id: str, user_explanation: str) -> dict[str, Any]:
    """
    Đánh giá lời giải thích của học viên đối chiếu với Rubric Points của Checkpoint.
    Trả về: % Mastery, danh sách ý đạt, ý hổng, và trạng thái PASS (>=80%) hoặc NEEDS_IMPROVEMENT.
    """
    cp = get_checkpoint_by_id(checkpoint_id)
    if not cp:
        return {
            "error": "checkpoint_not_found",
            "message": f"Không tìm thấy checkpoint '{checkpoint_id}' để chấm điểm."
        }

    norm_text = normalize_text(user_explanation)
    rubric_points = cp.get("rubric_points", [])
    
    total_weight = sum(pt.get("weight", 30) for pt in rubric_points)
    earned_weight = 0.0
    covered_points = []
    missing_points = []

    # Chấm từng tiêu chí theo từ khóa ngữ nghĩa
    for pt in rubric_points:
        pt_id = pt.get("id", "")
        weight = pt.get("weight", 30)
        keywords_groups = CONCEPT_KEYWORDS.get(pt_id, [])

        matched = True
        if keywords_groups:
            for group in keywords_groups:
                if not any(match_keyword(kw, norm_text) for kw in group):
                    matched = False
                    break
        else:
            matched = any(match_keyword(w, norm_text) for w in normalize_text(pt.get("concept", "")).split())

        if matched:
            earned_weight += weight
            covered_points.append({
                "id": pt_id,
                "concept": pt.get("concept"),
                "earned_weight": weight
            })
        else:
            missing_points.append({
                "id": pt_id,
                "concept": pt.get("concept"),
                "criteria": pt.get("criteria"),
                "weight": weight
            })

    # Tính % Mastery (Làm tròn 0-100)
    mastery_score = int(round((earned_weight / total_weight) * 100)) if total_weight > 0 else 0

    # Kiểm tra các lỗi hiểu sai (Misconceptions) học viên có thể vô tình khẳng định
    misconceptions_flagged = []
    if "chỉ cần query nhân key là đủ" in norm_text or "không cần value" in norm_text:
        misconceptions_flagged.append("Khẳng định sai: Không cần dùng Value")
    if "tăng gấp 8 lần tham số" in norm_text:
        misconceptions_flagged.append("Khẳng định sai: Multi-Head làm tăng gấp nhiều lần số lượng tham số")
    if "nối thêm vào embedding" in norm_text:
        misconceptions_flagged.append("Khẳng định sai: Positional Encoding được nối (concatenate) thay vì cộng (element-wise addition)")

    status = "PASS" if mastery_score >= 80 else "NEEDS_IMPROVEMENT"

    # Gợi ý phản hồi cho Persona "Bot Ngu"
    if status == "PASS":
        bot_guidance = (
            f"Học viên đã giải thích rất đầy đủ (đạt {mastery_score}%). "
            f"Hãy gật gù khen ngợi bạn học, chốt lại 1 ý mấu chốt và đồng ý chuyển sang Checkpoint tiếp theo."
        )
    else:
        missing_names = [p["concept"] for p in missing_points]
        bot_guidance = (
            f"Học viên đạt {mastery_score}%, còn thiếu các ý: {', '.join(missing_names)}. "
            f"Hãy tiếp tục đóng vai ngơ ngác, hỏi xoáy vào 1 trong các ý còn thiếu để học viên giải thích sâu hơn."
        )

    return {
        "checkpoint_id": checkpoint_id,
        "checkpoint_title": cp.get("title"),
        "mastery_score": mastery_score,
        "status": status,
        "threshold": 80,
        "covered_points": covered_points,
        "missing_points": missing_points,
        "misconceptions_flagged": misconceptions_flagged,
        "source_citation": cp.get("source_citation", ""),
        "bot_guidance": bot_guidance
    }
