# ==============================
# Stage 1: Build dependencies
# ==============================

# Start with a small Python 3.14 image.
# "slim" means it contains only the basic things needed.
# "AS builder" gives this stage the name "builder".
FROM python:3.14-slim AS builder

# Create/use /app as the working folder inside the container.
WORKDIR /app

# Copy requirements.txt from our computer into /app.
# We need this file so pip knows which packages to install.
COPY requirements.txt .

# Install all Python dependencies from requirements.txt.
# --no-cache-dir → don't keep pip's download cache (saves space).
# --prefix=/install → put the installed packages in /install.
# These packages will be copied into the final image later.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ==============================
# Stage 2: Runtime image
# ==============================

# Start a fresh, clean Python image.
# This becomes our actual final image.
FROM python:3.14-slim

# Our application will run from /app.
WORKDIR /app

# Copy ONLY the installed dependencies from Stage 1.
# We don't copy the entire builder stage.
# This helps keep the final image smaller.
COPY --from=builder /install /usr/local

# Copy our actual project files into /app.
# For example: main.py, routes.py, database.py, etc.
COPY . .

# Command that runs when the container starts.
# Start Uvicorn and run the "app" object from main.py.
# --host 0.0.0.0 → allow connections from outside the container.
# --port 3000 → FastAPI listens on port 3000.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]