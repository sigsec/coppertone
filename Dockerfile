FROM python:3.9-slim

WORKDIR /app
EXPOSE 8080

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY coppertone/ ./coppertone/

ENTRYPOINT [ "/usr/bin/env", "python3", "main.py" ]
