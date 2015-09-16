import mechanize
from bs4 import BeautifulSoup
import random
import time
import smtplib

class Event:
    def __init__(self, name, player, quantity):
        self.name = name
        self.player = player
        self.quantity = quantity

    def __str__(self):
        return ", ".join([self.name, self.player, str(self.quantity)])

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
        

def GetBrowser():
    # Browser
    browser = mechanize.Browser()

    # Browser options
    browser.set_handle_equiv(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots(False)
    return browser

def LoginToFantasyPremierLeague(browser, configuration):
    response = browser.open("https://users.premierleague.com/PremierUser/account/login.html")
    formCount=0
    for form in browser.forms():
        if "id" in form.attrs and str(form.attrs["id"])=="login_form":
            break
        formCount=formCount+1
      
    browser.select_form(nr=formCount)
    browser.form["j_username"] = configuration['fpl_username']
    browser.form["j_password"] = configuration['fpl_password']
    response = browser.submit()

def GetPointsPage(browser):
    response = browser.open("http://fantasy.premierleague.com")
    link = browser.find_link(text_regex="Points")
    response = browser.follow_link(link)
    return response

def GetCurrentSquad(soup):
    teamTag = soup.find("div", {"class": "ismPitch"})
    benchTag = soup.find("div", {"class": "ismBench"})

    teamPlayerTags = teamTag.find_all("span", { "class" : "ismElementText ismPitchWebName JS_ISM_NAME" },recursive=True)
    benchPlayerTags = benchTag.find_all("span", { "class" : "ismElementText ismPitchWebName JS_ISM_NAME" },recursive=True) 
    teamPlayers = map(lambda x: x.text.strip(), teamPlayerTags)
    benchPlayers = map(lambda x: x.text.strip(), benchPlayerTags)

    return (teamPlayers, benchPlayers)

def GetCurrentEvents(soup):
    results = soup.find("table", {"class": "ismFixtureTable"})
    playerTags = results.find_all("a", { "class": "ismViewProfile"} )

    events = []
    for playerTag in playerTags:
        playerName = playerTag.text
        eventName = playerTag.parent.findPreviousSibling('dt').text
        if eventName == "Yellow cards" or eventName == "Red cards":
            quantity = 1
        else:
            playerTagParentText = playerTag.parent.text
            if "(" not in playerTagParentText:
                quantity = 1
            else:
                quantity = int(playerTagParentText.split("(")[1].split(")")[0])
        events.append(Event(eventName,playerName,quantity))

    return events

def Notify(updates, configuration):

    if configuration['notifications_enabled'] == "True":
        toaddrs = [configuration['notification_phone'] + "@tmomail.net", configuration['notification_email']]
        fromaddr = "notifier@fantasypremierleagueupdates.com"
        message_subject = "Fantasy Premier League updates"
        message_text = "\n".join(map(str,updates))
        message = "From: %s\n" % fromaddr + "To: %s\n" % ",".join(toaddrs) + "Subject: %s\n" % message_subject + "\n"+ message_text
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(configuration['smtp_username'], configuration['smtp_password'])
        server.sendmail(fromaddr, toaddrs, message)
        server.quit()
        
    for update in updates:
        print update

def Run(storedEvents, configuration):
    while True:
        try:
            randomSleepInterval = random.randint(int(configuration['min_sleep']), int(configuration['max_sleep']))
            print "Sleeping for " + str(randomSleepInterval) + " seconds"
            time.sleep(randomSleepInterval)
            
            browser = GetBrowser()
            LoginToFantasyPremierLeague(browser, configuration)
            response = GetPointsPage(browser)
            soup = BeautifulSoup(response.read(),"html.parser")

            # Get squad
            squad = GetCurrentSquad(soup)
            teamPlayers = squad[0]
            benchPlayers = squad[1]

            # Get events
            events = GetCurrentEvents(soup)

            # Get relevant events
            relevantEvents = filter(lambda x: x.player in teamPlayers or x.player in benchPlayers, events)
            
            # Figure out the updates
            updates = filter(lambda x: x not in storedEvents, relevantEvents)
            storedEvents = relevantEvents
            
            if len(updates) == 0:
                print "No new updates :)"
            else:
                Notify(updates, configuration)
        except Exception, e:
            print e

def GetConfig(fileName):
    d = {}
    with open(fileName) as f:
        for line in f:
           (key, val) = line.rstrip('\n').split(':')
           d[key] = val
    return d
    
configuration = GetConfig("Config.txt")
Run([], configuration)
