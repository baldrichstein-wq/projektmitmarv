FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files and pre-existing databases
COPY *.py .
COPY *.db .

# Expose backend port
EXPOSE 5005

ENV PORT=5005

CMD ["python", "main.py"]
