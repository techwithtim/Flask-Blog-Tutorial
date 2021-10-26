# Life Program

## Migration
### Installation

`pip install Flask-Migrate`

### Instantiation
Inside the __init__.py file insert the following command after both the app and db have been initalized.

`Migrate(app, db)`

### Usage
### Initial

`flask db init`

This will come up with a message saying you need to configure a file.  Unless there is a specific reason to do so, simply skip that suggestion.
### Every time you change model.py
use the following commands in order in the terminal:

`flask db migrate`

`flask db upgrade`


## Sections
---
### Health
#### *Facilities*
#### *Doctors*
#### *Medications*
#### *Medication List*
#### *Hospitalizations*
#### *Allergies*
#### *Surgeries*
#### *A1C*
#### *C-PAP*
----
### Productivity
#### *Tasks*
#### *Goals*
#### *Projects*
----
### Menu Planner
#### *Planner*
#### *Reciepts*
#### *Shopping List*
<br><br><br>

# THINGS TO DO
<ul><li>[ ] Make a page that has archive plan information.  a place you can look back at different weeks and see what you had</li>
<li>[ ] Code Snippits</li>
<li>[ ] Text the person when the medication is due to be refilled.</li>
<li>[ ] Create a wallet size report in pdf that can be printed out</li>
<li>[ ] Place the keys in the database</li>
<li>[ ] Make each menu item selectable according to user (menu on for me off for shawn for example)</li>
<li>[X] Grave markers</li>