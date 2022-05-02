FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
        libmagic-dev \
        gcc \
        g++ \
        p7zip-full

# Change working directory
WORKDIR /opt/dino
ENV DAGSTER_HOME=/opt/dino

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy source code
COPY ./docker/dagster/dev/dagster.yaml .
COPY ./docker/dagster/dev/celery_config.yaml .
COPY ./docker/dagster/dev/workspace.yaml .
COPY  ./dino ./dino
COPY  ./external_tools ./external_tools


CMD ["dagit", "-w", "workspace.yaml", "-h", "0.0.0.0", "-p", "3000"]