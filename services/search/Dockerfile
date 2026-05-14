# Build argument for version
ARG VERSION=dev

FROM python:3.12-slim

WORKDIR /app

# Set version label
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.title="Talent Acquisition Agent - Search Service"

# Install uv for dependency management
RUN pip install uv

# Copy project configuration
COPY pyproject.toml .
RUN uv pip install --system .

# Copy service code (which includes modules/ since we copied them)
COPY services/search/ .

ENV PYTHONPATH=/app
ENV SEARCH_SERVICE_PORT=8081
ENV VERSION=${VERSION}

EXPOSE 8081

CMD ["python", "app.py"]
