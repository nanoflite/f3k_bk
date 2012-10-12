#!/usr/bin/env python

import csv
import glob
import os.path
import json
import pystache

class PilotCollection(object):
    
    def __init__(self):
        self.pilots = []

    def addPilot(self, pilot):
        self.pilots.append( pilot )

    def findPilotByName(self, name):
        for pilot in self.pilots:
            if ( pilot.name == name ):
                return pilot
        return None

    def findOrNewPilot(self, pilotName):
        pilot = self.findPilotByName( score['name'] )
        if (pilot == None):
            pilot = Pilot( score['name'] )
            self.addPilot( pilot )
        return pilot

    def each(self):
        for pilot in self.pilots:
            yield pilot

class Pilot(object):

    def __init__(self, name):
        self.name = name
        self.scores = []
        self.tourScores = []
        self.rank = -1

    def addScore(self, score):
        self.scores.append(score)

    def findScore(self, tourName, contestName):
        for score in self.scores:
            if score.tour.name == tourName and score.name == contestName:
                return score
        score = Score( tour, contestName, 0 )
        self.addScore( score )
        return score

    def addTourScore(self, tour):
        self.tourScores.append( TourScore( tour, tour.calculateScore( pilot ) ) )

    def findTourScore(self, tour):
        for score in self.tourScores:
            if score.tour.name == tour.name:
                return score
        return None

    def calculateTourPercent(self, tour, highScore):
        score = self.findTourScore( tour )
        score.percent = 100.0 * score.score / highScore.score

    def calculateTourScores(self, tour):
        scores = []
        for contest in tour.eachContest():
            scores.append( self.findScore( tour.name, contest ) )
        return scores

    def reachedCriterium(self, tour):
        score = self.findTourScore( tour )
        return tour.reachedCriterium( score )

    def totalScore(self):
        return sum( [ score.score for score in self.tourScores ] )

    def setRank(self, rank):
        self.rank = rank

class Score(object):
    
    def __init__(self, tour, name, score):
        self.tour = tour
        self.name = name
        self.score = float( score )
        self.scrapped = False               

    def attributes(self):
        if (self.scrapped):
            return "scrapped"
        return ""

class TourScore(object):

    def __init__(self, tour, score):
        self.tour = tour
        self.score = score
        self.percent = 0.0
        self.rank = -1

    def setRank(self, rank):
        self.rank = rank

    def __str__(self):
        return "%s / %0.2f / %0.2f" % (self.tour.name, self.score, self.percent)

class TourCollection(object):

    def __init__(self):
        self.tours = []

    def addTour(self, tour):
        self.tours.append( tour )

    def findTourByName(self, tourName):
        for tour in self.tours:
            if ( tour.name == tourName ):
                return tour
        return None

    def findOrNewTour(self, tourName, tourFolder):
        tour = self.findTourByName( tourName )
        if ( tour == None ):
            tour = Tour( tourName, tourFolder )
            self.addTour( tour )
        return tour

    def each(self):
        for tour in self.tours:
            yield tour

class Tour(object):

    def __init__(self, name, tourFolder):
        self.name = name
        self.tourFolder = tourFolder
        self.contests = []
        self.scrappers = 0
        self.criterium = "None"
        self._readConfig()

    def addContest(self, name):
        if name not in self.contests:
            self.contests.append( name )

    def numberContests(self):
        return len(self.contests)

    def eachContest(self):
        for contest in self.contests:
            yield contest    

    def calculateScore(self, pilot):
        scores = pilot.calculateTourScores( self )
        sortedScores = sorted( scores, key=lambda score: score.score )
        for score in sortedScores[0:self.scrappers]:
            score.scrapped = True
        return sum( [ score.score for score in sortedScores[self.scrappers:] ] )

    def _readConfig(self):
        with open("%s/config.json" % self.tourFolder, 'rb') as jsonFile:
            config = json.load(jsonFile)
            if 'scrappers' in config:
                self.scrappers = int( config['scrappers'] )
            if 'retain' in config:
                count = 0
                for dataFile in glob.glob( "%s/*.csv" % self.tourFolder ):
                    count += 1
                self.scrappers = count - int( config['retain'] )
            if 'criterium' in config:
                self.criterium = config['criterium']

    def criterium_percent(self, percent, score):
        return True

def readFiles(folder):
    for dataFile in glob.glob( "%s/*.csv" % folder ):
        for score in readFile(dataFile):
            yield score

def readFile(fileName):
    name = os.path.splitext( os.path.basename( fileName ) )[0]
    with open(fileName, 'rb') as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            yield { 'contest': name, 'name': row['Name'], 'score': row['Score'] } 

tourCollection = TourCollection()
pilotCollection = PilotCollection()

dataFolder = 'data'

for tourFolder in glob.iglob( "%s/*" % dataFolder ):
    tourName = os.path.basename( tourFolder )
    tour = tourCollection.findOrNewTour( tourName, tourFolder )
    for score in readFiles( tourFolder ):
        pilot = pilotCollection.findOrNewPilot( score['name'] )
        pilot.addScore( Score( tour, score['contest'], score['score'] ) )
        tour.addContest( score['contest'] )

for tour in tourCollection.each():
    for pilot in pilotCollection.each():
        pilot.addTourScore( tour )

for tour in tourCollection.each():
    scores = []
    for pilot in pilotCollection.each():
        scores.append( pilot.findTourScore( tour ) )
    highScore = sorted( scores, key = lambda score: -1 * score.score )[0]
    for pilot in pilotCollection.each():
        pilot.calculateTourPercent( tour, highScore )

rank = 1
for pilot in sorted( pilotCollection.each(), key = lambda pilot: -1 * pilot.totalScore() ):
    pilot.setRank( rank )
    rank += 1

for tour in tourCollection.each():
    rank = 1
    for pilot in sorted( pilotCollection.each(), key = lambda pilot: -1 * pilot.findTourScore(tour).score ):
        pilot.findTourScore( tour ).setRank( rank )
        rank += 1

header = []
header.append( { 'value': 'Name' } )
for tour in tourCollection.each():
    for contest in tour.eachContest():
        header.append( { 'value': "%s (%s)" % (contest, tour.name) } )
    header.append( { 'value': "total (%s)" % tour.name } )
    header.append( { 'value': "%% (%s)" % tour.name } )
    header.append( { 'value': "rank (%s)" % tour.name } )
header.append( { 'value': 'WK Total' } )
header.append( { 'value': 'WK Rank' } )
body = []
for pilot in pilotCollection.each():
    row = []
    row.append( { 'value': pilot.name } )
    for tour in tourCollection.each():
        for contest in tour.eachContest():
            row.append( { 'value': "%0.2f" % pilot.findScore( tour.name, contest ).score, 'class': pilot.findScore( tour.name, contest ).attributes() } )
        row.append( { 'value': "%0.2f" % pilot.findTourScore( tour ).score } )
        row.append( { 'value': "%0.2f" % pilot.findTourScore( tour ).percent } )
        row.append( { 'value': "%d" % pilot.findTourScore( tour ).rank } )
    row.append( { 'value': "%0.2f" % pilot.totalScore() } )
    row.append( { 'value': "%d" % pilot.rank } )
    body.append( { 'row': row } )
model = { 'header': header, 'body': body }

renderer = pystache.Renderer()
print renderer.render_path( './index.mustache', model )
