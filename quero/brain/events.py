from __future__ import annotations

from datetime import datetime
from pathlib import Path


def next_event_id(counter_path: Path, prefix: str = "q") -> str:
    counter_path.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    current_day = ""
    current_count = 0

    if counter_path.exists():
        raw = counter_path.read_text(encoding="utf-8", errors="replace").strip()
        if raw:
            parts = raw.split(",", 1)
            if len(parts) == 2:
                current_day, count_text = parts
                try:
                    current_count = int(count_text)
                except ValueError:
                    current_count = 0

    if current_day != today:
        current_count = 0

    current_count += 1
    counter_path.write_text(f"{today},{current_count}", encoding="utf-8")
    return f"{prefix}-{today}-{current_count:04}"
