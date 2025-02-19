# Use the official Python 3.10 slim image
FROM python:3.10.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN apt-get update && apt-get install -y \
    # build-essential \
    # cmake \
    # libgtk-3-dev \
    libgl1-mesa-glx \
    # libglib2.0-0 \
    # libavcodec-dev \
    # libavformat-dev \
    # libswscale-dev \
    # libv4l-dev \
    # libxvidcore-dev \
    # libx264-dev \
    # libjpeg-dev \
    # libpng-dev \
    # libtiff-dev \
    # gfortran \
    # openexr \
    # libatlas-base-dev \
    # libtbb2 \
    # libtbb-dev \
    # libdc1394-22-dev \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copy the src folder into the container
COPY src/ /app/src/

EXPOSE 5001

# Set the entry point for the container
CMD ["python", "src/extractor-app.py"]
# CMD ["bash"]