import json
import uuid
from pathlib import Path


class Store:
    def __init__(self, data_dir: Path):
        self.path = Path(data_dir) / "requests.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

    def _read(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, rows: list[dict]) -> None:
        self.path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    def find_by_key(self, idempotency_key: str) -> dict | None:
        if not idempotency_key:
            return None
        for row in self._read():
            if row.get("idempotency_key") == idempotency_key:
                return row
        return None

    def get(self, request_id: str) -> dict | None:
        for row in self._read():
            if row["id"] == request_id:
                return row
        return None

    def list(self) -> list[dict]:
        return self._read()

    def add(self, row: dict) -> dict:
        stored = {"id": f"svc-{uuid.uuid4().hex[:12]}", **row}
        rows = self._read()
        rows.append(stored)
        self._write(rows)
        return stored
