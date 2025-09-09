FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set the working directory to your Django project
WORKDIR /app/the_mooli_project

EXPOSE 8000

# Run server from the correct directory
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]