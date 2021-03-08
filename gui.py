import nicehash
import time
import urllib, json
import requests
import tkinter as tk
import threading
from tkinter import *
from PIL import Image, ImageTk
from PIL import ImageOps
from PIL import ImageFont
from PIL import ImageDraw
import currency
import yaml
import os
import currency
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import decimal
configfile = "config.yaml"
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')

root=tk.Tk()

frame=tk.Frame(root,width=480,height=320)

frame.configure(bg="white")
frame.pack()
frame2=tk.Frame(root,width=100,height=100)
frame3=tk.Frame(root,width=100,height=100)
frame4=tk.Frame(root,width=100,height=100)
frame5=tk.Frame(root,width=100,height=100)
frame6=tk.Frame(root,width=100,height=100)
frame2.configure(bg="white")
frame3.configure(bg="white")
frame4.configure(bg="white")
frame5.configure(bg="white")
frame6.configure(bg="white")
def currencystringtolist(currstring):
    # Takes the string for currencies in the config.yaml file and turns it into a list
    curr_list = currstring.split(",")
    curr_list = [x.strip(' ') for x in curr_list]
    return curr_list
def currencycycle(curr_list):
    # Rotate the array of currencies from config.... [a b c] becomes [b c a]
    curr_list = curr_list[1:]+curr_list[:1]
    return curr_list
def getData(config,whichcoin, fiat, other):
    geckourl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency="+fiat+"&ids="+whichcoin
    rawlivecoin = requests.get(geckourl).json()  
    liveprice = rawlivecoin[0]
    pricenow= float(liveprice['current_price'])
    alltimehigh = float(liveprice['ath'])
    other['volume'] = float(liveprice['total_volume'])
    print('Getting Data')
    days_ago=int(config['ticker']['sparklinedays'])   
    endtime = int(time.time())
    starttime = endtime - 60*60*24*days_ago
    starttimeseconds = starttime
    endtimeseconds = endtime  
    geckourlhistorical = "https://api.coingecko.com/api/v3/coins/"+whichcoin+"/market_chart/range?vs_currency="+fiat+"&from="+str(starttimeseconds)+"&to="+str(endtimeseconds)
    print('Got geckourlhistorical')
    rawtimeseries = requests.get(geckourlhistorical).json()
    print('Got price for the last '+str(days_ago)+' days from CoinGecko')
    timeseriesarray = rawtimeseries['prices']
    timeseriesstack = []
    length=len (timeseriesarray)
    i=0
    while i < length:
        timeseriesstack.append(float (timeseriesarray[i][1]))
        i+=1

    timeseriesstack.append(pricenow)
    return timeseriesstack, other

def makeSpark(pricestack):
    # Draw and save the sparkline that represents historical data

    # Subtract the mean from the sparkline to make the mean appear on the plot (it's really the x axis)    
    x = pricestack-np.mean(pricestack)

    fig, ax = plt.subplots(1,1,figsize=(10,3))
    plt.plot(x, color='k', linewidth=6)
    plt.plot(len(x)-1, x[-1], color='r', marker='o')

    # Remove the Y axis
    for k,v in ax.spines.items():
        v.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axhline(c='k', linewidth=4, linestyle=(0, (5, 2, 1, 2)))

    # Save the resulting bmp file to the images directory
    plt.savefig(os.path.join(picdir,'spark.png'), dpi=60)
    imgspk = Image.open(os.path.join(picdir,'spark.png'))
    file_out = os.path.join(picdir,'spark.bmp')
    imgspk.save(file_out) 
    plt.clf() # Close plot to prevent memory error
    ax.cla() # Close axis to prevent memory error
    plt.close(fig) # Close plot

def Draw(config,pricestack,whichcoin,fiat,other):
    crypto_list = currencystringtolist(config['ticker']['currency'])
    host = 'https://api2.nicehash.com'
    organisation_id = str(config['mining']['organisation'])
    key = str(config['mining']['key'])
    secret = str(config['mining']['secret'])
    private_api = nicehash.private_api(host, organisation_id, key, secret)
    accounts = private_api.get_accounts()
    accountsdata = str(accounts['total'])
    currencydata = str(accounts['currencies'])
    currencylist = currencydata.split(":")
    accountslist = accountsdata.split("'")
    wallet = float(accountslist[7]) #isolate total balance
    rate = float('{:.8}'.format(currencylist[7]))
    wallet = float(accountslist[7])
    total = wallet*rate
    balance = float('{:.2f}'.format(total))
    final = str(balance)

    unpaid = private_api.get_unpaid() #get unpaid json

    strdata = str(unpaid['data']) #grab "data" section and convert to string
    listdata = strdata.split(",") #organize
    maybe = float(listdata[2]) #grab total unpaid
    almost = format(float(maybe), '.8f') #convert form scientific to decimal float
    working = decimal.Decimal(almost) #convert from float to decimal
    ok = working * 100000000 #make whole number
    unpfd = int(ok) #convert to integer to drop decimals
    unpf = str(unpfd)
    geckourl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency="+fiat+"&ids="+whichcoin
    rawlivecoin = requests.get(geckourl).json()   
    liveprice = rawlivecoin[0]
    pricenow= float(liveprice['current_price'])
    pricenow = str(pricenow)
    print ('$'+pricenow+'/'+whichcoin)
    output = tk.StringVar()
    output.set('$'+pricenow+'/'+whichcoin)
    currencythumbnail= 'currency/'+whichcoin+'.bmp'
    tokenfilename = os.path.join(picdir,currencythumbnail)
    if os.path.isfile(tokenfilename):
        load = Image.open(tokenfilename)

    else:
        print('Getting token Image from Coingecko')
        tokenimageurl = "https://api.coingecko.com/api/v3/coins/"+whichcoin+"?tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false"
        rawimage = requests.get(tokenimageurl).json()
        load = Image.open(requests.get(rawimage['image']['large'], stream=True).raw).convert("RGBA")
        resize = 125,125
        load.thumbnail(resize, Image.ANTIALIAS)
        new_image = Image.new("RGBA", (125,125), "WHITE") # Create a white rgba background with a 10 pixel border
        new_image.paste(load, (0, 0), load)   
        load=new_image
        load.thumbnail((125,125),Image.ANTIALIAS)
        load.save(tokenfilename)
    pricechange = str("%+d" % round((pricestack[-1]-pricestack[0])/pricestack[-1]*100,2))+"%"
    days_ago=str(config['ticker']['sparklinedays']) 
    render = ImageTk.PhotoImage(load)
    img = Label(image=render, borderwidth=0,highlightthickness = 0)
    img.image = render
    img.place(x=25, y=4)

    load2 = Image.open(os.path.join(picdir,'spark.bmp'))
    render2 = ImageTk.PhotoImage(load2)
    img = Label(image=render2, borderwidth=0,highlightthickness = 0)
    img.config(highlightbackground='white')
    img.image = render2
    img.place(x=-65, y=145)

    frame2.place(x=20,y=124)


    text=Label(frame2,textvariable=output, fg='black', font=('Franklin Gothic Medium', 12, 'bold'), bg='white')
    text.pack()

    frame3.place(x=170,y=50)
    tbal = tk.StringVar()
    tbal.set('NiceHash Wallet Balance: $'+final)

    tbal2=Label(frame3,textvariable=tbal, fg='orange', font=('Franklin Gothic Medium', 12, 'bold'), bg='white')
    tbal2.pack()

    frame4.place(x=170,y=70)
    unpv = tk.StringVar()
    unpv.set('NiceHash Unpaid Mining: '+unpf+' Sat')

    upt=Label(frame4,textvariable=unpv, fg='orange', font=('Franklin Gothic Medium', 12, 'bold'), bg='white')
    upt.pack()

    frame5.place(x=250,y=120)
    sline = tk.StringVar()
    sline.set(str(days_ago+' day : '+pricechange))
    sline2=Label(frame5,textvariable=sline, fg='black', font=('Franklin Gothic Medium', 12, 'bold'), bg='white')
    sline2.pack()

    frame6.place(x=200,y=20)
    ctime = tk.StringVar()
    ctime.set(str(time.strftime("%H:%M %a %d %b %Y")))
    ctime2=Label(frame6,textvariable=ctime, fg='black', font=('Franklin Gothic Medium', 12, 'bold'), bg='white')
    ctime2.pack()
    if str(time.strftime("%H:%M")) == "16:20":
        print('420 BLAZE IT')

    print ('writing config')
def Refresher():

    other={}
    with open(configfile) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    crypto_list = currencystringtolist(config['ticker']['currency'])
    fiat_list=currencystringtolist(config['ticker']['fiatcurrency'])
    crypto_list = currencycycle(crypto_list)
    CURRENCY=crypto_list[0]
    FIAT=fiat_list[0]
    pricestack, ATH = getData(config,CURRENCY, FIAT, other)
    makeSpark(pricestack)
    config['ticker']['currency']=",".join(crypto_list)
    config['ticker']['fiatcurrency']=",".join(fiat_list)
    with open(configfile, 'w') as f:
        data = yaml.dump(config, f)


    for widget in frame2.winfo_children():
        widget.destroy()
    for widget in frame3.winfo_children():
        widget.destroy()
    for widget in frame4.winfo_children():
        widget.destroy()
    for widget in frame5.winfo_children():
        widget.destroy()
    for widget in frame6.winfo_children():
        widget.destroy()
    for widget in frame.winfo_children():
        widget.destroy()
    print ('refreshing')

    threading.Timer(float(config['ticker']['updatefrequency']), Refresher).start()
    Draw(config, pricestack, CURRENCY, FIAT, other)





Refresher()
root.mainloop()