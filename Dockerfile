# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY images/* /app/images/ 

COPY streamlit_app.py /app

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=80", "--server.address=0.0.0.0"]