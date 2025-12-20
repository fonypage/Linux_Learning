# ---------- builder ----------
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml /build/pyproject.toml

RUN python - <<'PY' > requirements.txt
import tomllib, pathlib
data = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
deps = data["project"]["dependencies"]
test_deps = data["project"].get("optional-dependencies", {}).get("test", [])
print("\n".join(deps + test_deps))
PY

RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir -r requirements.txt -w /wheels


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
 && rm -rf /wheels

COPY src /app/src
COPY tests /app/tests

RUN useradd -m appuser
USER appuser

ENV PORT=8002

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
ENV PYTHONPATH=/app