# Ausgangspunkt für das Hetzner-Deployment — noch nicht production-hardened
# (kein Multi-Stage-Build, kein non-root User, keine Healthchecks).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0"]
