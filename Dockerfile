# pull official base image
FROM python:3.8-buster

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
ENV SECRET_KEY my-secret-key
ENV AWS_ACCESS_KEY_ID_WM AKIA6IQSWMH33M4B57NC 
ENV AWS_SECRET_ACCESS_KEY_WM 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 

RUN apt-get update

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# collect static files
RUN python manage.py collectstatic --noinput

# add and run as non-root user
RUN adduser --disabled-password myuser
USER myuser

# run gunicorn
CMD gunicorn negocify.wsgi:application --bind 0.0.0.0:$PORT