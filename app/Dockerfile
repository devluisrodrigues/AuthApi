FROM python:3.9-slim

# Set the working directory to the root directory
WORKDIR /

# Copy the dependencies file to the working directory
COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

# Copy the app directory into the container
COPY . /

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]