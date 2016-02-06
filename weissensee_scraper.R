# Scraper to get all participant names from skate4air website and write it to csv.
library(rvest)

scrapeUser = function(tds){
    id <- as.numeric(tds[3] %>% html_text)
    name <- tds[4] %>% html_text
    country <- tds[5] %>% html_text
    city <- tds[6] %>% html_text
    laps <- tds[8] %>% html_text
    distance <- tds[9] %>% html_text
    time <- tds[10] %>% html_text
    speed <- tds[12] %>% html_text
    c(id, name, country, city, laps, distance, time, speed)
}

#scrape the event with given id
scrapeEvent = function(eventId, date){  
  #resulting df for this eventId
  eventResult <- data.frame(EventId = numeric(), Date = numeric(), Id = numeric(),Name = character(),Country = character(),City = character(),
                            Laps = numeric(), Distance = numeric(),Time = character(),Speed = character(), stringsAsFactors=FALSE)
  
  distances <- c("1", "2")
  for (distance in distances){
    url <- sub("%s", 2000, baseUrl) #number of records
    url <- sub("%s", eventId, url) #eventId    
    url <- sub("%s", distance, url) #distance
    print(url) 
    
    data <- read_html(url)
    
    ## list of users checked
    data_checked = list()
    
    # select the results table
    resultsTable <- data %>% html_nodes("table.leaderboard_table_results")
    rows <- resultsTable %>% html_nodes("tr")
    for(i in 2:length(rows)){
      row <- rows[i]
      tds <- row %>% html_nodes("td")
      if (length(tds) > 1) {
        person <- scrapeUser(tds)
        result <- c(eventId, date, person[1], person[2], person[3], person[4], person[5], person[6], person[7], person[8])
        eventResult[nrow(eventResult)+1,] <- result
      }
    }
    print("Finished scraping event,distance")
  }
  #print(eventResult)
  write.table(eventResult, filename, row.names=F, na="NA",append=T, quote= FALSE, sep=";", col.names=F)
}

#Main start
filename <- "data/results.csv"
baseUrl <- "http://live.ultimate.dk/desktop/front/data.php?mode=leaderboard&leaderboardid=0&olddistance=1&category=&show=standings&language=nl&records=%s&eventid=%s&distance=%s"

#write header
if (file.exists(filename)) 
  file.remove(filename)
write.table(all_results, filename, row.names=F, na="NA",append=T, quote= FALSE, sep=";", col.names=T)

#all participants
all_results <- data.frame(EventId = numeric(), Date = numeric(), Id = numeric(),Name = character(),Country = character(),City = character(),
                          Laps = numeric(), Distance = numeric(),Time = character(),Speed = character())
eventDates <- list("220103" = "24-1-2014", "220105" = "28-1-2014", "220108" = "30-1-2014", 
                   "2020942" = "23-1-2015", "2020945" = "27-1-2015", "2020948" = "30-1-2015",
                   "2021041" = "19-1-2016", "2021043" = "22-1-2016", "2021046" = "26-1-2016",
                   "2021049" = "29-1-2016")
eventDatesTest <- list("2021041" = "19-1-2016")
keys <- names(eventDates)
for(i in 1:length(keys)){
  scrapeEvent(keys[i], eventDates[keys[i]])
}