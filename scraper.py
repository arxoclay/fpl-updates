import mechanize
from bs4 import BeautifulSoup
from event import Event

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
    soup = BeautifulSoup(response.read(),"html.parser")
    return soup

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
