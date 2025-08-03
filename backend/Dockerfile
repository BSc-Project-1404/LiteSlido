# backend/Dockerfile

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install watchdog for auto-reload
RUN pip install watchdog

# Copy project files
COPY . .

# Start Django development server with auto-reload enabled
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
