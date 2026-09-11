# Ausgangspunkt für das Hetzner-Deployment — noch nicht production-hardened
# (kein Multi-Stage-Build, kein non-root User, keine Healthchecks).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8511

# --host=0.0.0.0: Ohne Angabe lauscht die App auf 127.0.0.1 und ist aus dem
# Container heraus nicht erreichbar. tests/test_packaging.py haelt das fest.
CMD ["python", "-m", "dashboard.web.app", "--host=0.0.0.0", "--port=8511"]
