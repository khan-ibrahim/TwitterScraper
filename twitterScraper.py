import time
import configparser
import requests
import os
import base64
import json

usersFilePath = 'twitterScraper_usernames.txt'
configFilePath = 'twitterScraper_config.txt'

users = []
numRequestsMade = 0

# # TODO: make private?
consumer_api_key = None
consumer_secret_api_key = None
bearer_token = None

#in a 24-hour period, a single app can make up to 100,000 requests
checksPerDay = 10   #number of times in 24hrs that all data is refreshed
delayBetweenUser = 180    #in seconds

dataFilePathPrefix = ''

def log(string):
    return


# CONFIGURATION
#

#Generates configFile with blank auth keys and default settings
def generateConfigFile(configFilePath):
    config = configparser.ConfigParser()
    config['AUTHENTICATION'] = {'consumer_api_key':'', \
    'consumer_secret_api_key':''}
    config['SETTINGS'] = {'checksPerDay':10, 'delayBetweenUser':180, \
    'dataFilePathPrefix':'dataFile_'}

    with open(configFilePath, 'w') as configFile:
        config.write(configFile)

    print('Config generated at {}'.format(os.path.abspath(configFilePath)))
    print('Set keys before using')
    # TODO: generate config file
    return

def loadConfig(configFilePath):
    print('Loading config from {}'.format(os.path.abspath(configFilePath)))
    if(not os.path.exists(configFilePath)):
        print('ERROR: Config not found at configFilePath: {}'\
        .format(os.path.abspath(configFilePath)))
        #print('Generate Sample Config: python twitterScraper.py --configGen')
        exit(1)

    config = configparser.ConfigParser()
    config.read(configFilePath)

    global consumer_api_key
    global consumer_secret_api_key
    consumer_api_key = config['AUTHENTICATION']['consumer_api_key']
    consumer_secret_api_key = config['AUTHENTICATION']['consumer_secret_api_key']

    if(consumer_api_key == '' or consumer_secret_api_key == ''):
        print('ERROR: consumer_api_key and consumer_secret_api_key must be set')
        exit(1)

    global checksPerDay
    global delayBetweenUser
    checksPerDay = config['SETTINGS']['checksPerDay']
    delayBetweenUser = config['SETTINGS']['delayBetweenUser']

    global dataFilePathPrefix
    dataFilePathPrefix = config['SETTINGS']['dataFilePathPrefix']

    return

# AUTHENTICATION
#

def generateBearerCredentials(consumer_api_key, consumer_secret_api_key):
    #url_key = urlEncode(consumer_api_key)
    #url_secret_key = urlEncode(consumer_secret_api_key)
    bearerCredentials = consumer_api_key + ':' + consumer_secret_api_key
    return base64.b64encode(bytearray(bearerCredentials, 'utf-8'))

def getBearerToken():
    global bearer_token

    if not bearer_token == None:
        return bearer_token

    bearerCredentials = \
    generateBearerCredentials(consumer_api_key, consumer_secret_api_key)

    # HTTP POST request to ouath2/token
    url = 'https://api.twitter.com/oauth2/token'
    headers = {}
    auth = b'Basic ' + bearerCredentials
    headers['Authorization'] = auth
    headers['Content-Type'] = r'application/x-www-form-urlencoded;charset=UTF-8'
    body = 'grant_type=client_credentials'

    r = requests.post(url, headers=headers, data=body)

    if not r.status_code == requests.codes.ok:
        print('ERROR requesting bearerToken')
        r.raise_for_status()
        exit(1)

    payload = r.json()

    if not payload['token_type'] == 'bearer':
        print('ERROR: Getting bearertoken: token_type invalid')
        print(payload)
        exit(1)

    bearer_token = payload['access_token']

    return bearer_token

#adds new users to users list from user file.
def loadUsers(usersFilePath):
    print('Loading users from {}'.format(os.path.abspath(usersFilePath)))
    with open(usersFilePath, 'r') as usersList:
        for user in usersList:
            if not str.strip(user) in users:
                users.append(str.strip(user))
    print(users)
    return

def getLastLoggedTweetId(screenName):
    # TODO: get the id of the user's most recently downloaded tweet
    return

def getMoreTweets(screen_name, since_id):
    # TODO: getTweets of screen_name made since tweet since_id
    # GET request to https://api.twitter.com/1.1/statuses/user_timeline.json

    url = '''https://api.twitter.com/1.1/statuses/user_timeline.json'''

    headers = {}
    headers['Authorization'] = 'Bearer ' + bearer_token

    params = {}
    params['tweet_mode'] = 'extended'
    params['screen_name'] = screen_name[1:]

    if since_id == None:
        numRecentTweets = 50
        # request as many as possible (omit count/since_id)
        params['count'] = numRecentTweets
        print('Getting {} most recent tweets from {}'.format(numRecentTweets, screen_name))

    else:
        # request tweets since since_id
        print('Getting tweets from {} since tweet id {}'.format(screen_name, since_id))
        params['since_id'] = since_id

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()

    # TODO: track response ratelimit data

    return r.json()

def initializeTweetsData(screen_name):
    with open(dataFilePathPrefix + screen_name[1:], 'x') as f: pass
    # TODO:
    return

# stores one tweet dict per line, from oldest to newest
def updateTweetsData(screen_name, tweetsJson):
    filePath = dataFilePathPrefix + screen_name[1:]
    dataFile = open(filePath, 'a')
    while len(tweetsJson) > 0:
        tweet = tweetsJson.pop()
        tweetJsonStr = json.dumps(tweet)
        dataFile.write(tweetJsonStr)
        dataFile.write('\n')
    return

def loadTweetsData(screen_name):
    filePath = dataFilePathPrefix + screen_name[1:]
    tweetsJson = []

    dataFile = open(filePath, 'r')
    for line in dataFile:
        tweet = json.loads(line)
        tweetsJson.append(tweet)

    return tweetsJson

def dataFileExists(screen_name):
    #default @sceen_name -> dataFile_screen_name
    filePath = dataFilePathPrefix + screen_name[1:]
    return os.path.exists(filePath)

def updateUser(screen_name):
    print('updating user %s'.format(screen_name))
    if not dataFileExists(screen_name):
        initializeTweetsData(screen_name)
    lastLoggedId = getLastLoggedTweetId(screen_name)
    responseJson = getMoreTweets(screen_name, lastLoggedId)
    updateTweetsData(screen_name, responseJson)
    return;

def updateAll():
    print('updating all!')
    for user in users:
        updateuser(screen_name)
        time.sleep(delayBetweenUser) #wait 3 minutes
    return;

def initialize():
    print('Loading configuration')
    loadConfig(configFilePath)
    print('Loading users list')
    loadUsers(usersFilePath)
    print('Users list loaded {}'.format(users))
    print('Obtaining authentication')
    getBearerToken()
    print('Initialization complete')
    return

def main():
    initialize()
    while(True):
        updateAll()
        time.sleep(60*60*24/checksPerDay) #waits for 1.5 hours
    return
