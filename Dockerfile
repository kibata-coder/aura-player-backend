FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget unzip supervisor curl libicu-dev && rm -rf /var/lib/apt/lists/*

ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1

WORKDIR /app
RUN mkdir -p /app/downloads /app/slskd_data /var/log/supervisor

RUN wget https://github.com/slskd/slskd/releases/download/0.25.1/slskd-0.25.1-linux-x64.zip -O slskd.zip && \
    unzip slskd.zip -d /app/slskd && \
    chmod +x /app/slskd/slskd && \
    rm slskd.zip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

# Setup Supervisor with STDOUT logging so Render can see the logs
RUN echo "[supervisord]\n\
nodaemon=true\n\n\
[program:slskd]\n\
command=/app/slskd/slskd --app-dir /app/slskd_data\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\n\
[program:python_worker]\n\
command=python /app/worker.py\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0" > /etc/supervisor/conf.d/supervisord.conf

# Expose 8000 for Python API, 5030 & 50300 for slskd
EXPOSE 8000 5030 50300

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
