#Kivik Locator (aka... Ikea Product Lookup)

This app uses [Twilio SMS](http://twilio.com/) to accept Ikea article numbers. Once an article number is submitted, the app returns all relevant information (name, price, location in warehouse, URL). Once the shopper is ready to pickup the items in the warehouse, the shopper texts “Done”. The app then returns all their items with their locations. [Check it out!](http://www.kivikfinder.com)

## Usage
Ikea shoppers submit articles numbers and receive product information. 

![Example of it
working](https://raw.github.com/mauerbac/twilio-ikea-lookup/images/screenshot1.png)
![Example of it
working](https://raw.github.com/mauerbac/twilio-ikea-lookup/images/screenshot2.png)

## Installation

Step-by-step on how to deploy, configure and develop this app.

### Create Credentials

1) Create [Twilio](http://twilio.com/) account or use existing. Buy a new phone number. 

2) Create [Bitly](http://bitly.com/a/your_api_key) API key.

### Setup Heroku Account & Database

1) Create [Heroku](http://www.heroku.com/) app

2) Add [PostgreSQL](https://postgres.heroku.com/) database addon

3) Use items.sql and users.sql to create two tables

###Configuration 

1) Enter Credentials in local_settings.py
