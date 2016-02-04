# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 16:14:27 2016
Scraper for Weissensee results based on event id's, where the output is written to a csv file.

@author: Ger Inberg
"""
# coding: utf-8
from bs4 import BeautifulSoup
import urllib2, time, random, csv, os
from collections import OrderedDict

class ScrapeUser:
    def __init__(self, date, data, id, eventId):
        self.date = date        
        self.data = data
        self.eventId = eventId        
        self.persondict = {}
        self.persondict["id"] = id

    def toUnicode(self, data, index, subContent):
        if len(data.contents) > index:
            if subContent:
                subContent = data.contents[index].contents[0]
                return subContent.encode('utf8')
            else:
                return data.contents[index].encode('utf8')
        else:
            if data.string is None:
                return ''
            else:
                return data
              
    def getPersonalia(self):
        #print self.data
        self.persondict["name"] = self.toUnicode(self.data[3], 0, False)
        self.persondict["country"] = self.toUnicode(self.data[4], 1, True)
        self.persondict["city"] = self.toUnicode(self.data[5], 0, False)
        self.persondict["laps"] = self.data[7].contents[0]
        self.persondict["distance"] = self.data[8].contents[0]
        self.persondict["time"] = self.data[9].contents[0]
        # add diff if it has a value 
        diff = self.data[10].contents
        if diff:
            self.persondict["diff"] = diff[0]
        else:
            self.persondict["diff"] = 0
        speed = self.data[11]               
        # speed is not always available, do some checks
        if len(speed.contents) >= 1:
            speedString = speed.contents[0].string
            if speedString is not None and "km/h" in speedString:
                self.persondict["speed"] = speedString  
            else:
                self.persondict["speed"] = 'NaN'            
        else:
            self.persondict["speed"] = 'NaN'        
        
    def scrape(self):        
        if self.data:
            self.getPersonalia()
        return self.persondict

class ScrapeEvent:
    
    #Amount of records
    AMOUNT_OF_RECORDS = 2000    

    def __init__(self, writer, eventId, date):
        self.writer = writer        
        self.eventId = eventId
        self.date = date
        
    def updateURL(self, distance):
        self.url = "http://live.ultimate.dk/desktop/front/data.php?mode=leaderboard&leaderboardid=0&olddistance=1&category=&show=standings&language=nl&records=%s&eventid=%s&distance=%s" % (self.AMOUNT_OF_RECORDS, self.eventId, distance)       
        print self.url        
                
    def requestMainDataPage(self):
        page = urllib2.urlopen(self.url).read()    
        data = BeautifulSoup(page)
        return data
        
    def scrape(self):
        # Distance 1 = 200km, 2 = 100km
        distances = ["1", "2"]
        for distance in distances:
            print "Now Scraping event-distance : " + self.eventId + "-" + distance

            # generate the Url
            self.updateURL(distance)
          
            # get the data from this URL
            data = self.requestMainDataPage()
            
            ## list of users checked
            data_checked = []
            # select the results table
            resultsTable = data.find("table", {"class" : "leaderboard_table_results"})
            # skip the first row        
            userRows = resultsTable.findAll("tr")[1:]        
            for userRow in userRows:
                userContents = userRow.findAll("td")
                if len(userContents) > 1:
                    id = userContents[2].text
                    #print id
                    if not id in data_checked:
                        data_checked.append(id)
                        #print "scraping user:",  id
                        s = ScrapeUser(self.date, userContents, id, self.eventId)
                        personDict = s.scrape()
                        data = [self.eventId, self.date, personDict["id"], personDict["name"],  
                                personDict["country"], personDict["city"], personDict["laps"], 
                                personDict["distance"], personDict["time"], personDict["speed"]]                       
                        self.writer.writerow(data)        
                
            print "Finished scraping event-distance :" + self.eventId + "-" + distance 
            time.sleep(1 + random.uniform(0, 1)) 



#map with eventId's to dates
eventDates = OrderedDict()
eventDates["220103"] = "24-1-2014"
eventDates["220105"] = "28-1-2014"
eventDates["220108"] = "30-1-2014"
eventDates["2020942"] = "23-1-2015"
eventDates["2020945"] = "27-1-2015"
eventDates["2020948"] = "30-1-2015"
eventDates["2021041"] = "19-1-2016"
eventDates["2021043"] = "22-1-2016"
eventDates["2021046"] = "26-1-2016"
eventDates["2021049"] = "29-1-2016"

# filename to write data to
FILENAME = "data/weissensee_results.csv"
#remove old file if exists
try:
    os.remove(FILENAME)
except OSError:
    pass

print "Starting"
with open(FILENAME, 'a') as fp:
    writer = csv.writer(fp, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    #write header row
    writer.writerow(["EventId", "Date", "Id", "Name", "Country", "City", "Laps", "Distance", "Time", "Speed"]) 
    # scrape all events in Map
    for event in eventDates:
        s = ScrapeEvent(writer, event, eventDates[event])
        s.scrape()
print "Done"




