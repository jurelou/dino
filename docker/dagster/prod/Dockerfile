FROM python:3.10-buster

RUN apt-get update && apt-get install -y libmagic-dev

# Change working directory
WORKDIR /opt/dino
ENV DAGSTER_HOME=/opt/dino

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy configuration files
COPY ./docker/dagster/prod/dagster.yaml .
COPY ./docker/dagster/prod/workspace.yaml .

# Copy source code
COPY  ./dino ./dino

# Run dagster gRPC server on port 4000
EXPOSE 4000

CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-f", "dino/repositories.py"]