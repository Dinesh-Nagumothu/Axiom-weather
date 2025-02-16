# Use the official Python image as base
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install Flask and other dependencies
RUN pip install Flask pymongo pyjwt

# Copy the Flask application code into the container
COPY . .

# Expose port 5000 to allow communication to/from server
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]