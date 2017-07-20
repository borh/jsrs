
# Japanese Speech Rating System

-   DOI: [![DOI](https://zenodo.org/badge/52085135.svg)](https://zenodo.org/badge/latestdoi/52085135)
-   Build status: [![CircleCI](https://circleci.com/gh/borh/jsrs/tree/master.svg?style=svg)](https://circleci.com/gh/borh/jsrs/tree/master)

Source URL: https://github.com/borh/jsrs

Hosted instances:

-   https://cuckoo.js.ila.titech.ac.jp/app/
-   https://cuckoo.js.ila.titech.ac.jp/c-jsrs/

## Summary

The Japanese Speech Rating System (JSRS) is a Python (Django) server and client application that crowdsources preference ratings of Japanese learner speech. Raters listen to two consequitive readings of the same sentence spoken by non-native and native Japanese speakers and indicate their preference between them.

The system also includes a sophisticated analysis module powered by the mdpref R package developed by [Okubo & Mayekawa (2015)](https://doi.org/10.1007/s11336-013-9392-7) available [here](http://mayekawa.in.coocan.jp/Rpackages.html).

## Dataset import

Currently, audio files and associated metadata must be imported from a spreadsheet.
Dataset import files (Django fixtures) are generated using the provided [generate_fixtures.py](generate_fixtures.py) script contained in the project's root directory.

### Audio file import

Audio files must be place under `audio` and have the following directory and naming structure:

<!--- TODO -->

WAV files will be automatically converted to MP3 format. All files will also be normalized with mp3gain.

### Metadata import

You will need to create an Excel file named `データID.xlsx` containing the following structure:

First sheet containing the set of sentences with number corresponding to the number used in the audio file name, order the priority of the sentence, and sentence text showing the original text stimulus:

| number | order | text |
| --- | --- | --- |
| 2 | 1 | こんにちは |
| 8 | 2 | 二つで一万円でした。 |
| 13 | 3 | いっしょに旅行に行きましょう。 |
| 37 | 4 | ここでは写真をとらないで下さい。 |

Second sheet containing:

| old_name | gender | name | disabled |
| --- | --- | --- | --- |
| n001 | M | p001 | 0 |
| n002 | F | p002 | 0 |
| n003 | M | p003 | 0 |
| n004 | F | p004 | 0 |

Third sheet containing:

| old_name | sentence_id | new_name |
| --- | --- | --- |
| n001 | 1 | p001 |
| n001 | 2 | p001 |
| n001 | 3 | p001 |
| n001 | 4 | p001 |

## Settings

General settings are inherited from the Cookiecutter Django template. See the [settings](http://cookiecutter-django.readthedocs.org/en/latest/settings.html) documentation there.

## Python Environment

```bash
source venv/bin/activate # or activate.fish/etc. depending on your shell
```

## Initial Setup

### Packages

```bash
pip install -r requirements/local.txt
pip install -r requirements/production.txt
pip install -r requirements/test.txt
```

Install needed R pacakges (see [README](R/README.md)):

```bash
cd R
curl -O http://mayekawa.in.coocan.jp/Rpackages/lazy.mat_0.1.3.zip
curl -O http://mayekawa.in.coocan.jp/Rpackages/lazy.tools_0.1.3.zip
curl -O http://mayekawa.in.coocan.jp/Rpackages/lazy.mdpref_0.1.2.zip
unzip -x lazy.mat_0.1.3.zip
unzip -x lazy.tools_0.1.3.zip
unzip -x lazy.mdpref_0.1.2.zip
Rscript -e "install.packages('naturalsort')"
R CMD INSTALL lazy.mat
R CMD INSTALL lazy.tools
R CMD INSTALL lazy.mdpref
Rscript -e "source(\"http://bioconductor.org/biocLite.R\"); biocLite(\"pcaMethods\")"
cd ..
```

### Database

Create the database and run schema migrations:

```bash
createdb -U postgres jsrs # -U <user-running-jsrs-app> would be better
# 'sudo -u postgres createdb -U postgres jsrs' under peer auth
# Replace as necessary:
export DATABASE_URL="postgres://<pg_user_name>:<pg_user_password>@127.0.0.1:5432/jsrs"
python manage.py migrate
```

Alternatively, if importing an existing database dump `jsrs-2017-07-19.sql` into `jsrs-dbname`:

```bash
createdb -T template0 -U postgres jsrs-dbname
psql -U postgres jsrs-dbname < jsrs-2017-07-19.sql
```

## Environment

Look at `env.example` and adjust accordingly. Then, load the environment variables into the environment before running the app.

## Testing Production

```bash
./gunicorn.sh
```

## Testing Development

NOTE: Currenly only production settings are supported.

```bash
python manage.py runserver
```

Visit localhost:8000 in your browser to check if everything worked.

Optionally setting up MailHog as SMTP app:

```bash
curl -O https://github.com/mailhog/MailHog/releases/download/v0.2.1/MailHog_linux_amd64
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

## Loading audio, sentence, and reader file fixtures

First generate audio fixtures using provided python script. Then load the fixtures into the database.

Audio files should be accessible from `media/`.

```bash
./generate_fixtures.py
python manage.py loaddata audio-sentence-fixtures.json
python manage.py loaddata audio-reader-fixtures.json
python manage.py loaddata audio-audio-fixtures.json
```

## Basic Commands

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

### Making and applying migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

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

## Running end to end integration tests

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

## Deployment

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

The steps below are only for the record, *do not* run them after initial project setup.

First set up a Python 3 virtual environment:

```bash
pyvenv venv # alternatively: virtualenv-3.6 venv
source venv/bin/activate # or activate.fish/etc. depending on your shell
pip install --upgrade pip
```

Use cookiecutter to generate project:

```bash
pip install --upgrade cookiecutter
cookiecutter https://github.com/pydanny/cookiecutter-django.git
```

# License

This project is licensed under the [MIT license](LICENSE).

<!---
# Funding

This project is partially funded by ....
-->
