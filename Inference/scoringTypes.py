#TODO: UNTESTED
#technically violating DRY principle, but I think it's better to not let the 
#software design stray too far from the original to make bugfixing easier

import datetime as dt
from scoringTypes import *
from functools import reduce

''' this throws strange error on import
from enum import Enum

#https://docs.python.org/3/library/enum.html
class InferenceScoringType(Enum):
    spatialVariance = "spatialVariance"
    temporalContinuity = "temporalContinuity"
    pointCount = "pointCount"
    nightnesss = "nightness"
    workHous9to5 = "workHours9to5"

class InferenceType(Enum):
    home = "home"
    work = "work"
    poi = "poi"
'''

'''
String scoringType
'''
class InferenceDefinition:
    '''
    scoringType: "pointCount" OR "workHours9to5" OR "nightness"

    '''
    def __init__(self, scoringType, scoringWeight=1, scoringConfidence=0.3, info=None, iconName=None):
        self.scoringConfigurations = [
            {
            "type": scoringType,
            "weight": scoringWeight,
            "confidence": scoringConfidence
            }
        ]
        self.type = scoringType
    
    def getScoringConfig(self, scoringType):
        for config in self.scoringConfigurations:
            if config["type"] == scoringType:
                return config
        else:
            return None

class PointCountScoring:
    def __init__(self):
        self.type = "pointCount"
    
    '''
    params: point[] cluster, point[][] allClusters
    '''
    def score(self, cluster, allClusters):
        minClusterSize = min(map(len, allClusters))
        maxClusterSize = max(map(len, allClusters))

        deltaClusterSize = abs(maxClusterSize - minClusterSize)
        pointCountScore = 1.0 #default for if delta is 0
        if deltaClusterSize != 0:
            pointCountScore = (len(cluster) - minClusterSize) * (1 / deltaClusterSize)
        return {"type": self.type, "value": pointCountScore}

class WorkHoursScoring:
    def __init__(self):
        self.type = "workHours9to5"
        self.referenceStartHours = 9
        self.referenceEndHours = 17

    def score(self, cluster, allClusters):
        #filter work hours
        workHourPoints = []
        for point in cluster:
            if point.time is not None:
                if self.isUsualWorkingTime(point.time):
                    workHourPoints.append(self.isUsualWorkingTime(point.time))
        workHourPointPercentage = len(workHourPoints) / len(cluster)
        return {"type": self.type, "value": workHourPointPercentage}

    '''
    params: dt.datetime time
    '''
    def isUsualWorkingTime(self, time):
        return self.isWorkingHours(time.hour, time.minute) and self.isWorkingDay(time.weekday())

    def isWorkingHours(self, hours, minutes):
        minutesToDecimalHoursFactor = 0.0166
        hoursAndMinutes = hours + minutes * minutesToDecimalHoursFactor
        return (hoursAndMinutes > self.referenceStartHours and hoursAndMinutes < self.referenceEndHours)

    def isWorkingDay(self, weekday):
        return (weekday > 0 and weekday < 6)

class NightnessScoring:
    def __init__(self):
        self.type = "nightness"

    def score(self, cluster, allClusters):
        #simple average 'nightness' from 1 (midnight) to 0 (midday)
        diffsToMidnight = []
        for point in cluster:
            if point.time is not None:
                diffsToMidnight.append(self.computeDiffToMidnight(point))
            
        sumDiffs = reduce(lambda x,y: x+y, diffsToMidnight)
        avgDiff = sumDiffs / len(diffsToMidnight) if len(diffsToMidnight) > 0 else -1
        nightness = 1 - avgDiff / 12
        return {"type": self.type, "value": nightness}

    #TODO: check this. this one i am unsure about. time might behave different in Typescript
    def computeDiffToMidnight(self, point):
        referenceHoursAndMinutes = 0
        pointHoursAndMinutes = NightnessScoring.getHoursAndMinutes(point.time)
        diffToMidnight = abs(
            pointHoursAndMinutes - referenceHoursAndMinutes
        )
        if (diffToMidnight > 12):
            diffToMidnight = abs(diffToMidnight - 24)
        return diffToMidnight
        
    '''
    params: dt.datetime time
    '''
    def getHoursAndMinutes(time):
        minutesToDecimalHoursFactor = 0.0166
        return time.hour + time.minute * minutesToDecimalHoursFactor