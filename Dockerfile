# Use official Python image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 
    # GDAL_LIBRARY_PATH=/usr/lib/libgdal.so \
    # GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so \
    # PROJ_LIB=/usr/share/proj

# Set working directory
WORKDIR /app
COPY pyproject.toml /app     

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libdbus-1-3\
    libatk1.0-0\
    libatk-bridge2.0-0\ 
    libcups2\           
    libxkbcommon0\      
    libatspi2.0-0\      
    libxcomposite1\     
    libxdamage1\        
    libxfixes3\         
    libxrandr2\         
    libgbm1\            
    libasound2\
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="/app"
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev -q
RUN playwright install chromium
#RUN playwright install-deps
# Copy project files
COPY . .
RUN python manage.py collectstatic --noinput
# Expose port
EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh
# RUN if [ -f .env ]; then cp .env .env.example; fi

RUN chmod +x /entrypoint.sh

# Run migrations and start the server
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "django_app.wsgi:application"]
# ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]