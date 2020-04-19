# Backend of TranslateForSG

This is a simple REST API provider for any HTTP-compatible consumer. E.g. Web App, Mobile App

## Dependencies

* PostgreSQL / MySQL / MariaDB / Oracle (maybe not) / SQLite
* Google Cloud Text-to-Speech API, Translate API
* Amazon S3 compatible Storage Bucket

## Running

### Installation

```shell script
$ pip install -r requirements.txt
```

### Locally

```shell script
$ python manage.py runserver
```

### Production

```shell script
$ pip install uwsgi
$ uwsgi --socket :8080 --module translateforsg.wsgi
```

Then hookup nginx to proxy requests to `:8080`.