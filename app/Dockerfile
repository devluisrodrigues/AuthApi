FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory into the container
COPY . .

# CMD ["fastapi", "run", "app.py"]
# veja oq esta dentro da pasta app

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]
