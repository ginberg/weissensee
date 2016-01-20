# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 16:14:27 2016
Scraper for Weissensee results based on event id's, where the output is written to a csv file.

@author: Ger Inberg
"""
# coding: utf-8
from bs4 import BeautifulSoup
import urllib2, time, random, csv

class ScrapeUser:
    def __init__(self, data, user_id):
        self.data = data        
        self.persondict = {}
        self.persondict["user_id"] = user_id


    def toUnicode(self, name):
        return name.encode('utf8')
  
    def getPersonalia(self):
        self.persondict["name"] = self.toUnicode(self.data[3].contents[0])
        self.persondict["country"] = self.data[4].contents[1].contents[0]
        self.persondict["city"] = self.toUnicode(self.data[5].contents[0])
        self.persondict["laps"] = self.data[7].contents[0]
        self.persondict["distance"] = self.data[8].contents[0]
        self.persondict["time"] = self.data[9].contents[0]
        self.persondict["speed"] = self.data[11].contents[0]
        # add diff it it has a value        
        diff = self.data[10].contents
        if diff:
            self.persondict["diff"] = diff[0]
        
    def scrape(self):        
        if self.data:
            self.getPersonalia()
        return self.persondict

class ScrapeUsers:
    
    #Amount of records
    AMOUNT_OF_RECORDS = 2000

    def __init__(self, eventId):
        self.eventId = eventId
        
    def updateURL(self):
        self.url = "http://live.ultimate.dk/desktop/front/data.php?mode=leaderboard&leaderboardid=0&distance=1&olddistance=1&category=&show=standings&language=nl&records=%s&eventid=%s" % (self.AMOUNT_OF_RECORDS, self.eventId)
        print self.url        
                
    def requestMainDataPage(self):
        page = urllib2.urlopen(self.url).read()    
        data = BeautifulSoup(page)
        #print data
        return data
        
    def scrape(self):
        print "Now Scraping event : " + self.eventId
        # create csv file to write data to
        filename = "data/weissensee_results.csv"

        with open(filename, 'a') as fp:        
            self.writer = csv.writer(fp, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            # generate the Url
            self.updateURL()
          
            # get the data from this URL
            data = self.requestMainDataPage()
            #print data
            
            ## Get all the link4 items e.g. the links to the profiles
            data_checked = []
            resultsTable = data.find("table", {"class" : "leaderboard_table_results"})
            # skip the first row        
            userRows = resultsTable.findAll("tr")[1:]        
            for userRow in userRows:
                userContents = userRow.findAll("td")
                if len(userContents) > 1:
                    userId = userContents[2].text
                    #print userId
                    if not userId in data_checked:
                        data_checked.append(userId)
                        print "scraping user:",  userId
                        s = ScrapeUser(userContents, userId)
                        personDict = s.scrape()
                        data = [self.eventId, personDict["user_id"], personDict["name"],  
                                personDict["country"], personDict["city"], personDict["laps"], 
                                personDict["distance"], personDict["time"], personDict["speed"]]
                        print data                        
                        self.writer.writerow(data)
                        #print "wrote:", userId         
            
        print "sleeping ..... "
        time.sleep(1 + random.uniform(0, 1)) 
        print "done "

#list of eventIds
events =  ["2020942", "2020945", "2020948"]
for event in events:
    s = ScrapeUsers(event)
    s.scrape()





