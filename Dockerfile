FROM python:3.12-slim

# Install libmagic (if needed)
RUN apt-get update && apt-get install -y libmagic1 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

# Set the working directory
WORKDIR /app


# Copy the rest of the application code
COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
