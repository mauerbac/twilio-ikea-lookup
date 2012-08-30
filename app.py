import os 
from flask import Flask, request, redirect
from urllib import urlopen
from twilio import twiml
import re
import mechanize
from bs4 import BeautifulSoup
import bitlyapi
import database
import sys
from twilio.rest import TwilioRestClient
import unicodedata
import local_settings


app = Flask(__name__)

def getProdName(soup):
  prodName=soup.find("div", {"class": "sc_com_header sc_graph_product_text"}).text
  prodName=unicodedata.normalize('NFKD', prodName).encode('ascii','ignore')
  prodName=prodName[:-20]
  return prodName

#handles multiple than one location
def doubleloc(user_id,locsize,loc,soup):
    i=0  #counter
    response=""  #response for txt message
    dbresponse="" #response for database
    locsize=(locsize/2)  #number of locations 
    while (i<locsize):   #loop through all locations. pull info and create responses
      aisle=loc[i].text  
      bin1=loc[i+1].text
      response=response + "\n %s) Aisle: " %(i+1) + aisle + " Bin: " + bin1
      dbresponse=dbresponse+ "  %s) Aisle: " %(i+1) + aisle + " Bin: " + bin1
      i+=1
    price=soup.find(id="price1").text.strip()  #pull price
    prodName=getProdName(soup) 
    url=soup.find(id="pipUrl").get('href')
    url="http://www.ikea.com"+ url
    newurl=makeBit(url)   #create new URL
    database.enterItem(user_id,prodName,dbresponse,price,newurl) #add item to the database
    return prodName + "\nLocations: " + response + "\nPrice: " + price + "\nMore Info: " + newurl

#scrape Ikea site for info -handles the normal case 
def pullInfo(html,br,user_id,number):
  soup=BeautifulSoup(html)
  loc=soup.findAll("div", {"class": "sc_com_locationNo sc_find_it_location_number"}) #find location
  locsize=len(loc) 
  if(locsize==0):  #check for problems
    findproblems(html,soup,br,user_id,number) 
  if(locsize>2): #check for multiple locations
    response=doubleloc(user_id,locsize,loc,soup) 
    return sendOut(response,number)
  aisle=loc[0].text  #pull aisle number
  bin1=loc[1].text   #pull location number
  price=soup.find(id="price1").text.strip() #pull price
  prodName=getProdName(soup)
  url=soup.find(id="pipUrl").get('href')
  url="http://www.ikea.com"+ url
  newurl=makeBit(url)
  location="Aisle: " + aisle +" Bin: " +bin1 
  database.enterItem(user_id,prodName,location,price,newurl) #enter in database
  return prodName + "\nLocation: " + "Aisle: " + aisle + "  Bin: " + bin1 + "\nPrice: " + price + "\nMore Info: " + newurl

#send text to user
def sendOut(result,number):
  numchars=len(result)
  #check if message is larger than 160 chars
  if(numchars>160):
    mess1="Message 1/2 \n" + result[0:(numchars/2)]  #split into two messages
    mess2="Message 2/2 \n"+ result[(numchars/2):] 
    sendOutF(mess1,number) #send sms messages
    sendOutF(mess2,number)
    return sys.exit(0)
  else:  
    sendOutF(result,number) #send out sms
    return sys.exit(0)

def sendOutF(message,number):
  account_sid = local_settings.ACCOUNT_SID 
  auth_token = local_settings.AUTH_TOKEN    
  client = TwilioRestClient(account_sid, auth_token)
  message = client.sms.messages.create(to=number, from_=local_settings.TWILIO_FROM_NUMBER, body=message) #enter your FROM Twilio number


#create Bitly Url
def makeBit(url):
  b = bitlyapi.BitLy("mauerbac", local_settings.BITLY_API_KEY) #Add bitly API key
  res = b.shorten(longUrl=url)
  return res['url']

#handles items not in warehouse 
def noavailableF(html,user_id):
  soup=BeautifulSoup(html)
  price=soup.find(id="price1").text.strip()
  prodName=getProdName(soup)
  url=soup.find(id="pipUrl").get('href')
  url=u"http://www.ikea.com"+ url
  newurl=makeBit(url)
  location="Contact staff for purchase and information" 
  database.enterItem(user_id,prodName,location,price,newurl) #add item to DB
  return prodName + "\nLocation: Contact staff for purchase and information" + "\nPrice: " + price + "\nMore Info: " + newurl

#after problem is detected, find the problem 
def findproblems(html,soup,br,user_id,number):
  soup=BeautifulSoup(html, "lxml")
  #searches for No location text
  noavailable=soup.findAll("div", {"class": "sc_com_noLocationText sc_find_it_location_text"})
  noavailablesize=len(noavailable)
  noresults=soup.findAll("h2", {"class": "headerLeftNavi"}) #searches for "search results" -meaning invaild entry
  nosize=len(noresults)
  outofstock=soup.findAll("div", {"class": "sc_com_stockInfo sc_graph_stockInfo_container"}) #searches for out of stock text
  outofstocksize=len(outofstock)
  if(outofstocksize==1): #if item is out of stock
    outofstock1=soup.find("div", {"class": "sc_com_stockInfo sc_graph_stockInfo_container"}).text
    instock=outofstock1.rfind("This product is out of stock at your selected store.") #make sure out of stock
    if(instock>0):
      return sendOut("This item is currently out of stock",number) 
  if(nosize==1): #some type of error-- let's find it
    noresults=noresults[0].text
  if(noavailablesize==1):
    noavailable=noavailable[0].text
      #if no info is available
    if(noavailable=="Contact staff for purchase and information"): #make sure no location 
      response= noavailableF(html,user_id) #although no location, find other info
      return sendOut(response,number) 
  elif (noresults=="Search Results"): #make sure invaild entry
    return sendOut("Invaild entry. Please send item numbers only",number)
  #some item numbers have "confirm screens" -select the form with store number   
  br.select_form(name="stocksearch")  
  br.form['ikeaStoreNumber1']= [local_settings.STORE_NUMBER]  
  br.submit()
  html=br.response().read()
  response= pullInfo(html,br,user_id,number)
  return sendOut(response,number)  

@app.route("/", methods=['POST'])
def main():
    number=request.form['From']  #stores From number 
    userid=database.checkNum(number) #checks for returning users
    message= request.form['Body'] #stores response from Twilio
    print "message" + message
    #handles if shopper is done
    if(message=="Done" or message=="done"):
      return database.returnAll(userid,number)
    else:
      #store item number 
      itemnum=message
      br=mechanize.Browser()
      br.open("http://www.ikea.com/us/en/catalog/stockcheck/") #open catalog
      br.select_form(name="stocksearch")   #select form
      br.form['query']= itemnum     #pass item number 
      br.form['ikeaStoreNumber1']= [local_settings.STORE_NUMBER]  
      br.submit()  #submit form
      html=br.response().read()
      soup=BeautifulSoup(html, "lxml")  #create soup object from page response
      loc=soup.findAll("div", {"class": "sc_com_locationNo sc_find_it_location_number"}) #try to find loc & bin
      locsize=len(loc)
      #is location available
      if(locsize==0):
          return findproblems(html,soup,br,userid,number)
      response= pullInfo(html,br,userid,number)
      return sendOut(response,number)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
