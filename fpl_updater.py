import mechanize
from bs4 import BeautifulSoup
import random
import time
import smtplib
import datetime
import os
from unidecode import unidecode

class Event:
    def __init__(self, name, player, quantity):
        self.name = name
        self.player = player
        self.quantity = quantity

    def __str__(self):
        return ', '.join([self.name, unidecode(self.player), str(self.quantity)])

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

def LoginToFantasyPremierLeague(browser, userConfiguration):
    response = browser.open("https://users.premierleague.com/PremierUser/account/login.html")
    formCount=0
    for form in browser.forms():
        if "id" in form.attrs and str(form.attrs["id"])=="login_form":
            break
        formCount=formCount+1
      
    browser.select_form(nr=formCount)
    browser.form["j_username"] = userConfiguration['fpl_username']
    browser.form["j_password"] = userConfiguration['fpl_password']
    response = browser.submit()
    print "Logged in user: " + userConfiguration['fpl_username']

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

def Notify(updates, userConfiguration, configuration):

    if configuration['notifications_enabled'] == "True":
        print "Notifying user"
        phoneNumber = userConfiguration['notification_phone']
        emailAddress =  userConfiguration['notification_email']
        toaddrs = []
        if phoneNumber:
            toaddrs.append(phoneNumber + "@tmomail.net")
        if emailAddress:
            toaddrs.append(emailAddress)
        fromaddr = "notifier@fantasypremierleagueupdates.com"
        message_subject = "Fantasy Premier League updates"
        message_text = "\n".join(map(str,updates))
        message = "From: %s\n" % fromaddr + "To: %s\n" % ",".join(toaddrs) + "Subject: %s\n" % message_subject + "\n"+ message_text
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(configuration['smtp_username'], configuration['smtp_password'])
        server.sendmail(fromaddr, toaddrs, message)
        server.quit()
    print "Updates for user " + userConfiguration['fpl_username']
    for update in updates:
        print update

def Run():
    storedEvents = {}
    configuration = {}
    userConfiguration = {}
    while True:
        try:
            modifiedTime = os.stat('Config.txt').st_mtime
            if not configuration or modifiedTime != configurationLastModified:
                configuration = GetConfig("Config.txt")
                configurationLastModified = modifiedTime
                
            randomSleepInterval = random.randint(int(configuration['min_sleep']), int(configuration['max_sleep']))
            print "Sleeping for " + str(randomSleepInterval) + " seconds"
            time.sleep(randomSleepInterval)

            modifiedTime = os.stat('UserConfig.txt').st_mtime
            if not userConfiguration or modifiedTime != userConfigurationLastModified:
                userConfiguration = GetUserConfig("UserConfig.txt")
                userConfigurationLastModified = modifiedTime

            for user in userConfiguration['users']:
                startTime = datetime.datetime.now()
                print "Started processing user at " + startTime.time().isoformat()
                if user not in storedEvents:
                    storedEvents[user] = []
                    
                browser = GetBrowser()
                print "Logging in user: " + user
                LoginToFantasyPremierLeague(browser, userConfiguration[user])
                response = GetPointsPage(browser)
                soup = BeautifulSoup(response.read(),"html.parser")

                print "Fetching squad"
                # Get squad
                squad = GetCurrentSquad(soup)
                teamPlayers = squad[0]
                benchPlayers = squad[1]

                print "Fetching events"
                # Get events
                events = GetCurrentEvents(soup)

                # Get relevant events
                relevantEvents = filter(lambda x: x.player in teamPlayers or x.player in benchPlayers, events)

                print "Computing updates"
                # Figure out the updates
                updates = filter(lambda x: x not in storedEvents[user], relevantEvents)

                print str(len(updates)) + " updates found"
                storedEvents[user] = relevantEvents
                
                if len(updates) == 0:
                    print "No new updates :)"
                else:
                    Notify(updates, userConfiguration[user], configuration)

                endTime = datetime.datetime.now()
                print "Done processing user at " + endTime.time().isoformat()
                print "Processing time: " + str((endTime - startTime).total_seconds()) + " seconds"

 
        except Exception, e:
            print e

def GetConfig(fileName):
    d = {}
    with open(fileName) as f:
        for line in f:
            (key, val) = line.rstrip('\n').split(':')
            d[key] = val
    print "Configuration acquired " + str(d)
    return d

def GetUserConfig(fileName):
    userData = {}
    userData['users'] = []
    fields = []
    with open(fileName) as f:
        for line in f:
            if len(fields) == 0:
                fields = line.rstrip('\n').split(',')
            else:
                (a, b, c, d) = line.rstrip('\n').split(',')
                userData["users"].append(a)
                userData[a] = { fields[0] : a, fields[1] : b,
                                        fields[2] : c, fields[3] : d}
    print "User configuration acquired " + str(userData)
    return userData
    
Run()
