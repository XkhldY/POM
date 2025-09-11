# Stage 1: Builder stage to install dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to create the virtualenv in the project's root
RUN poetry config virtualenvs.in-project true

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install dependencies into a virtual environment
RUN poetry install --without dev --no-root

# Copy the application source code
COPY . .

# Stage 2: Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /.venv

# Activate the virtual environment by adding it to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code from the builder stage
COPY --from=builder /app/app ./app

EXPOSE 8000

# Command to run the FastAPI application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
