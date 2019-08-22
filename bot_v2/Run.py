import string
import time
import math
import urllib.request
from urllib.request import urlopen
from json import loads
from Socket import openSocket, sendMessage
from Initialize import joinRoom
from Read import getUser, getMessage
from Settings import CHANNEL, COOLDOWN, IDENT, CHANNELPASS, SRC_USERNAME, GAMES, CATEGORIES


#Returns the world record for the category that's written in the stream title
def worldRecord(input):
    if input == message.lower().strip():
        #Get the stream title from the Twitch API
        try:
            response = urlopen('https://api.twitch.tv/kraken/channels/{}?oauth_token={}'.format(CHANNEL, CHANNELPASS.strip('oauth:')))
        except urllib.error.HTTPError as err:
            sendMessage(s, "Error: Invalid CHANNEL/CHANNELPASS in settings file")
            cooldown()
            return
        readable = response.read().decode('utf-8')
        lst = loads(readable)
        title = lst['status'].lower()
        game = None

        for i in range(len(GAMES)):
            if GAMES[i][0].lower() in title:
                game = GAMES[i][1]
                platform = GAMES[i][3]
                break

        category = None
        category_title = None
        for i in range(len(CATEGORIES)):
            if CATEGORIES[i][0].lower() in title:
                category = CATEGORIES[i][1]
                category_title = CATEGORIES[i][0]
                break

        if game == None:
            sendMessage(s, "No game and/or category detected in stream title.")
            cooldown()
            return

        if category != None:
            response = urlopen('https://www.speedrun.com/api/v1/leaderboards/{}/category/{}?top=1&embed=players&platform={}'.format(game, category, platform))
            readable = response.read().decode('utf-8')
            lst = loads(readable)
            runner = lst['data']['players']['data'][0]['names']['international']
            time_in_sec = int(lst['data']['runs'][0]['run']['times']['realtime_t'])
            hours = divmod(time_in_sec, 3600)
            minutes = divmod(hours[1], 60)
            seconds = minutes[1]
            wr = ''
            if hours[0] > 0:
                wr = str(hours[0]) + (" hour " if hours[0] == 1 else " hours ") + str(minutes[0]) + " min " + str(seconds) + " sec "
            elif minutes[0] > 0:
                wr = str(minutes[0]) + " min " + str(seconds) + " sec "
            else:
                wr = str(seconds) + " sec "

            sendMessage(s, "The " + category_title + " world record is " + wr + "by " + runner + ".")
            cooldown()
            return

        elif category == None:
            sendMessage(s, "No game and/or category detected in stream title.")
            cooldown()
            return

#Returns the channel owner's personal best time for the category that's written in the stream title
def personalBest(input):
    if input == message.lower().strip():
        #Get the stream title from the Twitch API
        try:
            response = urlopen('https://api.twitch.tv/kraken/channels/{}?oauth_token={}'.format(CHANNEL, CHANNELPASS.strip('oauth:')))
        except urllib.error.HTTPError as err:
            sendMessage(s, "Error: Invalid CHANNEL/CHANNELPASS in settings file")
            cooldown()
            return
        readable = response.read().decode('utf-8')
        lst = loads(readable)
        title = lst['status'].lower()

        game_title = None
        for i in range(len(GAMES)):
            if GAMES[i][0].lower() in title:
                game_title = GAMES[i][0].lower()
                platform_title = GAMES[i][2]
                break

        category_title = None
        for i in range(len(CATEGORIES)):
            if CATEGORIES[i][0].lower() in title:
                category_title = CATEGORIES[i][0]
                break

        if game_title == None:
            sendMessage(s, "No game and/or category detected in stream title.")
            cooldown()
            return

        if category_title != None:
            response = urlopen('https://www.speedrun.com/api/v1/users/{}/personal-bests?embed=category,game,platform'.format(SRC_USERNAME))
            readable = response.read().decode('utf-8')
            lst = loads(readable)

            place = None
            time_in_sec = None
            for cat in lst['data']:
                if cat['category']['data']['name'] == category_title and cat['game']['data']['names']['international'].lower() == game_title and cat['platform']['data']['name'] == platform_title:
                    time_in_sec = int(cat['run']['times']['realtime_t'])
                    place = cat['place']
                    break

            if place == None:
                sendMessage(s, CHANNEL.title() + " currently has no " + category_title + " PB on the leaderboard.")
                cooldown()
                return

            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

            hours = divmod(time_in_sec, 3600)
            minutes = divmod(hours[1], 60)
            seconds = minutes[1]
            pb = ''
            if hours[0] > 0:
                pb = str(hours[0]) + (" hour " if hours[0] == 1 else " hours ") + str(minutes[0]) + " min " + str(seconds) + " sec"
            elif minutes[0] > 0:
                pb = str(minutes[0]) + " min " + str(seconds) + " sec"
            else:
                pb = str(seconds) + " sec"

            sendMessage(s, CHANNEL.title() + "\'s " + category_title + " PB is " + pb + " (" + ordinal(place) + " place).")
            cooldown()

        elif category_title == None:
            sendMessage(s, "No game and/or category detected in stream title.")
            cooldown()
            return


#Returns a kadgar.net link with the channel owner and the other racers if a race is happening
def raceCommand(input):
    if input == message.lower().strip():
        #Get the stream title from the Twitch API
        try:
            response = urlopen('https://api.twitch.tv/kraken/channels/{}?oauth_token={}'.format(CHANNEL, CHANNELPASS.strip('oauth:')))
        except urllib.error.HTTPError as err:
            sendMessage(s, "Error: Invalid CHANNEL/CHANNELPASS in settings file")
            cooldown()
            return
        readable = response.read().decode('utf-8')
        lst = loads(readable)
        title = lst['status'].lower()

        if 'race with' in title:
            pass
        elif 'race with' not in title:
            sendMessage(s, CHANNEL.title() + " is not currently racing or no racers detected in stream title.")
            cooldown()
            return

        title_list = title.split()
        r = title_list.index('with') + 1
        contenders = []
        length = len(title_list)
        diff = length - r
        while True:
            contenders.append(title_list[r].strip(','))
            diff = diff - 1
            r = r + 1
            if diff == 0:
                break


        sendMessage(s, "Race link: http://kadgar.net/live" + CHANNEL + "/" + "/".join(contenders))
        cooldown()


#Displays commands
def getCommands(input):
    if input == message.strip().lower():
        sendMessage(s, 'Commands: !wr • !pb • !race')
        cooldown()


#Global cooldown
def cooldown():
    if user == CHANNEL:
        pass
    elif user:
        abort_after = COOLDOWN
        start = time.time()
        while True:
            delta = time.time() - start
            if delta >= abort_after:
                break


#Checks if a message is from Twitch or a user
def Console(line):
    if "PRIVMSG" in line:
        return False
    else:
        return True


#Quits the bot program
def quitCommand(input):
    if input == message.strip().lower() and user == CHANNEL:
        sendMessage(s, "[Disconnected]")
        quit()
    elif input == message.strip():
        sendMessage(s, "@" + user.title() + " Only the channel owner may use the !kill command.")
        cooldown()


s = openSocket()
joinRoom(s)
readbuffer = ""

while True:

    readbuffer = s.recv(1024)
    readbuffer = readbuffer.decode()
    temp = readbuffer.split("\n")
    readbuffer = readbuffer.encode()
    readbuffer = temp.pop()


    for line in temp:
        print(line)
        if "PING" in line and Console(line):
            msgg = "PONG tmi.twitch.tv\r\n".encode()
            s.send(msgg)
            print(msgg)
            break
        user = getUser(line)
        message = getMessage(line)
        print(user + " said: " + message)

        response = urlopen('https://tmi.twitch.tv/group/user/{}/chatters'.format(CHANNEL))
        readable = response.read().decode('utf-8')
        chatlist = loads(readable)
        chatters = chatlist['chatters']
        moderators = chatters['moderators']
        vips = chatters['vips']
        viewers = chatters['viewers']


        getCommands('!commands')
        worldRecord('!wr')
        personalBest('!pb')
        raceCommand('!race')
        quitCommand('!kill')
        continue
