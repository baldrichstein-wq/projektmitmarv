FROM python:3.11-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libsqlite3-dev git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt /workspace/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /workspace/requirements.txt

RUN curl -fsSL "https://github.com/nektos/act/releases/download/v0.2.33/act_Linux_x86_64.tar.gz" | tar -xz -C /usr/local/bin act; \
    chmod +x /usr/local/bin/act

COPY . /workspace

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]


