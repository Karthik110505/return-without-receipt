# Use a compatible base image with dlib and face_recognition preinstalled
FROM python:3.10-slim

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the app code
COPY . /app
WORKDIR /app

# Expose the port
EXPOSE 10000

# Run the app
CMD ["python", "server.py"]
