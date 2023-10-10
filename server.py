import socket
import sys
import threading
import rsa
from encryption import *
from database import *




class Server():
    def __init__(self):
        self.client_n_key = []
        self.client_n_username = []

        # attributes required for file transfers

        self.receive_file_flag = False
        self.file_name_to_receive = ''
        self.ready_to_receive_file_data = False



    def exchange_keys(self, conn):
        e, d, n = rsa.generateKeys(32)
        PublicKey = [e, n]
        PrivateKey = [d, n]

        ############FIRST STAGE################

        print("sending Public Key...: ",str(PublicKey),"\n")
        conn.send(("PK" + str(PublicKey)).encode())

        ###########SECOND STAGE#################
        try:
            print("Receiving Sym Key...")
            data = conn.recv(2024).decode()
            if data[0:2] == "SK":
                data = data[2:]
                Sym_Key = rsa.decrypt(PrivateKey, data)
                print("Sym_Key received: ",Sym_Key)

                conn.send((encryption.encrypt_sym("ACK", Sym_Key).encode())) #sending ACK signal
                print("Exchange successfully")
                self.client_n_key.append([conn, Sym_Key])
        except:
            print("Something went wrong, deleting connection", sys.exc_info())
            conn.close()

    def recieve_requests(self, client):
        while True:
            if not self.receive_file_flag:           # treat incoming data as command
                cipher = client[0].recv(2048).decode()
                request = encryption.decrypt_sym(cipher, client[1])
                if request != "":
                    self.handle_request(request, client)
                else:
                    print("broken pipe deleting client from the list")
                    client[0].close()
                    self.client_n_key.remove(client)

                    for client_with_username in self.client_n_username:
                        if client in client_with_username:
                            self.client_n_username.remove(client_with_username)
                    break

            elif self.receive_file_flag:              # elif to treat incoming data as a file not command


                with open(self.file_name_to_receive, "wb") as f:
                    while True:
                        bytes_read = client[0].recv(1024)
                        print(bytes_read)
                        if bytes_read[-4:] == b"DONE":
                            bytes_read = bytes_read[:-4]
                            break
                        f.write(bytes_read)
                        #print("writen")
                    f.write(bytes_read)
                    f.close()
                print("receiving finished")

                self.receive_file_flag = False



                self.broadcast_file(self.file_name_to_receive,self.tmp_chatroom_where_file_sent,self.tmp_sender_of_a_file)

                self.broadcast(self.tmp_sender_of_a_file, self.tmp_chatroom_where_file_sent, "sent a file")




                # setting temporary attributes back to default

                self.file_name_to_receive = ''
                self.tmp_chatroom_where_file_sent = ''
                self.tmp_sender_of_a_file = ''

    def handle_request(self, request, client):
        request = request.split('|')

        command = request[0]
        request.pop(0)

        print('command: ', command)
        print('data: ', request)

        if command == "LOGIN":
            self.login_user(request,client)


        elif command == "SEND_STARTUP_DATA":
           self.send_starting_data(request[0], client)

        elif command == 'REG':
            self.register_new_user(request,client)


        elif command == 'SEND TEXT':
            self.send_text(request,client)

        elif command == "SEND TEXT NS":
            self.send_text_without_saving(request, client)


        elif command == 'SEARCH USERNAME':
            username_to_be_searched = request[0]

            list_of_found_usernames = self.search_usernames(username_to_be_searched)

            client[0].send(encryption.encrypt_sym("FOUND USERNAMES"+ "|" + list_of_found_usernames, client[1]).encode())
            #print('list of usernames sent')

        elif command == 'CREATE NEW CHAT':
            chat_name = request[0]
            users_list = request[1].split(",")

            database = Database("messenger_database")

            if database.check_chat_exists(chat_name) == False:

                self.create_new_chat(chat_name)

                self.add_users_to_chat(chat_name,users_list)

                self.broadcast_new_chat(chat_name,users_list[-1])

                msg = "CHAT CREATE OK|"
                client[0].send(encryption.encrypt_sym(msg, client[1]).encode())
            elif database.check_chat_exists(chat_name) == True:
                msg = "CHAT CREATE FAILED|"
                client[0].send(encryption.encrypt_sym(msg, client[1]).encode())
                print("CHAT CREATE FAILED SENT")

        elif command == "SEARCH CHAT":
            chat_to_be_searched = request[0]

            list_of_found_chats = self.search_chat(chat_to_be_searched)

            client[0].send(
                encryption.encrypt_sym("FOUND CHATS" + "|" + list_of_found_chats, client[1]).encode())
            print('list of usernames sent')

        elif command == 'DELETE USER':
            user_to_delete = request[0]
            if self.delete_user(user_to_delete) == True:
                msg = "DELETE USER OK" + "|" + user_to_delete
                client[0].send(encryption.encrypt_sym(msg, client[1]).encode())

        elif command == 'DELETE CHAT':
            chat_to_delete = request[0]
            if self.delete_chat(chat_to_delete) == True:
                msg = "DELETE CHAT OK" + "|" + chat_to_delete
                client[0].send(encryption.encrypt_sym(msg, client[1]).encode())

        elif command == "READY TO RECEIVE FILE DATA":
            self.ready_to_receive_file_data = True

        elif command == "PREPARE TO RECEIVE FILE":
            request = request[0].split(",")
            file_name = request[0]
            #print("file name in command mode: ",file_name)
            sender = request[1]
            chatroom_name = request[2]

            self.receive_file_flag = True
            self.file_name_to_receive = file_name
            self.tmp_sender_of_a_file = sender
            self.tmp_chatroom_where_file_sent = chatroom_name

    def broadcast(self, sender_username, chatroom, text):
        database = Database('messenger_database')

        list_of_users_in_the_same_chat = database.get_list_of_users_in_chat(chatroom)


        for client_with_username in self.client_n_username:
            username = client_with_username[0]
            client = client_with_username[1]
            if username in list_of_users_in_the_same_chat:
                msg = "NEW MESSAGE|" + sender_username + ',' + chatroom + ',' + text

                client[0].send(encryption.encrypt_sym(msg, client[1]).encode())

    def broadcast_file(self,file_name,chatroom,sender):
        database = Database('messenger_database')
        list_of_users_in_the_same_chat = database.get_list_of_users_in_chat(chatroom)
        list_of_users_in_the_same_chat.remove(sender)

        for client_with_username in self.client_n_username:
            username = client_with_username[0]
            client = client_with_username[1]

            if username in list_of_users_in_the_same_chat:
                #print('sending to: ', username)
                self.send_file(file_name,client)



    def send_file_transfer_warning(self,file_name,client):
        msg = str("PREPARE TO RECEIVE FILE" + "|" + file_name)

        client[0].send(encryption.encrypt_sym(msg, client[1]).encode())


    def send_file(self,file_name,client):

        self.send_file_transfer_warning(file_name,client)

        while True:

            if self.ready_to_receive_file_data == True:
                with open(file_name, "rb") as f:
                    #print('file name right before sending file: ',file_name)
                    while True:
                        bytes_read = f.read(1024)
                        #print('sending bytes:',bytes_read)
                        if not bytes_read:
                            break
                        client[0].sendall(bytes_read)

                    print("all bytes sent")
                    client[0].send(b"DONE")
                f.close()
                break

    def send_starting_data(self, username, client):

        self.client_n_username.append([username, client])

        #print('client_n_username: ', self.client_n_username)
        msg = "CHATS|"
        database = Database('messenger_database')
        data_chats = database.get_chats_related_to_user(username)

        for chat in data_chats:
            data_messages = str(database.get_messages_related_to_chat(chat))
            data_messages = data_messages[1:-1]
            msg += "--" + chat + ":" + data_messages

            #print(msg)

        client[0].send(encryption.encrypt_sym(msg, client[1]).encode())

    def try_login(self, username, password):
        database = Database('messenger_database')
        username_from_database, password_from_database = database.check_user_exists(username)
        if username_from_database == 'admin':
            return "admin OK"

        elif username_from_database != None:
            if username_from_database == username and password_from_database == password:
                # print('login successfully')
                return True

        else:
            return False

    def search_usernames(self,username_to_find):
        database = Database('messenger_database')

        list_of_usernames = database.get_list_of_possible_usernames(username_to_find)

        return list_of_usernames

    def search_chat(self,chat_to_find):
        database = Database('messenger_database')

        list_of_usernames = database.get_list_of_possible_chats(chat_to_find)

        return list_of_usernames

    def register_new_user(self,request,client):
        database = Database('messenger_database')
        username = request[0]
        password = request[1]

        if database.check_user_exists(username)[0] is None:
            database.add_user(username, password)
            client[0].send(encryption.encrypt_sym("REG OK", client[1]).encode())
        else:
            client[0].send(encryption.encrypt_sym("REG FAILED", client[1]).encode())

    def login_user(self,request,client):
        username = request[0]
        password = request[1]
        if self.try_login(username,password) == 'admin OK':
            client[0].send(encryption.encrypt_sym("ADMIN LOGIN OK", client[1]).encode())
        elif self.try_login(username, password):
            # print("login successfully")
            client[0].send(encryption.encrypt_sym("LOGIN OK", client[1]).encode())
        elif not self.try_login(username, password):
            # print('login failed')
            client[0].send(encryption.encrypt_sym("LOGIN FAILED", client[1]).encode())

    def send_text(self,request,client):
        username = request[0]
        chatroom_name = request[1]
        text = request[2]

        database = Database('messenger_database')
        try:
            database.new_message(chatroom_name, username, text)
            #print("broadcasting now")
            client[0].send(encryption.encrypt_sym("SEND MSG|OK", client[1]).encode())


            self.broadcast(username, chatroom_name, text)

        except Exception as e:
            client[0].send(encryption.encrypt_sym("SEND MSG|FAILED", client[1]).encode())
            print(e)
        del database

    def send_text_without_saving(self,request, client):
        username = request[0]
        chatroom_name = request[1]
        text = request[2]


        try:

            #print("broadcasting now")
            client[0].send(encryption.encrypt_sym("SEND MSG|OK", client[1]).encode())

            self.broadcast(username, chatroom_name, text)

        except Exception as e:
            client[0].send(encryption.encrypt_sym("SEND MSG|FAILED", client[1]).encode())
            print(e)



    def create_new_chat(self,chat_name):


        database = Database('messenger_database')

        database.add_chat(chat_name)
        del database

    def add_users_to_chat(self,chat_name,users_list):
        database = Database("messenger_database")
        #print("users list: ",users_list)
        for user in users_list:
            database.add_participant_to_chat(chat_name,user)

        #print(users_list[0], ": ",database.get_chats_related_to_user('sasha'))

        database.new_message(chat_name,'automatic message',str(users_list[-1] + " created chatroom"))
        del database

    def broadcast_new_chat(self,chat_name,chat_creator):
        database = Database('messenger_database')

        list_of_users_in_the_same_chat = database.get_list_of_users_in_chat(chat_name)

        msg = "NEW CHAT" + "|" + chat_name + ":" +chat_creator

        for client_with_username in self.client_n_username:
            username = client_with_username[0]
            client = client_with_username[1]
            if username in list_of_users_in_the_same_chat:
                client[0].send(encryption.encrypt_sym(msg, client[1]).encode())
        del database

    def delete_user(self,user_to_delete):
        database = Database('messenger_database')

        database.delete_user(user_to_delete)
        del database
        return True

    def delete_chat(self,chat_to_delete):
        database = Database('messenger_database')

        database.delete_chat(chat_to_delete)
        del database
        return True

# ------------------------------------------------------
# ---------------------MAIN_FUNCTION--------------------
# ------------------------------------------------------

server_object = Server()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(('localhost', 8080))

server.listen(20)

def Main():
    print("Server is running")
    while True:

        conn, addr = server.accept()
        print(addr[0] + ' connected')
        try:
            server_object.exchange_keys(conn)


            client = server_object.client_n_key[-1]                                              #these 4 lines create a separate thread (proccess) running in background
            th = threading.Thread(target=server_object.recieve_requests, args=(client,))         # for receiving and handling requests from all of the connected clients simulataneusly
            th.daemon = True
            th.start()
        except:
            print("error occured when client was connecting")


Main()