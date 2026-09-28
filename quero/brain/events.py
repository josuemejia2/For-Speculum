from __future__ import annotations

import contextlib
from datetime import datetime
from pathlib import Path


@contextlib.contextmanager
def _exclusive_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as lock_file:
        try:
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            yield
        except ImportError:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            try:
                import msvcrt

                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            except ImportError:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def next_event_id(counter_path: Path, prefix: str = "q") -> str:
    counter_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = counter_path.with_suffix(counter_path.suffix + ".lock")

    with _exclusive_lock(lock_path):
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
