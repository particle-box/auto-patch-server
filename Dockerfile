FROM ubuntu:22.04

# 1) System deps: Python + Java for lspatch
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip openjdk-17-jre-headless && \
    apt-get clean

# 2) App deps
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# 3) App code (must include app.py and lspatch.jar)
COPY . .

# Render provides PORT; fall back to 10000 locally
ENV PORT=10000

# 4) Start (shell form so $PORT expands)
CMD ["sh","-lc","gunicorn app:app --bind 0.0.0.0:${PORT}"]
