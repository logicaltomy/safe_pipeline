FROM python:3.12-slim

WORKDIR /opt/app

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV PATH="/opt/venv/bin:${PATH}"

EXPOSE 5000

CMD ["python", "app.py"]
