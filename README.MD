# Mercator Shop
Mercator is a simple shop app that i made using Python Django framework.
I created it to better learn programming in python and how to use Django.
Also this is still early development version, so everything could change (for better)

## Fast start
First you should create migration
```
python manage.py makemigrations
python manage.py migrate
```

After creating our database you can create admin account 
`python manage.py createsuperuser`
When our database and admin account are created you can run server
`python manage.py runserver`

Django provides their own admin dashboard which you can enter by going to /admin/, but unfortunetly many things right now you can only add, remove, modify by django shell.
To enter django shell you can type `python manage.py shell` and import models that you want to modify 

```
# Import model we want to modify
from mainsite.models import CustomerDetails

# Get values
a = CustomerDetails.objects.get(user=4) # Number 4 you can replace with other user id
# Modify data
a.shipping_address.city = 'New York'
# Save changes
a.save()
```

## TODO:
* [ ] Admin panel
* [ ] Simple search
* [ ] Account managment
* [ ] Make better front-end template
* [ ] Order system
* [ ] Initial setup file
* [ ] Support for redirection after logging (?next=...)