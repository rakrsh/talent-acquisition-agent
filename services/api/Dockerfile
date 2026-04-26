FROM python:3.12-slim

WORKDIR /app

# Install dependencies using uv
COPY pyproject.toml .
RUN pip install uv && uv pip install --system -r pyproject.toml

# Copy service code
COPY services/api/ .
# Also need the modules if they are used as modules
# But wait, I copied src/* to services/api/ so modules/ is already there.

ENV PYTHONPATH=/app
ENV HTTP_PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]
