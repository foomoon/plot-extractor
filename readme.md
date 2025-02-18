# Plot Extractor

This project extracts data points from plot images using OpenCV and Tesseract OCR. The application is containerized using Docker.

## Prerequisites

- Docker installed on your machine

## Building the Docker Image

1. Clone the repository and navigate to the project directory:

   ```bash
   git clone <repository-url>
   cd plot-extractor

   docker build -t plot-extractor .

   docker run --rm -it -v $(pwd):/app plot-extractor