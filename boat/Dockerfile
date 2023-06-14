FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY boat.py .
COPY in_denm.json .
COPY in_cam.json .

ENV MAP_PRCSN="10"
ENV ZONE="[(37.87400, -25.78800), (37.87400, -25.77800), (37.8640, -25.77800), (37.86400, -25.78800)]"
    

CMD ["python3", "-u", "boat.py"]

