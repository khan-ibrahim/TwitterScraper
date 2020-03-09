import time
import configparser
import requests
import os
import base64

usersFilePath = 'twitterScraper_usernames.txt'
configFilePath = 'twitterScraper_config.txt'

users = []
numRequestsMade = 0

# # TODO: make private?
consumer_api_key = None
consumer_secret_api_key = None
access_token = None

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
    bearerCredentials = \
    generateBearerCredentials(consumer_api_key, consumer_secret_api_key)

    # HTTP POST request to ouath2/token
    url = 'api.twitter.com/oauth2/token'
    headers = {}
    headers['Authorization': 'Basic ' + bearerCredentials]
    headers['Content-Type'] = r'application/x-www-form-urlencoded;charset=UTF-8'
    body = 'grant_type=client_credentials'

    r = requests.post(url, headers=headers, data=body)

    print(r)

    if not r.status_code == requests.codes.ok:
        print('ERROR requesting bearerToken')
        r.raise_for_status()
        exit(1)

    print(r.headers)

    if not r.headers['token_type'] == 'bearer':
        print('ERROR: Getting bearertoken: token_type invalid')
        print(r.headers)

        exit(1)

    access_token = r.headers['access_token']

    return access_token

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

    if since_id == None:
        # request as many as possible (omit count/since_id)
        print('Getting most tweets from %s'.format(screen_name))

        return
    else:
        # request tweets since since_id
        print('Getting tweets since %s'.format(since_id))
        return

    return

def updateTweetsData(screen_name, tweetsJson):
    return

def dataFileExists(screen_name):
    #default @sceen_name -> dataFile_screen_name
    filePath = dataFilePathPrefix + screen_name[1:]
    return os.path.exists(filePath)

def updateUser(screen_name):
    print('updating user %s'.format(screen_name))
    if not dataFileExists(screen_name):
        #create data file for user
        pass
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
    print('loading configuration')
    loadConfig(configFilePath)
    print('loading users list')
    loadUsers()
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
