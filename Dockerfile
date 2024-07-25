# Base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]

#direkt docker build -t blogdocker . sonrada, docker run -d -p 5000:5000 --name dockerflask blogdocker bu kadar, javada
#mysql olduğu için docker compose çünkü aynı anda 2 koteynır çalıştırcaz.
