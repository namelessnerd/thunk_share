# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /aiml_api_root

# Copy the requirements.txt first to leverage Docker cache
COPY requirements.txt /aiml_api_root/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /aiml_api_root/requirements.txt

# Copy all files from the current directory to the container, excluding those in .dockerignore
COPY . /aiml_api_root

# Expose the port that the FastAPI app will run on
EXPOSE 8000

CMD ["bash", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"]


