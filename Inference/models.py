import json
import uuid
from datetime import datetime

class Trajectory:
    def __init__(self, coords, timestamps, accuracy=None, speed=None, 
            trajId=None, trajType=None, placename=None, durationDays=None):
        #data
        self.coords = coords
        self.timestamps = timestamps
        self.accuracy = accuracy
        self.speed = speed
        #metadata
        self.id = trajId if trajId is not None else uuid.uuid4()
        self.type = trajType
        self.placename = placename
        self.durationDays = durationDays

    #def fromJSON(coords, timestamps, accuracy, speed, state, time0):
    #def toJSON(trajectory=None)

    def addPoint(self, latLon, time, accuracy, speed=None, state=None):
        self.coords.append(latLon)
        self.accuracy.append(accuracy)
        self.timestamps.append(time) #TODO: default to now
        self.speed.append(speed)
        #self.state.append(state)

    def getCopy(self):
        return Trajectory(self.coords, self.timestamps, self.accuracy, self.speed,
                        self.id, self.type, self.placename, self.durationDays)

    #assume geojson is a feature of polyline with properties.timestamps being an array of Unix-epoch timestamps in ms       #No-> iso8601 dates
    def fromGeoJSON(JSONString):
        geoObj = json.loads(JSONString)
        coordinates = geoObj["features"][0]["geometry"]["coordinates"]
        #swap coords
        for coord in coordinates:
            lat = coord[1]
            coord[1] = coord[0]
            coord[0] = lat
        timestamp = geoObj["features"][0]["properties"]["timestamp"]
        for i, stamp in enumerate(timestamp):
            if stamp == '':
                timestamp[i] = None
                continue
            else:
                stamp = int(float(stamp))

                #distinguish between UNIX seconds and ms
                timestamp[i] = None
                try:
                    #this works with UNIX seconds and ms decimals
                    timestamp[i] = datetime.fromtimestamp(stamp)
                except:
                    #fallback for when the value is in unix-milliseconds
                    #this only works for timestamps after 1978-01-11, 21:31:37 (253402297199)
                    stamp = int(stamp) / 1000
                    timestamp[i] = datetime.fromtimestamp(stamp)

        accuracy = geoObj["features"][0]["properties"]["accuracy"]
        for i, point in enumerate(accuracy): #can't get map() to work with empty entries.
            if point == '':
                accuracy[i] = None
                continue
            else:
                accuracy[i] = float(point)
        speed = geoObj["features"][0]["properties"]["speed"]
        for i, point in enumerate(speed): #can't get map() to work with empty entries.
            if point == '':
                speed[i] = None
                continue
            else:
                speed[i] = float(point)

        return Trajectory(coordinates, timestamp, accuracy, speed)
    
    def fromGeoJSONfile(filename):
        file = open(filename, "r").read()
        return Trajectory.fromGeoJSON(file)

    #abstract method
    def fromJSON(JSONstring):
        json = json.loads(JSONstring)

        return Trajectory(
                json["coordinates"],
                json["timestamps"],
                json["accuracy"] if json["accuracy"] else None,
                json["speed"] if json["speed"] else None,
                )

class Point:
    def __init__(self, latLon, time=None, accuracy=None, speed=None, state=None):
        self.latLon = latLon
        self.time = time
        self.accuracy = accuracy
        self.speed = speed
        self.state = state
    
    def __repr__(self):#
        outStr = f'''{{
    "type": "Feature",
    "properties": {{
        "time": "{self.time}",
        "accuracy": "{self.accuracy}",
        "speed": "{self.speed}"
    }},
    "geometry": {{
        "coordinates": [
            {self.latLon[1]},
            {self.latLon[0]}
        ],
        "type":"Point"
    }}
}}'''
        return str(outStr)

class Inference:
    def __init__(self, 
                id, #string 
                name, #string
                infType, #InferenceType, probably just a string. thats easier
                #desc, #string
                trajID, #string
                latLon, #[number,number]
                coords, #[number,number][]
                confidence=None,  #number
                accuracy=None, #number
                onSiteTimes=None #[Date, Date][]
                ):
        self.name = name
        self.id = id
        self.type = infType
        #self.description = desc
        self.trajectoryID = trajID
        self.latLon = latLon
        self.coordinates = coords
        self.confidence = confidence
        self.accuracy = accuracy
        self.onSiteTimes = onSiteTimes
        self.geocoding = None
    
    #def __repr__(self):
    #    return(f"{{coords: {self.latLon}, accuracy: {self.accuracy}, type: {self.type}, confidence: {round(self.confidence, 3)}}}")
    
    def __str__(self):
        outString = f'''{{
    "type": "Feature",
    "properties": {{
        "id": "{self.id}"
        "type": "{self.type}",
        "accuracy": "{self.accuracy}",
        "confidence": {round(self.confidence, 3)}
    }},
    "geometry": {{
        "coordinates": {self.latLon},
        "type": "Point"
    }}
}}'''
        return outString

    #fromObject TODO

    def hasGeocoding(self):
        return self.geocoding is not None

    #def addressDisplayName() #TODO

    #def coordinatesAsPolyline() #TODO

    #def icon() TODO

    #def outlinedIcon() TODO

class InferenceConfidenceThresholds:
    high = 0.6
    medium = 0.3
    low = 0.05

    def getQualitativeConfidence(confidenceValue):
        if(confidenceValue >= InferenceConfidenceThresholds.high):
            return "high"
        elif (confidenceValue >= InferenceConfidenceThresholds.medium):
            return "medium"
        elif (confidenceValue >= InferenceConfidenceThresholds.low):
            return "low"
