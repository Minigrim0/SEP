# SEP
This project uses the `uv` python version manager.

## Installation
Make sure to have `uv` installed locally ([website](https://docs.astral.sh/uv/))

```bash
uv run manage.py migrate  # Create the database schema (by default sqlite)
uv run manage.py createsuperuser --username $USER  # Create a superuser to naviguate the site, the user is a CS employee by default
uv run manage.py runserver  # Runs the server locally
```

and then naviguate to [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Without `uv`
```bash
python -m venv ve  # Create a virtual environment
source ve/bin/activate  # Activate the virtual environment
pip install django django-extensions # Install the required packages
python manage.py migrate  # Create the database schema (by default sqlite)
python manage.py createsuperuser --username $USER  # Create a superuser to naviguate the site, the user is a CS employee by default
python manage.py runserver  # Runs the server locally
```

and then naviguate to [http://127.0.0.1:8000](http://127.0.0.1:8000) to see the website


## Unit testing
To run the tests, simply run the following command:
```bash
uv run manage.py test
```

or in a python virtual environment:
```bash
python manage.py test
```

The source code for the tests is located in the `tests.py` files in the `project` & `SEP` directories.
