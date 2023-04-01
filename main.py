import sqlite3
import getpass
from datetime import date

connection = None
cursor = None

def create_db(path):
    '''
    Connect inputed database
    '''
    global connection, cursor 
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    return

def login_():
    '''
    Login Page for Users And Artits
    '''
    global connection, cursor
    user = input("ID: ")
    cursor.execute("SELECT uid from users WHERE uid like ?;",(user,)) 
    user_1 = cursor.fetchall()        
    cursor.execute("SELECT aid from artists WHERE aid like ?;",(user,))
    artist_1 = cursor.fetchall()
    if user_1 == [] and artist_1 == []:
            #if not in users and artists
            print("Incorrect ID!")
            login_()
    if user_1 != []:
            if user != [] and artist_1 == []:
                #if in user and not in artists
                pwd = getpass.getpass()
                cursor.execute("SELECT pwd from users WHERE uid = ?;",(user_1[0][0],))
                user_pwd = cursor.fetchall()
                if user_pwd[0][0] == pwd:  #check is password is right
                    print("Valid Password!\n")
                    user_login(user)
                else:
                    print("Incorrect password!")
                    login_()
    if artist_1 != [] and user_1 == []:
            #if in artist not in user
            pwd = getpass.getpass()
            cursor.execute("SELECT pwd from artists WHERE aid = ?;",(artist_1[0][0],))
            artist_pwd = cursor.fetchall()
            if pwd == artist_pwd[0][0]:  #check if password is right
                print("Valid Password!\n")
                artists_login(user)
            else:
                print("Incorrect password!")
                login_()

    if user_1 != [] and artist_1 != []:
            #if in user and artist
            print("Your ID has matched with Users and Artists!")
            choice  = input("Login as User(U) or Artist(A): ")
            while choice.lower() not in ['u','a']:
                print("Incorrect choice!")
                choice  = input("Login as User(U) or Artist(A): ")
            if choice.lower() == "u":
                pwd = getpass.getpass()
                cursor.execute("SELECT pwd from users WHERE uid = ?;",(user_1[0][0],))
                user_pwd = cursor.fetchall()
                if pwd == user_pwd[0][0]:  #check if password is right
                    print("Valid Password!\n")
                    user_login(user)
                else:
                    print("Incorrect Password!")
                    login_()
            if choice.lower() == "a":
                pwd = getpass.getpass()
                cursor.execute("SELECT pwd from artists WHERE aid = ?;",(artist_1[0][0],))
                artist_pwd = cursor.fetchall()
                if pwd == artist_pwd[0][0]:  #check if password is right
                    print("Valid Password!\n")
                    artists_login(user)
                else:
                    print("Incorrect Password")
                    login_()
                
        

def user_login(user):
    '''
    User Login
    user parameter is the current users uid.
    The user is prompted with 5 different choices each corresponding to an if statement.
    '''
    global connection, cursor
    print("Welcome User!")
    quit = False
    while quit == False:
        choice = input("Choose what you want to do: Start a session(1) or Search for songs and playlists(2) or Search for artists(3) or End the Session(4) or Logout(5): ")
        while choice not in ['1','2','3','4','5'] or choice == '': #error checking if user doesn't input anything or wrong number
            choice = input("Choose what you want to do: Start a session(1) or Search for songs and playlists(2) or Search for artists(3) or End the Session(4) or Logout(5): ")
        print()
        if choice == '1':
            #In order to start a new session you require the uid, session number, start time and end time.
            uid = user #The uid of the user. Will use to start new session
            startDate = date.today() #This will return the current date
            endDate = None #Setting the end date to none because the user has yet to end the session. Option number 4 handles this
            cursor.execute(""" SELECT DISTINCT sessions.sno
                                FROM sessions, users
                                WHERE sessions.uid =:uid
                                ORDER BY sessions.sno
                                """,{"uid":uid})
            sno = cursor.fetchall() #Getting all the sessions that have been started by this user.
            ListOfSessionNumbers = []
            for number in sno:
                ListOfSessionNumbers.append(number[0]) #Appending all the sno started by this user to a list.
            LengthOfSessions = len(ListOfSessionNumbers)
            last = ListOfSessionNumbers[-1]
            if LengthOfSessions > 0: #If the list is not empty
                NewSno = last + 1 #Add one to the last sno to get a new unique one.
            else:
                NewSno = 1 #If this user has not made any sessions then we will just assign sno to 1.
            cursor.execute("INSERT INTO sessions(uid, sno, start, end) VALUES(?,?,?,?)",(uid,NewSno,startDate,endDate)) #Inserting in the new session
            print("A new Session has been Started! The following information was used to create your session:")
            print("Uid: ",uid)
            print("Sno: ",NewSno)
            print("Start Date: ",startDate)
            print("End Date: ", endDate)

        if choice == '2':
            keywords = input("What songs or playlists are you looking for (provide one or more unique keywords)?: ") #Asking the user for input.
            #The following query does the following: It will find the songs that contain the keywords the user entered and return the songs sid, title and duration.
            cursor.execute("""  SELECT "Song:",songs.sid, songs.title, songs.duration
                                FROM plinclude
                                INNER JOIN playlists
                                on playlists.pid = plinclude.pid
                                INNER JOIN songs
                                on songs.sid = plinclude.sid
                                WHERE songs.title LIKE  ?
                                GROUP BY songs.title 
                                ORDER BY count(songs.title LIKE ?) DESC; """,('%'+keywords+'%','%'+keywords+'%',)) #The order by makes sure that the one with the most keyword matches are first.
            song_name = cursor.fetchall()
            
            #The following query does the following: It will find the playlists that contain the keywords the user entered and return the playlists pid, title and duration of all the songs in the playlist.
            cursor.execute("""  SELECT DISTINCT "Playlist:",playlists.pid,playlists.title,playlists.uid
                                FROM playlists,plinclude,users
                                WHERE playlists.pid = plinclude.pid
                                AND playlists.uid = users.uid
                                AND playlists.title LIKE ?
                                GROUP BY playlists.pid
                                ORDER BY count(playlists.title LIKE ?) DESC; """,('%'+keywords+'%','%'+keywords+'%',)) #The order by ensures that the titles with the most keyword matches shows up first. 
            playlistName = cursor.fetchall()
            allResults = song_name + playlistName #Adding the results from both queries because we want to output both songs and playlists.
            numberOfResults = len(allResults) #Getting the number of results

            if numberOfResults <= 5: #If the number of results are less than five we will simply just ouput the results that are there. 
                y = 1
                z = 0 #Keep track of number of the number of results being printed.
                for x in allResults:
                    print(str(y) + ". " + str(x[0]) + "|" + str(x[1]) + "|" + str(x[2]))
                    y += 1
                    z += 1
                info_or_more = input("Would you like to select one of the songs listed above for more info(1) or return to user login page, if there are no songs(3)?:")

            if numberOfResults > 5: #If the results are greater than 5.
                y = 1
                z = 0
                for x in allResults:
                    print(str(y) + ". " + str(x[0]) + "|" + str(x[1]) + "|" + str(x[2]))
                    y += 1
                    z += 1
                    if (z % 5) == 0 and z != numberOfResults: #To print only 5 at a time
                        info_or_more = input("Would you like to select one of the songs listed above for more info(1) or view rest of the matches(2)?: ")
                        if info_or_more == '1':
                            print()
                            break
                        if info_or_more == '2':
                            print()
                            pass
                    if z == numberOfResults:#Thereare no more results remaining
                        info_or_more = input("No more results, would you like to select one of the songs listed above for more info(1)?: ")
                        print()
                        break
            if info_or_more == '1': #If user wants more information about a song that was listed
                    info = input("Input the song name from above that you would like more information about: ")
                    cursor.execute("""  SELECT songs.sid, songs.title,songs.duration,artists.name
                                        from songs, perform, artists
                                        where perform.aid = artists.aid
                                        and perform.sid = songs.sid
                                        and songs.title like ?;""",('%'+info+'%',))
                    song_info = cursor.fetchall()
                    if song_info == []:
                        print("No such song, try again!\n")
                        user_login(user)
                    for x in song_info:
                        print(str(x[0])+ '|' + str(x[1]) + '|' + str(x[2])+ '|' + str(x[3]))
                    song = input("Enter the song sid you would you like to select: ")
                    artists_songaction(song,user,NewSno)
                    quit = True
            if info_or_more == '3':
                quit = True

        if choice == '3':
            artistname = input("What artist or song are you looking for(provide one or more unique keywords)?: ")
            cursor.execute("""  SELECT a.name, a.nationality, count(p.aid)
                                from artists a, perform p
                                where a.name LIKE ?
                                and p.aid = a.aid
                                group by a.name, a.nationality
                                ORDER by count(a.name LIKE ? ) DESC;""",('%'+artistname+'%','%'+artistname+'%',))
            artist_name = cursor.fetchall()
            cursor.execute(""" SELECT a.name, a.nationality,count(p.aid)
                                from artists a, perform p, songs s
                                where p.aid = a.aid
                                and p.sid = s.sid
                                and s.title like ?
                                GROUP by  a.name, a.nationality
                                ORDER by (s.title like ?) DESC;""",('%'+artistname+'%','%'+artistname+'%',))
            song_name = cursor.fetchall()
            number_of_artists = len(artist_name)   #length of both, so the largest length gets printed
            number_of_songs = len(song_name)
            if number_of_artists >= number_of_songs:
                # if number of matched artists is greater than matched song
                if number_of_artists > 5:
                        y = 1
                        z = 0 # keeps track of number of selected attributes being printed
                        for x in artist_name:
                            print(str(y) + ". " + str(x[0]) + "|" + str(x[1]) + "|" + str(x[2]))      
                            y +=1
                            z += 1
                            if (z % 5) == 0 and z != number_of_artists:  
                                # for the paginated downward format
                                info_or_more = input("Would you like to select artist listed above for more info(1) or view rest of the matches(2)?: ")
                                if info_or_more == '1':
                                    print()
                                    break
                                if info_or_more == '2':
                                    print()
                                    pass
                            if z == number_of_artists:
                                info_or_more = input("No more results, would you like to select artist listed above for more info(1)?: ")
                                print()
                                break
                if number_of_artists <= 5:
                        y = 1
                        for x in artist_name:
                            print(str(y) + ". " + str(x[0]) + "|" + str(x[1]) + "|" + str(x[2]))
                            y += 1
                        info_or_more = input("Would you like to select artist listed above for more info(1)?: ")
                if info_or_more == '1':
                        info = input("Input the artist name from above that you would like more information about: ")
                        cursor.execute("""  SELECT songs.sid,title,duration
                                            from songs, perform, artists
                                            where perform.aid = artists.aid
                                            and perform.sid = songs.sid
                                            and artists.name like ?;""",(info,))
                        artist_info = cursor.fetchall()
                        if artist_info == []:  #error checking in case user enters artist thats not in database
                            print("No such artist, try again!\n")
                            
                        for x in artist_info:
                            print(str(x[0])+ '|' + str(x[1]) + '|' + str(x[2]))
                        song = input("Enter the song sid you would you like to select: ")
                        artists_songaction(song,user,NewSno)
                        quit = True

            if number_of_songs > number_of_artists:
                # if number of matched songs is greater than matched artists
                if number_of_songs > 5:
                    y = 1
                    z = 0
                    for x in song_name:
                        print(str(y) + ". " + str(x[0]) + "|" + str(x[1]) + "|" + str(x[2]))      
                        y +=1
                        z += 1  #keeps track that 5 attributes are being printed
                        if (z % 5) == 0 and z != number_of_songs: 
                            # produces a downward paginated format
                            info_or_more = input("Would you like to select artist for more info(1) or view rest of the matches(2)?: ")
                            if info_or_more == '1':
                                print()
                                break
                            if info_or_more == '2':
                                print()
                                pass
                        if z == number_of_songs:
                                info_or_more = input("No more results, would you like to select artist for more info(1)?: ")
                                print()
                                break
                if number_of_songs <= 5:
                    y = 1
                    for x in artist_name:
                        print(str(y) + ". " + str(x[0]) + "|" + str(x[1]) + "|" + str(x[2]))
                        y += 1
                        info_or_more = input("Would you like to select artist for more info(1)?: ")
                if info_or_more == '1':
                    info = input("Input the artist name that you would like more information about: ")
                    cursor.execute("""  SELECT songs.sid,title,duration
                                            from songs, perform, artists
                                            where perform.aid = artists.aid
                                            and perform.sid = songs.sid
                                            and artists.name like ?;""",(info,))
                    artist_info = cursor.fetchall()
                    for x in artist_info:
                        print(str(x[0])+ '|' + str(x[1]) + '|' + str(x[2]))
                    song = input("Enter the song sid you would you like to select: ")
                    artists_songaction(song,user,NewSno)
                    quit = True

            if choice == '4':
                endDate = startDate #Now the end date has been set to the start date.
                cursor.execute(""" UPDATE sessions
                                SET end = ?
                                WHERE sessions.sno = ?
                                AND sessions.uid = ?        
                                """,(endDate,NewSno,uid))
                print("The Session has successfully been ended")
                quit = True

            if choice == '5':
                quit = True
                mainlogin()
                
def artists_songaction(song,user,NewSno):
    '''
    The parameter song is the sid for the song the user selected
    The user parameter is the uid for the user
    The parameter NewSno is the session number of the current session.
    '''
    actions = input("Would you like to listen to this song(1) or view more information about it(2) or add it to a playlist(3): ")
    if actions == "1":
        #the listen sng action has some bugs in it. 
        #Overall our approach was to query the listen table withthe sno,sid and uid. If the result was empty we would attempt to start a new session
        # and then set the cnt to 1. Otherwise we would find the cnt and add one to it.
        print("We will now start a new listening event within the current session")
        cursor.execute(""" SELECT songs.title,listen.sid, listen.uid,listen.sno,listen.cnt
                            FROM songs,sessions,listen
                            WHERE sessions.sno = listen.sno
                            AND listen.uid = sessions.uid
                            AND listen.sid = songs.sid
                            AND sessions.sno = ?
                            AND songs.sid = ?
                            AND listen.uid = ?;""",(NewSno,song,user))
        listen = cursor.fetchall()
        if listen == []:
            cnt = 1
            cursor.execute("INSERT INTO listen(uid,sno,sid,cnt) VALUES(?,?,?,?)",(user,NewSno,song,cnt))
        else:
            cursor.execute(""" SELECT listen.cnt
                            FROM songs,sessions,listen
                            WHERE sessions.sno = listen.sno
                            AND listen.uid = sessions.uid
                            AND listen.sid = songs.sid
                            AND sessions.sno = ?
                            AND songs.sid = ?
                            AND listen.uid = ?;""",(NewSno,song,user))
            oldCnt = cursor.fetchall()
            oldCnt += 1
            cursor.execute(""" UPDATE listen
                                SET cnt = ?
                                WHERE listen.sno = ?
                                AND listen.uid = ?;""",(oldCnt,NewSno,user))
    if actions == "2":
        cursor.execute(""" select DISTINCT artists.name, songs.sid, songs.duration,playlists.title
                            from artists, perform,songs, plinclude,playlists
                            where songs.sid = perform.sid
                            and artists.aid = perform.aid
                            and songs.sid = plinclude.sid
                            and playlists.pid = plinclude.pid
                            and plinclude.sid = ?;""",(song,))
        playlist = cursor.fetchall()
        if playlist == []:
            print("This song does not belong to any playlist!")
            cursor.execute("""select artists.name, songs.sid, songs.duration
                                from artists, perform,songs
                                where songs.sid = perform.sid
                                and artists.aid = perform.aid
                                and songs.sid = ?;""",(song,))
            no_playlist = cursor.fetchall()
            for x in no_playlist:
                print(str(x[0])+ '|' + str(x[1]) + '|' + str(x[2]))
        else:
            for x in playlist:
                print(str(x[0])+ '|' + str(x[1]) + '|' + str(x[2]) + '|' + str(x[3]))
        print()
    if actions == "3":
        cursor.execute(""" select users.uid, playlists.title
                            from playlists, users
                            where users.uid = playlists.uid
                            and users.uid like ?""",(user,))
        existing_playlist = cursor.fetchall()
        playlist_choice = input("Would you like to add song to an existing playlist(1) or create a new one(2): ")
        while playlist_choice not in ['1', '2']:
            playlist_choice = input("Would you like to add song to an existing playlist(1) or create a new one(2): ")
        if playlist_choice == '2':
            new_title = input("What is the playlist name you would like to create: ")
            cursor.execute("SELECT count(distinct pid) from playlists")
            pid = cursor.fetchone()
            pid = pid[0] + 1 #giving unqiue pid 
            sorder = 1
            cursor.execute("INSERT INTO playlists VALUES(?,?,?)",(pid,new_title,user))
            cursor.execute("INSERT INTO plinclude VALUES(?,?,?)",(pid,song,sorder))
            connection.commit()
            print("Playlist succesfully created!\n")
        if playlist_choice == '1':
            if existing_playlist != []:
                print("You have existing playlists!")
                for x in existing_playlist:
                    print(str(x[1]))
            playlist = input("What playlist would like the song to be in: ")
            songin = True
            while songin:
                cursor.execute("""SELECT playlists.title 
                                        from playlists, plinclude
                                        where plinclude.pid = playlists.pid
                                        and plinclude.sid = ?;""",(song,))
                titles = cursor.fetchall()
                if playlist in titles:
                    print("this song is already in the playlist!")
                    playlist = input("What playlist would like the song to be in: ")
                if playlist not in titles:
                    songin = False
            cursor.execute("SELECT pid from playlists where title like ?;",(playlist,))
            pid = cursor.fetchone()
            cursor.execute("SELECT count(distinct sorder) from plinclude where pid = ?;",(pid[0],))
            sorder = cursor.fetchone()
            sorder = sorder[0] + 1
            cursor.execute("INSERT INTO plinclude VALUES(?,?,?)",(pid[0],song,sorder,))
            connection.commit()
            print("Successfully added song to playlist!\n")




def artists_login(user):
    """
    Artist Login
    """
    global connection,cursor
    aid = user
    print("Welcome Artists!")
    choice = input("Choose what you want to do: Add a song(1) or Find top fans and playlists(2) or Logout(3): ")
    if choice == '1':
        song = input("Song Title: ")
        duration = input("Song duration: ")
        cursor.execute("SELECT title, duration FROM songs WHERE title = ? and duration = ?;",(song,duration,))
        data = cursor.fetchall()
        if data == []: #if title and duration is distinct
            cursor.execute("SELECT count(distinct sid) from songs")
            sid = cursor.fetchone()
            sid = sid[0] + 1  #giving unique sid
            cursor.execute("INSERT INTO songs(sid,title,duration) VALUES(?,?,?)",(sid,song,duration))
            cursor.execute("INSERT INTO perform(aid,sid) VALUES(?,?)",(aid,sid))
            connection.commit()
            artists_login(aid) # going back to artist login
        if data != []:
            if song == data[0][0]:
                print("This song is already added!")
                artists_login(aid)
    if choice == '2':
        print("The top 3 users/names are:")
        cursor.execute(""" SELECT DISTINCT u.uid, u.name
                            from users u, listen l, perform p, songs s
                            where l.uid = u.uid
                            and s.sid = p.sid
                            and p.sid = l.sid
                            and p.aid = ?
                            group by u.uid, u.name
                            order by sum(duration*cnt) DESC
                            limit 3;""",(aid,))
        users = cursor.fetchall()
        for i in users:
            print(i)
        print()
        print("The top 3 playlists that include the largest number of their songs: ")
        cursor.execute(""" select plinclude.pid, playlists.title
        from plinclude, playlists, perform
        where plinclude.pid = playlists.pid
        and perform.sid = plinclude.sid
        and perform.aid = ?
        GROUP by plinclude.pid, playlists.title
        ORDER by count(perform.sid) DESC
        limit 3;""",(aid,))
        playlists = cursor.fetchall()
        for i in playlists:
            print(i)
        artists_login(aid)
    if choice == '3':
        print("Succesfully Logged Out... You will be redirected to the main page!\n")
        mainlogin() #going back to main login screen

def sign_up():
    '''
    Creating a new user 
    '''
    global connection, cursor
    print("Sign up\n")
    name = input("Name: ")
    uid = input("Unique uid: ")
    pwd = getpass.getpass()
    cursor.execute("SELECT uid from users WHERE uid = ?;",(uid,))
    unique_uid = cursor.fetchall()
    if unique_uid != []:
        while uid == unique_uid[0][0]:
            print("This uid already exists!\n")
            name = input("Name: ")
            uid = input("Unique uid: ")
            pwd = getpass.getpass()
    cursor.execute("INSERT INTO users(uid,name,pwd) VALUES(?,?,?)",(uid,name,pwd))
    connection.commit()
    print("Succesfully Signed Up!")
    user_login()

def mainlogin():
    '''
    Main Screen
    '''
    exit = False 
    print("Welcome to the Main page!")
    while not exit:
        login = input("Input Login(1) or Signup(2) or Exit(3): ")
        while login not in ["1","2","3","4"]:
            print("Input not valid!")
            login = input("Input Login(1) or Signup(2) or Exit(3): ")
        if login == '1':
            exit = True
            login_()
        elif login == '2':
            exit = True
            sign_up()
        elif login == '3':
            print("Successfully exited the program!")
            exit = True


def main():
    global connection, cursor
    path = input("Insert filename: ")
    while path == " ":
        print("No file entered!")
        path = input("Insert filename: ")
    create_db(path)
    mainlogin()
            

if __name__ == '__main__':
    main()

