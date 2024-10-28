# SEP
This project uses the `uv` python version manager.

## Installation
Make sureto have `uv` installed locally ([website](https://docs.astral.sh/uv/))

```bash
uv run manage.py migrate  # Create the database schema (by default sqlite)
uv run manage.py createsuperuser --username $USER  # Create a superuser to naviguate the site, the user is a CS employee by default
uv run manage.py runserver  # Runs the server locally
```

and then naviguate to [http://127.0.0.1:8000](http://127.0.0.1:8000)


# Currently implemented

# Request making
On the home page, there is a form for a client to fill, that form will allow them to create a request, that will be reviewed by the
Customer Service team employees.

# Request Formatting
A customer service employee can use the `Employee site` link on the top right of the page to go to their dashboard.
There they will see requests waiting for formatting, the projects they have initiated and their current status (why not, allows to watch progress)
and finally an overview of their profile (might be split into separate template for re-use).

Once the employee clicks on the `review` button from the requests table. they are redirected to the project creation homepage, which displays
side by side the request and the form to create a project. The employee can either save a draft of the project for later updates or directly
`publish` it, meaning the project will be ready for the approval (or disapproval) of the CS manager.


# Misc stuff
[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) contains an admin panel for easily changing the models
