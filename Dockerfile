FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# GEAENDERT 06.08.2026 (Stefan): "COPY *.db ." entfernt. Projekt nutzt nur noch PostgreSQL
# (Benutzer) und MongoDB (Essen/Wein) als externe Datenbanken, die alten SQLite-Dateien
# wurden aus dem Repo geloescht und werden im Image nicht mehr gebraucht.
COPY *.py .

# NEU 06.08.2026 (Stefan): Container laeuft nicht mehr als root, sondern als eigener User
# (appuser) -- reduziert den Schaden bei einer eventuellen Code-Ausfuehrungs-Schwachstelle.
RUN useradd --create-home appuser
USER appuser

# Expose backend port
EXPOSE 5005

ENV PORT=5005
# GEAENDERT 07.08.2026 (Stefan): Worker-Anzahl war vorher fest auf 4 im CMD verdrahtet -- das
# ist fuer eine kleine AWS-Sandbox-Instanz (z.B. t3.micro mit 1 GiB RAM) zu viel und kann zu
# Out-of-Memory fuehren. Default jetzt 2, ueber WEB_CONCURRENCY (.env/docker-compose.yml) ohne
# Image-Neubau anpassbar -- auf einer leistungsfaehigeren NAS kann der Wert erhoeht werden.
ENV WEB_CONCURRENCY=2

# GEAENDERT 06.08.2026 (Stefan): Vorher "python main.py" (Flasks eingebauter Dev-Server:
# single-threaded, nicht fuer echten Produktionsbetrieb gedacht). requirements.txt enthielt
# zwar schon gunicorn, wurde hier aber nie tatsaechlich benutzt. Jetzt startet Gunicorn mit
# konfigurierbarer Worker-Anzahl -- geeignet fuer den Produktivbetrieb auf AWS/NAS.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5005 --workers ${WEB_CONCURRENCY:-2} main:app"]
