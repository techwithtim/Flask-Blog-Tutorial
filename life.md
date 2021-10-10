# Ticketing

## Customer

## Venue

### TicketGrid
### Location

## Migration
### Installation
~~~
pip install Flask-Migrate
~~~
### Instantiation
Inside the __init__.py file insert the following command after both the app and db have been initalized.
~~~
Migrate(app, db)
~~~
### Usage
### Initial
~~~
flask db init
~~~
This will come up with a message saying you need to configure a file.  Unless there is a specific reason to do so, simply skip that suggestion.
### Every time you change model.py
use the following commands in order in the terminal:
~~~
flask db migrate
~~~
~~~
flask db upgrade
~~~
## Event

### Ticket


