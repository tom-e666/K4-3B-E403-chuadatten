from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path, *, override: bool = True) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and (override or key not in os.environ):
            os.environ[key] = value


def _setup_extra_ca_bundle() -> None:
    """Một số máy có phần mềm diệt virus / proxy công ty tự chặn và ký lại HTTPS
    (SSL inspection) bằng chứng chỉ gốc riêng — Python (certifi) không tin chứng chỉ
    đó nên mọi request tới API (Gemini/OpenAI...) sẽ lỗi CERTIFICATE_VERIFY_FAILED.

    Nếu gặp lỗi này, set EXTRA_CA_BUNDLE trong .env CÁ NHÂN của bạn (không commit)
    trỏ tới file .pem chứng chỉ gốc đó (ví dụ với Avast: EXTRA_CA_BUNDLE="C:\\ProgramData\\Avast Software\\Avast\\wscert.pem").
    Hàm này gộp chứng chỉ đó với bộ CA public chuẩn (certifi) rồi trỏ SSL_CERT_FILE/
    REQUESTS_CA_BUNDLE vào bản gộp, để vừa tin được API thật vừa tin được proxy nội bộ.
    """
    extra_ca = os.getenv("EXTRA_CA_BUNDLE")
    if not extra_ca or not Path(extra_ca).expanduser().exists():
        return
    try:
        import certifi
    except ImportError:
        return

    merged_path = Path(os.getenv("TEMP", ".")) / "feynman_ai_merged_ca_bundle.pem"
    try:
        base_bundle = Path(certifi.where()).read_bytes()
        extra_bundle = Path(extra_ca).expanduser().read_bytes()
        merged_path.write_bytes(base_bundle + b"\n" + extra_bundle)
    except OSError:
        return

    merged_str = str(merged_path)
    os.environ["SSL_CERT_FILE"] = merged_str
    os.environ["REQUESTS_CA_BUNDLE"] = merged_str


def load_lab_env(root: Path) -> None:
    external_path = os.getenv("DAY04_ENV_FILE")
    if external_path:
        load_dotenv(Path(external_path).expanduser())
    else:
        load_dotenv(root / ".env")
    _setup_extra_ca_bundle()
