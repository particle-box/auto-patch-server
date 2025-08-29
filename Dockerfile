FROM ubuntu:22.04

# 1. Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip openjdk-17-jre-headless && \
    apt-get clean

# 2. Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# 3. Copy code, including lspatch.jar
COPY . .

# 4. Expose port and start
ENV PORT=10000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
