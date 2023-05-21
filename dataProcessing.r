#!/usr/bin/Rscript

workdir <- getwd()
#install.packages("rjson")
#install.packages("stringr")

library("rjson")
library("stringr")



mc_log <- read.csv("mc_join.csv")
nom_log <- read.csv("nom_join.csv")
mes_log <- read.csv("mes_log.csv", sep=";")
#mes_NoDummies <- read.csv("mes_log_noDummies.csv", sep=";")

mes_log$totalData <- cumsum(mes_log$responseSize)
nom_log$totalData <- cumsum(nom_log$responseSize)
#mes_NoDummies$totalData <- cumsum(mes_NoDummies$responseSize)

elapsed_remote <- 0.140645
elapsed_local <- mean(nom_log$elapsed)
delay_remote <- elapsed_remote-elapsed_local

mes_log$elapsedRemote <- mes_log$elapsed + delay_remote
nom_log$elapsedRemote <- nom_log$elapsed + delay_remote
#mes_NoDummies$elapsedRemote <- mes_NoDummies$elapsed + delay_remote


#nom_log$address <- fromJSON(nom_log$nom_result)$display_name
for(i in 1:nrow(nom_log)){
    nom_log$placename[i] <- fromJSON(nom_log$nom_result[i])$display_name
}


print("############### MC log summary ###############")
summary(mc_log)
print("############### NOM log summary ###############")
summary(nom_log)
print("############### MES log summary ###############")
summary(mes_log)
#print("############### MES log summary NO DUMMIES ###############")
#summary(mes_NoDummies)

#x11(xpos=1024,width=10, height=10)
#png()
#plot(type="p", y=mc_log$elapsed, x=nom_log$elapsed, xlim=c(0,0.030), ylim=c(0,0.030))
# wait until window is closed (check every second)
#while(names(dev.cur()) !='null device') Sys.sleep(1)


address <- data.frame(nom_log$placename, mc_log$mc_result)



#TODO: remove duplicates from dataset
for(i in 1:nrow(address)){
    #generalised Levenshtein distance between the two address strings    
    # This method is very inadequate. Longer string differences have
    # higher impact than wrong house number. even if the former pointed
    # to the correct address.
    address$adist[i] <- adist(address$nom[i], address$mc[i])
    #print(paste(i, "/", nrow(address)))

    #need a scoring system based on present substrings.
    # Hausnummer UND Straße. hausnummer alleine schlecht, straße alleine OK
    # Ort UND PLZ. vorzugsweise beides. Punktabzug wenn nur Ortsname
    # Land: country-code ist ausreichend 
    addr_lower = tolower(address$mc[i])
    nomi_addr = fromJSON(nom_log$nom_result[i])$address

    
    
    #scoring
    number      <- FALSE
    wrongNumber <- FALSE
    street      <- FALSE
    postcode    <- FALSE
    city        <- FALSE
    country     <- FALSE 
    
    #print(exists(nomi_addr$house_number))

    #using https://nominatim.org/release-docs/latest/api/Output/#addressdetails to make sure most cases are covered
    if(!is.null(nomi_addr$house_number)){
        extractedNumber <- str_extract(addr_lower, "^[0-9]+")
        wrongNumber <- !is.na(extractedNumber) & (extractedNumber != nomi_addr$house_number)
        number = (grepl(nomi_addr$house_number, addr_lower) & !wrongNumber)
    }
    if(!number && !is.null(nomi_addr$house_name)){
        number = grepl(nomi_addr$house_name, addr_lower)
    }
    if(!is.null(nomi_addr$road)){
        street = grepl(tolower(nomi_addr$road), addr_lower) #| grepl(tolower(nomi_addr$city_block), addr_lower)
    }
    if(!street && !is.null(nomi_addr$highway)){
        street = grepl(tolower(nomi_addr$highway), addr_lower) #| grepl(tolower(nomi_addr$city_block), addr_lower)
    }
    if(!is.null(nomi_addr$postcode)){
        postcode = grepl(tolower(nomi_addr$postcode), addr_lower) 
    }
    if(!is.null(nomi_addr$city)){
        city = grepl(tolower(nomi_addr$city), addr_lower)
    }
    if(!city && !is.null(nomi_addr$town)){
        city = grepl(tolower(nomi_addr$town), addr_lower)
    }
    if(!is.null(nomi_addr$country_code)){
        country = grepl(tolower(nomi_addr$country_code), addr_lower)
    }
    if(!country && !is.null(nomi_addr$country)){
        country = grepl(tolower(nomi_addr$country), addr_lower)
    }
    address$numberMatch[i] = number
    address$wrongNumber[i] = wrongNumber
    address$streetMatch[i] = street 
    address$postcodeMatch[i] = postcode
    address$cityMatch[i] = city
    address$countryMatch[i] = country


    #summing weighted score
    #score = 1*country + 2*postcode + 3*city + 3*street + 2*number - 1*wrongNumber
    #score = 1*country + 1*postcode + 1*city + 1*street + 1*number #- 1*wrongNumber
    score = 0
    maxScore = 0
    if(!is.null(nomi_addr$house_number) || !is.null(nomi_addr$house_name)){
        score = score + 1*number
        maxScore = maxScore + 1
    }
    if(!is.null(nomi_addr$road) || !is.null(nomi_addr$highway)){
        score = score + 1*street
        maxScore = maxScore + 1
    }
    if(!is.null(nomi_addr$postcode)){
        score = score + 1*postcode
        maxScore = maxScore + 1
    }
    if(!is.null(nomi_addr$city) || !is.null(nomi_addr$town)){
        score = score + 1*city
        maxScore = maxScore + 1
    }
    if(!is.null(nomi_addr$country_code) || !is.null(nomi_addr$country)){
        score = score + 1*country
        maxScore = maxScore + 1
    }
    
    confidence = score/maxScore
    if(confidence < 0){
        confidence = 0
    }

    address$correctness[i] = confidence
}

addr <- address[!duplicated(address), ]

print("############### address result summary ###############")
summary(addr)

#write.csv(addr, "address_correctness.csv")

#correlation between correctness and edit distance
correlation <- cor(addr$correctness, addr$adist)
print(correlation)

#x11(xpos=1024,width=10, height=10)
png(filename="CorrectnessRelation.png", width=1433, height=900, units = "px", pointsize = 24)
plot(
    type="p", y=addr$correctness, x=addr$adist, ylim=c(0,1), 
    xlab="edit distance", ylab="correctness scoring"
)
title(    
    main="Relation of edit distance to correctnes scoring"
)
# wait until window is closed (check every second)
#while(names(dev.cur()) !='null device') Sys.sleep(1)
