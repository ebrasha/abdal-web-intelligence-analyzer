# -------------------------------------------------------------
# Programmer       : Ebrahim Shafiei (EbraSha)
# Email            : Prof.Shafiei@Gmail.com
# -------------------------------------------------------------

# Use an official Python base image
FROM python:3.11-slim

# Set work directory inside container
WORKDIR /app

# Copy all project files to the container
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default port (if the app uses Flask or similar)
EXPOSE 8000

# Run the main script
CMD ["python", "abdal-web-intelligence-analyzer.py"]

