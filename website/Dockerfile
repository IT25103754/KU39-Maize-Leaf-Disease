FROM python:3.12-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser model ./model
COPY --chown=appuser:appuser templates ./templates
COPY --chown=appuser:appuser static ./static
ENV MAIZE_HOST=0.0.0.0 MAIZE_PORT=7860 MAIZE_NO_BROWSER=1 PYTHONUNBUFFERED=1
USER appuser
EXPOSE 7860
CMD ["python", "app.py"]
