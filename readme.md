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

   docker run --rm -it -p 5001:5001 plot-extractor

## Installed Python Packages (as of 2/18/25)
| Package          | Version         |
|------------------|-----------------|
| blinker          | 1.9.0           |
| click            | 8.1.8           |
| contourpy        | 1.3.1           |
| cycler           | 0.12.1          |
| exceptiongroup   | 1.2.2           |
| Flask            | 3.1.0           |
| fonttools        | 4.56.0          |
| iniconfig        | 2.0.0           |
| itsdangerous     | 2.2.0           |
| Jinja2           | 3.1.5           |
| kiwisolver       | 1.4.8           |
| MarkupSafe       | 3.0.2           |
| matplotlib       | 3.10.0          |
| numpy            | 2.2.3           |
| opencv-python    | 4.11.0.86       |
| packaging        | 24.2            |
| pillow           | 11.1.0          |
| pip              | 23.0.1          |
| pluggy           | 1.5.0           |
| pyparsing        | 3.2.1           |
| pytesseract      | 0.3.13          |
| pytest           | 8.3.4           |
| python-dateutil  | 2.9.0.post0     |
| setuptools       | 65.5.1          |
| six              | 1.17.0          |
| tomli            | 2.2.1           |
| Werkzeug         | 3.1.3           |
| wheel            | 0.45.1          |