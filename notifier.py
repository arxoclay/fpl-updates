import smtplib

def Notify(updates, userConfiguration, configuration):

    if configuration['notifications_enabled'] == "True":
        print "Notifying user"
        phoneDetails = userConfiguration['notification_phone']
        emailAddress =  userConfiguration['notification_email']
        toaddrs = []
        if phoneDetails:
            (carrier, phoneNumber) = phoneDetails.split("-")
            if carrier == "AT&T":
                toaddrs.append(phoneNumber + "@txt.att.net")
            elif carrier == "Verizon":
                toaddrs.append(phoneNumber + "@vtext.com")
            elif carrier == "TMobile":
                toaddrs.append(phoneNumber + "@tmomail.net")
            else:
                raise ValueError('Unknown carrier specified. notification_phone set to ' + phoneDetails)
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
