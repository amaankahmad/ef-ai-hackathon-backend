# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install protobuf==3.20

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define an environment variable
# This variable will be used by Flask
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Run app.py when the container launches
CMD ["flask", "run"]
