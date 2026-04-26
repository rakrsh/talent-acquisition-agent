FROM python:3.12-slim

WORKDIR /app

# Install uv for dependency management
RUN pip install uv

# Copy project configuration
COPY pyproject.toml .
RUN uv pip install --system .

# Copy service code (which includes modules/ since we copied them)
COPY services/search/ .

ENV PYTHONPATH=/app
ENV SEARCH_SERVICE_PORT=8081

EXPOSE 8081

CMD ["python", "app.py"]
