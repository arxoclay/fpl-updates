import random
import time
import datetime
import os
import logging
from event import Event
import scraper
import notifier

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
                    
                browser = scraper.GetBrowser()
                print "Logging in user: " + user
                scraper.LoginToFantasyPremierLeague(browser, userConfiguration[user])
                soup = scraper.GetPointsPage(browser)

                print "Fetching squad"
                # Get squad
                squad = scraper.GetCurrentSquad(soup)
                teamPlayers = squad[0]
                benchPlayers = squad[1]

                print "Fetching events"
                # Get events
                events = scraper.GetCurrentEvents(soup)

                # Get relevant events
                relevantEvents = filter(lambda x: x.player in teamPlayers or x.player in benchPlayers, events)

                print "Computing updates"
                # Figure out the updates
                updates = Event.GetEventUpdates(storedEvents[user], relevantEvents)

                print str(len(updates)) + " updates found"
                storedEvents[user] = relevantEvents
                
                if len(updates) == 0:
                    print "No new updates :)"
                else:
                    notifier.Notify(updates, userConfiguration[user], configuration)

                endTime = datetime.datetime.now()
                print "Done processing user at " + endTime.time().isoformat()
                print "Processing time: " + str((endTime - startTime).total_seconds()) + " seconds"

 
        except Exception, e:
            print e
            logging.exception(datetime.datetime.now().isoformat())
            

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

logging.basicConfig(level=logging.DEBUG, filename='error.log')   
Run()
