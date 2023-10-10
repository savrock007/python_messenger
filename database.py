import sqlite3
class Database:
    def __init__(self,database_name):
        self.cursor , self.conn = self.create_connection(database_name)

        self.participates_last_primary_key = self.get_participates_primary_key()
        self.messages_last_primary_key = self.get_messages_primary_key()
        self.chatroom_last_primary_key = self.get_chatroom_primary_key()

    def get_participates_primary_key(self):
        self.cursor.execute('''
        SELECT participates_id FROM participates ORDER BY participates_id DESC''')

        try:
            num = (self.cursor.fetchone())[0]
        except:
            num = 0
        return num

    def get_messages_primary_key(self):
        self.cursor.execute('''
        SELECT message_id FROM message ORDER BY message_id DESC''')
        try:
            num = (self.cursor.fetchone())[0]
        except:
            num = 0
        return num

    def get_chatroom_primary_key(self):
        self.cursor.execute('''
        SELECT chatroom_id FROM chatroom ORDER BY chatroom_id DESC''')
        try:
            num = (self.cursor.fetchone())[0]
        except:
            num = 0
        return num

    def create_connection(self,db_file):
        conn = sqlite3.connect(db_file)
        #print(sqlite3.version)
        cur = conn.cursor()
        return cur, conn

    def create_tables(self):
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS user 
                        (username TEXT PRIMARY KEY, password_hash TEXT, status TEXT)

                        ''')
        self.conn.commit()

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS chatroom
                (chatroom_id INTEGER PRIMARY KEY, 
                chatroom_name TEXT)
                ''')
        self.conn.commit()

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS participates
        (participates_id INTEGER PRIMARY KEY,
        username TEXT,
        chatroom_id INTEGER,
        privilege TEXT,
        FOREIGN KEY (username) REFERENCES user (username),
        FOREIGN KEY (chatroom_id) REFERENCES chatroom (chatroom_id))
        ''')
        self.conn.commit()

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS message
        (message_id INTEGER PRIMARY KEY,
        chatroom_id INTEGER,
        username TEXT,
        text TEXT,
        FOREIGN KEY (chatroom_id) REFERENCES chatroom (chatroom_id),
        FOREIGN KEY (username) REFERENCES user (username))''')
        self.conn.commit()

    def insert_default_data(self):
        self.cursor.execute('''
            INSERT INTO user 
            (username , password_hash, status) 
            VALUES
            ('sasha','2-58322213.04334080437004082204813666200660448181008023814284400','active')
        ''')
        self.conn.commit()

        self.cursor.execute('''
            INSERT INTO user
            (username, password_hash, status)
            VALUES
            ('admin','0002881720081826242200724618224822840022840228260038104003003060', 'admin')
            ''')

        self.cursor.execute('''
           INSERT INTO user 
           (username , password_hash, status) 
           VALUES
           ('test_user1','2-58322213.04334080437004082204813666200660448181008023814284400','active')
           ''')
        self.conn.commit()

        self.cursor.execute('''
           INSERT INTO user 
           (username , password_hash, status) 
           VALUES
           ('test_user2','2-58322213.04334080437004082204813666200660448181008023814284400','offline')
           ''')
        self.conn.commit()

        self.cursor.execute('''
        INSERT INTO chatroom
        (chatroom_id,chatroom_name)
        VALUES
        (1,'maths')
        ''')
        self.conn.commit()

        self.cursor.execute('''
            INSERT INTO chatroom
            (chatroom_id,chatroom_name)
            VALUES
            (2,'phy')
            ''')

        self.conn.commit()

        self.cursor.execute('''
            INSERT INTO chatroom
            (chatroom_id,chatroom_name)
            VALUES
            (3,'music')
            ''')
        self.conn.commit()

        self.cursor.execute('''
        INSERT INTO participates
        (participates_id,username,chatroom_id,privilege)
        VALUES
        (1,'sasha',2,'admin')
        ''')
        self.conn.commit()

        self.cursor.execute('''
            INSERT INTO participates
            (participates_id,username,chatroom_id,privilege)
            VALUES
            (2,'test_user1',1,'participant')
            ''')
        self.conn.commit()

        self.cursor.execute('''
                    INSERT INTO participates
                    (participates_id,username,chatroom_id,privilege)
                    VALUES
                    (4,'test_user1',2,'participant')
                    ''')


        self.cursor.execute('''
            INSERT INTO participates
            (participates_id,username,chatroom_id,privilege)
            VALUES
            (3,'test_user2',1,'participant')
            ''')
        self.conn.commit()

        self.cursor.execute('''
        INSERT INTO message
        (message_id, chatroom_id, username,text)
        VALUES 
        (1, 1 , 'test_user1', 'hello this is check message in maths chatroom')
        ''')
        self.conn.commit()

        self.cursor.execute('''
            INSERT INTO message
            (message_id, chatroom_id, username,text)
            VALUES 
            (2, 1 , 'test_user2', 'hello this is check message2')
            ''')
        self.conn.commit()

        self.cursor.execute('''
            INSERT INTO message
            (message_id, chatroom_id, username,text)
            VALUES 
            (3, 2 , 'sasha', 'hello this is check message3')
            ''')
        self.conn.commit()

        self.cursor.execute('''
                INSERT INTO message
                (message_id, chatroom_id, username,text)
                VALUES 
                (4, 2 , 'test_user2', 'hello this is check message from masha in phy')
                ''')
        self.conn.commit()

    def check_user_exists(self,name):
        self.cursor.execute(f'''
        SELECT user.username, user.password_hash
        FROM user 
        WHERE username = '{name}'
        ''')
        list = []
        rows = self.cursor.fetchone()
        if rows != None:
            for row in rows:
                list.append(row)
            return list[0],list[1]

        elif rows == None:
            #print("Username doesn't exist")
            return None, None

    def check_chat_exists(self,chat_name):
        self.cursor.execute(f'''
        SELECT chatroom.chatroom_id
        FROM chatroom 
        WHERE chatroom.chatroom_name = '{chat_name}'
        ''')

        rows = self.cursor.fetchone()

        if rows != None:
            return True

        else:
            return False

    def get_chats_related_to_user(self,username):
        self.cursor.execute(f'''
        SELECT chatroom.chatroom_name 
        FROM chatroom , user , participates
        WHERE participates.username = user.username
        AND chatroom.chatroom_id = participates.chatroom_id
        AND user.username = "{username}" ''')

        list = []
        rows = self.cursor.fetchall()
        #print(rows)
        for row in rows:
            list.append(str(row)[2:-3])
        return list

    def get_messages_related_to_chat(self,chat):
        self.cursor.execute('''
        SELECT message.username , message.text
        FROM message , chatroom
        WHERE message.chatroom_id = chatroom.chatroom_id
        AND chatroom.chatroom_name = "{chatroom_name}" '''.format(chatroom_name = chat))
        list = []
        rows = self.cursor.fetchall()
        for row in rows:
            list.append(row)
        self.conn.commit()
        return list

    def add_user(self,username,password):
        self.cursor.execute(f'''
           INSERT INTO user 
           (username , password_hash, status) 
           VALUES
           ('{username}','{password}','offline')
           ''')
        self.conn.commit()

    def add_chat(self,chat_name):
        chatroom_id = int(self.chatroom_last_primary_key + 1)
        self.chatroom_last_primary_key += 1

        self.cursor.execute(f'''
            INSERT INTO chatroom
            (chatroom_id , chatroom_name)
            VALUES
            ({chatroom_id},'{chat_name}')
            ''')
        self.conn.commit()

    def add_participant_to_chat(self,chatroom_name,user):

        participates_id = int(self.participates_last_primary_key + 1)
        self.participates_last_primary_key += 1

        chatroom_id = self.get_chatroom_id(chatroom_name)

        self.cursor.execute(f'''
            INSERT INTO participates
            (participates_id , username , chatroom_id , privilege)
            VALUES
            ({participates_id},'{user}',{chatroom_id}, "participant")
            ''')

        self.conn.commit()



    def get_chatroom_id(self,chatroom_name):
        self.cursor.execute(f'''
            SELECT chatroom_id FROM chatroom
            WHERE chatroom.chatroom_name = "{chatroom_name}"
            ''')
        value = self.cursor.fetchone()
        if value != None:
            self.conn.commit()
            return int(value[0])

    def new_message(self,chatroom_name,username,text):
        message_id = self.messages_last_primary_key + 1
        self.messages_last_primary_key += 1

        chatroom_id = self.get_chatroom_id(chatroom_name)

        self.cursor.execute(f'''
        INSERT INTO message
                (message_id, chatroom_id, username,text)
                VALUES 
                ({message_id},{chatroom_id},"{username}","{text}")
        ''')
        #print("new message has been added")
        self.conn.commit()

    def get_list_of_users_in_chat(self,chatroom_name):
        chatroom_id = self.get_chatroom_id(chatroom_name)
        self.cursor.execute(f'''
        SELECT participates.username FROM participates WHERE chatroom_id = '{chatroom_id}' 
        ''')

        list = []
        rows = self.cursor.fetchall()
        for row in rows:
            list.append(row[0])

        self.conn.commit()
        return list

    def get_list_of_possible_usernames(self,username_to_find):

        self.cursor.execute(f'''
        SELECT user.username 
        FROM user
        WHERE username LIKE '{username_to_find}%'
        ''')

        list_of_usernames = ""
        rows = self.cursor.fetchall()
        for row in rows:
            list_of_usernames += str(row[0]) + ','

        self.conn.commit()
        return list_of_usernames


    def get_list_of_possible_chats(self,chat_to_find):

        self.cursor.execute(f'''
               SELECT chatroom.chatroom_name 
               FROM chatroom
               WHERE chatroom_name LIKE '{chat_to_find}%'
               ''')

        list_of_chats = ""
        rows = self.cursor.fetchall()
        for row in rows:
            list_of_chats += str(row[0]) + ','

        self.conn.commit()
        return list_of_chats


    def delete_user(self,user_to_delete):
        #print("BOOM")

        self.cursor.execute(f'''
                        DELETE FROM message
                        WHERE message.username = '{user_to_delete}'
                     ''')
        self.cursor.execute(f'''
                                DELETE FROM participates
                                WHERE participates.username = '{user_to_delete}'
                             ''')

        self.cursor.execute(f'''
                       DELETE FROM user
                       WHERE user.username = '{user_to_delete}'
                                      ''')
        self.conn.commit()

    def delete_chat(self,chat_to_delete):
        chatroom_id = self.get_chatroom_id(chat_to_delete)
        self.cursor.execute(f'''
                DELETE FROM message
                WHERE message.chatroom_id = {chatroom_id}
             ''')
        self.cursor.execute(f'''
                        DELETE FROM participates
                        WHERE participates.chatroom_id = {chatroom_id}
                     ''')

        self.cursor.execute(f'''
               DELETE FROM chatroom
               WHERE chatroom.chatroom_name = '{chat_to_delete}'
                              ''')

        #print("DONE")
        self.conn.commit()

#database = Database("messenger_database")

#database.create_tables()

#database.insert_default_data()
#print(database.get_messages_related_to_chat('test_chat_14'))
#print(database.get_messages_related_to_chat("phy"))