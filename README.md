# jsrs

Japanese Speech Rating System

LICENSE: MIT

Settings
--------

Moved to
[settings](http://cookiecutter-django.readthedocs.org/en/latest/settings.html).

## Python Environment

```bash
source venv/bin/activate # or activate.fish/etc. depending on your shell
```

## Initial Setup

```bash
pip install -r requirements/local.txt
createdb -U postgres jsrs # -U <user-running-jsrs-app> would be better
# Replace as necessary:
export DATABASE_URL="postgres://<pg_user_name>:<pg_user_password>@127.0.0.1:5432/jsrs"
python manage.py migrate
python manage.py runserver
```

Visit localhost:8000 to check if everything worked.

Optionally setting up MailHog as SMTP app:

```bash
curl -O https://github.com/mailhog/MailHog/releases/download/v0.1.8/MailHog_linux_amd64
mv MailHog_linux_amd64 mailhog
chmod +x mailhog
export DJANGO_EMAIL_BACKEND=./mailhog
```

Install npm prerequisites and confirm serving with grunt works:

```bash
npm install
grunt serve
```

Visit localhost:8000 to check if everything worked.

## Loading audio file fixtures

First generate audio fixtures using provided python script. Then load the fixtures into the database.

Audio files should be accessible from `data/`.

```bash
./generate_fixtures.py
python manage.py loaddata audio-files-fixtures.json
```

Basic Commands
--------------

### Setting Up Your Users

To create a **normal user account**, just go to Sign Up and fill out the
form. Once you submit it, you'll see a "Verify Your E-mail Address"
page. Go to your console to see a simulated email verification message.
Copy the link into your browser. Now the user's email should be verified
and ready to go.

To create an **superuser account**, use this command:

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and
your superuser logged in on Firefox (or similar), so that you can see
how the site behaves for both kinds of users.

### Test coverage

To run the tests, check your test coverage, and generate an HTML
coverage report:

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS
compilation](http://cookiecutter-django.readthedocs.org/en/latest/live-reloading-and-sass-compilation.html).

It's time to write the code!!!

Running end to end integration tests
------------------------------------

N.B. The integration tests will not run on Windows.

To install the test runner:

    $ pip install hitch

To run the tests, enter the jsrs/tests directory and run the following
commands:

    $ hitch init

Then run the stub test:

    $ hitch test stub.test

This will download and compile python, postgres and redis and install
all python requirements so the first time it runs it may take a while.

Subsequent test runs will be much quicker.

The testing framework runs Django, Celery (if enabled), Postgres,
HitchSMTP (a mock SMTP server), Firefox/Selenium and Redis.

Deployment
----------

We providing tools and instructions for deploying using Docker and
Heroku.

### Heroku

[![image](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

See detailed [cookiecutter-django Heroku
documentation](http://cookiecutter-django.readthedocs.org/en/latest/deployment-on-heroku.html).

### Docker

See detailed [cookiecutter-django Docker
documentation](http://cookiecutter-django.readthedocs.org/en/latest/deployment-with-docker.html).

# Initial App Skeleton Setup

The steps below are only for the record, *do not* run them after intial project setup.

First set up a Python 3 virtual environment:

```bash
pyvenv venv # alternatively: virtualenv-3.5 venv
source venv/bin/activate # or activate.fish/etc. depending on your shell
pip install --upgrade pip
```

Use cookiecutter to generate project:

```bash
pip install --upgrade cookiecutter
cookiecutter https://github.com/pydanny/cookiecutter-django.git
```
