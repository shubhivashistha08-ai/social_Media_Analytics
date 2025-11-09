# Use official Python image
FROM python:3.10

# Create app directory
WORKDIR /code

# Copy all files
COPY ./app /code/app

# Install dependencies
RUN pip install --no-cache-dir -r /code/app/requirements.txt

# Expose API port
EXPOSE 7860

# Run the app
CMD ["uvicorn", "app.predict:app", "--host", "0.0.0.0", "--port", "7860"]

