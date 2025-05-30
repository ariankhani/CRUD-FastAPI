# Use a lightweight Python image
FROM python:3.12-slim

# Install system dependencies (e.g. libmagic for python-magic)
RUN apt-get update && apt-get install -y libmagic1 && rm -rf /var/lib/apt/lists/*

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Create a static folder (if you need to serve static files)
RUN mkdir -p static

# Copy the rest of your application code
COPY . /app

# Expose the port on which your app will run
EXPOSE 8000

# Run the application using uvicorn.
# Adjust the module path according to your project structure.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
