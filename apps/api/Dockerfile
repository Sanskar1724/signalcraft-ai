FROM python:3.12-slim
WORKDIR /srv/signalcraft
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY apps/api ./apps/api
ENV SIGNALCRAFT_DB_PATH=/data/signalcraft.db
VOLUME ["/data"]
EXPOSE 8000
CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/srv/signalcraft"]
