# Use an official lightweight Python image.
# Using the specific version the user has (3.13) is good practice.
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# The command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "webapp:app"]