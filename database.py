import psycopg2
from sqlalchemy import *
import ikea2
from twilio.rest import TwilioRestClient
import sys
import local_settings

#connect to database 
db = create_engine(local_settings.DB_INFO)
metadata=MetaData(db)

    
    #send text to user
def sendNewTxt(currentnum,message):
    numchars=len(message)
    #greater than 160 chars?
    if(numchars>160):
        mess1="Message 1/2 \n" + message[0:(numchars/2)]
	mess2="Message 2/2 \n"+ message[(numchars/2):] 
	sendNewTxt(currentnum,mess1)
	sendNewTxt(currentnum,mess2)
    else:
        account_sid = local_settings.ACCOUNT_SID
	auth_token = local_settings.AUTH_TOKEN
	client = TwilioRestClient(account_sid, auth_token)
	message = client.sms.messages.create(to=currentnum, from_="+12014264579",body=message)

    #enter item in database
def enterItem(user_id,product,loc,price,url):
	product=product.strip() #strip of white space
	loc=loc.strip() #strip loc of white space
	items=Table('items',metadata, autoload=True)
	ins=items.insert()
	item=ins.values(user_id=user_id,product=product,loc=loc,price=price,url=url)
	db.execute(item)
	
    #add new user
def newUser(currentnum):
        #send welcome text
	newUserTxt= "Welcome! Store: Paramus, NJ. Text article numbers as you shop to store them in your cart. \nWhen you are done shopping text 'done' and you will receive all your items."
	sendNewTxt(currentnum,newUserTxt)
	users= Table('users',metadata, autoload=True)
	ins= users.insert()
	new_user=ins.values(numbers=currentnum)
	db.execute(new_user)

        #get user_id
	s=users.select(users.c.numbers==currentnum)
	rs=s.execute()
	row=rs.fetchone()
	user_id= row['userid']
	return user_id

    #return all items
def returnAll(user_id,number):
	items= Table('items',metadata, autoload=True)
	s=items.select(items.c.user_id==user_id)
	rs=s.execute()
	count=1 #start counter
	#traverse all items
	for row in rs:
		prodName=row['product'] #get product name
		loc=row['loc']  #get location
		price=row['price']  #get price
		url=row['url']   #get URL
		message="Item: " + str(count) +"\n" +prodName + "\nLocation: " +loc #create message
		sendNewTxt(number,message)
		count=count + 1
	return sys.exit(0)

    #check if new user
def checkNum(currentnum):
	print currentnum
	users= Table('users',metadata, autoload=True)
	try:
		s=users.select(users.c.numbers==currentnum)
		rs=s.execute()
		row=rs.fetchone()
		user_id= row['userid']
		return user_id   #existing user. return user_id
	except:
		#new user - add to DB
		return newUser(currentnum)

