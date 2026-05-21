FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget unzip supervisor curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p /app/downloads /app/slskd_data /var/log/supervisor

# Extract slskd
RUN wget https://github.com/slskd/slskd/releases/download/0.25.1/slskd-0.25.1-linux-x64.zip -O slskd.zip && \
    unzip slskd.zip -d /app/slskd && \
    chmod +x /app/slskd/slskd && \
    rm slskd.zip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

# Setup Supervisor to run slskd and python worker simultaneously
RUN echo "[supervisord]\nnodaemon=true\n\n[program:slskd]\ncommand=/app/slskd/slskd --app-dir /app/slskd_data\nautostart=true\nautorestart=true\n\n[program:python_worker]\ncommand=python /app/worker.py\nautostart=true\nautorestart=true" > /etc/supervisor/conf.d/supervisord.conf

EXPOSE 5030 50300

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
