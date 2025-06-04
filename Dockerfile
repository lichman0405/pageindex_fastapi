FROM python:3.12-slim

# Setting environment variables to ensure Python output is sent straight to terminal (e.g., for logging)
ENV PYTHONUNBUFFERED 1                     
ENV PYTHONDONTWRITEBYTECODE 1              
ENV APP_MODULE "api_main:app"             

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"]