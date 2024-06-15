FROM python:3.11-slim
WORKDIR /service
COPY requirements-2024.txt .
RUN pip install --no-cache-dir -r requirements-2024.txt
COPY app ./app
RUN useradd -r -u 10001 apiuser && mkdir -p /data && chown -R apiuser:apiuser /service /data
USER apiuser
ENV DATABASE_URL=sqlite:////data/app.db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
