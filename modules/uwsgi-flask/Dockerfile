FROM python:3.7-alpine
WORKDIR /var/www
ENV FLASK_APP app/app.py
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY ./modules/uwsgi-flask/uwsgi.ini uwsgi.ini
COPY ./modules/uwsgi-flask/wsgi.py wsgi.py
COPY ./modules/uwsgi-flask/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./modules/uwsgi-flask/app app
CMD ["uwsgi", "--ini", "uwsgi.ini"]