import os, sys
import socket
import threading

import PySimpleGUI as pg

import encryption
import rsa
from encryption import *

# ------------------------------------------------------
# ---------------------LAYOUTS--------------------------
# ------------------------------------------------------

login = [
    [pg.Text("Welcome to S-Chat", background_color=('black'), font=("Helvetica", 22), pad=(130, 30))],
    [pg.Text("Username: ", background_color=('black'),font=("Helvetica", 14),size = (11,1),pad=(5,(1,20))), pg.Input(size=(30, 1),pad=(5,(1,20)), focus=True, key='username',font=("Helvetica", 14))],
    [pg.Text("Password: ", background_color=('black'),font=("Helvetica", 14),size = (11,1)),pg.Input(size=(30, 1), key='password', password_char=('*'),font=("Helvetica", 14))],
    [pg.Text('', font=("Helvetica", 16), text_color=('red'), key='login_error_text', background_color=('black'))],
    [pg.Button('Login',bind_return_key=True, key="login_key", size = (10,2),pad=(170,3), button_color=('black'))],
    [pg.Text("Don't have an account: ",font=("Helvetica", 13), background_color=("black"), pad=(0, 20)),
     pg.Text('register',font=("Helvetica", 13), text_color=('lightblue'), click_submits=True, key='reg_button',
             background_color=("black"))],
    [pg.Button('Exit',size = (10,2),pad=(170,(90,1)), button_color=("black"))]
]

register = [
    [pg.Text("Register", background_color=('black'), font=("Helvetica", 22), pad=(190, 30))],
    [pg.Text("", background_color=('black'), key='register_error_text', text_color='red')],
    [pg.Text('Username:', background_color="black",font=("Helvetica", 14),size = (11,1),pad=(5,(1,20))), pg.Input(key='new_user_username',font=("Helvetica", 14),size = (30,1),pad=(5,(1,20)))],
    [pg.Text('Password:', background_color="black",font=("Helvetica", 14),size = (11,1)), pg.Input(key='new_user_password',font=("Helvetica", 14),size = (30,1))],
    [pg.Button("Register",size = (10,2),pad=(170,3), button_color='black', key='register_button')],
    [pg.Text("Already have an account?: ",font=("Helvetica", 13), background_color=('black'), pad=(0, 20)),
     pg.Text('Login', text_color=('lightblue'),font=("Helvetica", 13), click_submits=True, key='transfer_to_login_button',
             background_color=("black"))],

]

main = [
    [pg.Button("Log Out", button_color="black", key='log_out_button', pad=(0, 0),size = (10,2)),
     pg.Button("New chat", button_color="black", key="new_chat_button",size = (10,2))],
    [pg.Text(background_color='black')]

]

chat = [
    [pg.Button('Back',key = 'chat_window_back_button',button_color='black',pad = (0,0),size = (10,1)),pg.Checkbox('Save messages in database',key = 'save_messages_checkbox',default=True,background_color='black')],
    [pg.Multiline(key='text_field', background_color='black', size=(65, 23),font=("Helvetica", 14),autoscroll=True)],
    [pg.Input(size=(45, 1),font=("Helvetica", 14), key="text_to_send", background_color='black', text_color='white'),
     pg.Button("Send", size=(10, 0), key="send_button", button_color='black',bind_return_key=True)],
    [pg.Text("Select a file",background_color='black',size = (55,0)),pg.FileBrowse(key = 'file_browser',button_color='black',),pg.Button("Submit",key = 'send_file_button',button_color='black')]
]

new_chat_window = [
    [pg.Button("Back", size=(10, 1), key='back_button', button_color='black')],

    [pg.Text("Chat name",font=("Helvetica", 14), text_color='white', background_color='black'),
     pg.Input(size=(20, 1),font=("Helvetica", 14), key='new_chat_name', text_color="black")],

    [pg.Text('Search for users: ',font=("Helvetica", 14), background_color='black'), pg.Input(key='user_search_input',font=("Helvetica", 14), size=(15, 1)),
     pg.Button('Search', key="search_button", button_color='black')],

    [pg.Text("Possible users: ",font=("Helvetica", 14), background_color='black',size=(28,0),pad = ((40,0),0)),pg.Text('Added Users: ',font=("Helvetica", 14),background_color='black',pad = ((40,0),0))],

    [pg.Listbox(key="possible_users_listbox", size=(20, 10),font=("Helvetica", 14), values= []),
     pg.Button("Add ->",key = 'new_chat_add_button',size = (10,1),button_color='black'),
     pg.Listbox(key = 'added_users_listbox',size = (20,10),values = [],font=("Helvetica", 14))],

    [pg.Button("Remove <-",key = 'new_chat_remove_button',size = (10,1),button_color='black',pad = (195,0))],

    [pg.Button('Create Chat', key='create_chat_button', size = (25,2),button_color='black',pad = (190,(50,0)))],
    [pg.Text("",key = 'new_chat_error_text',background_color='black',text_color= 'red',font=("Helvetica", 14),pad = (130,(5,0)))]
]

admin_panel_window = [
    [pg.Button("Log out",key = 'admin_panel_logout_button',button_color='black',size = (10,1)),
     pg.Text("Welcome to Admin Panel",background_color='black',size = (23,2),font = ("Helvetica", 18),pad = ((40,0),0))],
    [pg.Text('Search for users: ',font=("Helvetica", 14), background_color='black',pad=((40, 0), 0)),pg.Text('Search for chat: ',font=("Helvetica", 14), background_color='black',pad=((120,0), 0))],
    [pg.Input(key='admin_panel_user_search_input',font=("Helvetica", 14), size=(15, 1)), pg.Button('Search', key="admin_panel_user_search_button", button_color='black',pad=((0, 80), 0)),
     pg.Input(key='admin_panel_chat_search_input',font=("Helvetica", 14), size=(15, 1)), pg.Button('Search', key="admin_panel_chat_search_button", button_color='black')],
    [pg.Listbox(key="admin_panel_users_listbox", size=(20, 10), values=[], font=("Helvetica", 14),pad=((0, 80), 0)),
     pg.Listbox(key='admin_panel_chats_listbox', size=(20, 10), values=[], font=("Helvetica", 14))],
    [pg.Button('Delete user',key = 'admin_panel_delete_user_button',button_color='black',size = (10,2),pad=((40, 80), 0)),
     pg.Button('Delete chat', key = 'admin_panel_delete_chat_button',button_color='black',size = (10,2),pad=((80,0),0))]
]

tabgroup = [
    [
        pg.TabGroup(
            [[
                pg.Tab("Login window", login, key='login_window', title_color='black', background_color='black',
                       visible=True, disabled=False),

                pg.Tab('Register', register, key='register_window', title_color='black', background_color='black',
                       visible=False, disabled=True),

                pg.Tab("Main", layout=main, key='main_window', title_color='black', background_color='black',
                       visible=False, disabled=True),

                pg.Tab("Chat", layout=chat, key='chat_window', title_color='black', background_color='black',
                       visible=False, disabled=True),

                pg.Tab("Create_new_chat", layout=new_chat_window, key='new_chat_window', background_color='black',
                       visible=False, disabled=True),

                pg.Tab('Admin panel',layout= admin_panel_window, key = 'admin_panel_window', background_color='black',
                       visible=False,disabled=True)
            ]],
            key='tab_group', title_color='black', background_color='black', selected_background_color='black',size=(500,500)
        )
    ]
]


# ------------------------------------------------------
# ---------------------MAIN_FUNCTION--------------------
# ------------------------------------------------------

def Main():
    global current_user
    current_user = Client()

    global current_admin
    current_admin = Admin()

    global window
    pg.theme('Black')
    window = pg.Window('Login/Register', tabgroup, background_color='#000000',size = (500,500))
    global recv_loop
    recv_loop = threading.Thread(target=Client.receive_msg_loop, args=(current_user.s, current_user.Sym_Key),
                                 daemon=True)

    window_controller.login_while()


# ------------------------------------------------------
# ---------------------CHATROOM_CLASS-------------------
# ------------------------------------------------------

class chatroom():
    instances = []

    def __init__(self, chatroom_name):
        self.name = chatroom_name
        self.messages = []
        self.__class__.instances.append(self)

    def __del__(self):
        pass

    @classmethod
    def find(cls, name_to_find):          #finds and return the chatroom object given its name
        for instance in cls.instances:
            if instance.name == name_to_find:
                return instance

    @classmethod
    def get_chat_num(cls):        # returns the number of chatroom objects
        return len(cls.instances)

    @classmethod
    def get_list_of_chatnames(cls):  # return a list of names of all the chatroom objects
        list_of_names = []
        for instance in cls.instances:
            list_of_names.append(instance.name)
        return list_of_names

    @classmethod
    def create_chats(cls, data):     # creates a chatroom instances given the data
        #print('creating chats')
        for chat_n_messages in data:
            chatname = str(chat_n_messages[0])
            messages_list = list(chat_n_messages[1])

            #print("messages_list: ", messages_list)

            chatname = chatroom(chatname)
            chatname.messages = messages_list




    @classmethod
    def add_chat(cls,chat_name,chat_creator):     # creates another chatroom object
        chat_name = chatroom(chat_name)

        chat_name.messages.append("automatic message, This chat was created by "+ chat_creator)

    @classmethod
    def append_message_to_chatroom_object(cls, chatroom_sending_to, sender_username, text):
        chatroom_to_append_to = chatroom.find(chatroom_sending_to)

        #print('chatroom messages before appending: ', chatroom_to_append_to.messages)

        chatroom_to_append_to.messages.append(str(sender_username + "," + text))

        #print('chatroom messages after appending: ', chatroom_to_append_to.messages)

    def get_messages(self):    #returns a list of messages of the give chatroom object
        return self.messages


# ------------------------------------------------------
# ---------------------WINDOW_CONTROLLER_CLASS-----------
# ------------------------------------------------------


class window_controller():

    @staticmethod
    def check_login_fields(values):
        if values['username'] != '':
            if values['password'] != '':
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def check_new_chat_fields(values):
        chat_name = values['new_chat_name']
        added_users = window['added_users_listbox'].get_list_values()

        if chat_name == '':
            window['new_chat_error_text'].Update("Please input a name for the chat")
            return False
        elif added_users == []:
            window['new_chat_error_text'].Update("At least one other user has to be added ")
            return False
        else:
            return True

    @staticmethod
    def update_search_listbox(list_of_possible_usernames):
        if current_user.get_username() in list_of_possible_usernames:
            list_of_possible_usernames.remove(current_user.get_username())
        window['possible_users_listbox'].Update(values = list_of_possible_usernames)

    @staticmethod
    def update_admin_panel_users_listbox(list_of_possible_usernames):
        list_of_possible_usernames.remove('admin')

        window['admin_panel_users_listbox'].Update(values = list_of_possible_usernames)

    @staticmethod
    def update_admin_panel_chats_listbox(list_of_possible_chats):

        window['admin_panel_chats_listbox'].Update(values=list_of_possible_chats)

    @staticmethod
    def display_messages_in_chat(chat_name, num):

        current_chat = chatroom.find(chat_name)

        msg = current_chat.messages
        msg2 = msg.copy()

        # print("messages when displaying: ",current_chat.messages)
        if num == 'all':
            window['text_field'].Update('')
            for i in range(len(msg2)):
                #print('first: ',msg2[i])
                #msg2[i] = msg2[i].replace(",", ":", 1)
                #print('second: ',msg2[i])
                msg2[i] = msg2[i].split(",")
                #print('third: ',msg2[i])
                username = msg2[i][0]
                text = msg2[i][1]

                window['text_field'].Update(username + ':', append=True)
                window['text_field'].Update(text + "\n", append=True, text_color='white')
        else:
            msg2[-1] = msg2[-1].replace(",", ":", 1)
            msg2[-1] = msg2[-1].split(":")
            username = msg2[-1][0]
            text = msg2[-1][1]
            window['text_field'].Update(username + ':', append=True)
            window['text_field'].Update(text + "\n", append=True, text_color='white')

    @staticmethod
    def append_user_to_added_users_listbox(selected_user):
        added_listbox_values = window['added_users_listbox'].get_list_values()

        added_listbox_values.append(selected_user)

        window['added_users_listbox'].Update(values = added_listbox_values)

    @staticmethod
    def remove_user_from_added_users_listbox(user_to_remove):
        added_listbox_values = window['added_users_listbox'].get_list_values().copy()

        added_listbox_values.remove(user_to_remove)

        window_controller.append_user_to_added_users_listbox(user_to_remove)

        window['added_users_listbox'].Update(values=added_listbox_values)

    @staticmethod
    def transfer_to_main_window():
        for i in range(chatroom.get_chat_num()):
            window.extend_layout(window['main_window'], [[pg.Text(chatroom.get_list_of_chatnames()[i],
                                                                  font=("Helvetica", 18),

                                                                  size=(25, 1)),
                                                          pg.Button('Message',
                                                                    key=('join' + chatroom.get_list_of_chatnames()[i]),

                                                                    pad=((80,1), 0))]])

        window['main_window'].Update(disabled=False, visible=True)
        window['tab_group'].Widget.select(2)
        window['login_window'].Update(disabled=True, visible=False)
        window['new_chat_window'].Update(disabled=True, visible=False)
        window_controller.main_while()

    @staticmethod
    def transfer_to_main_window_no_upate():
        window['main_window'].Update(disabled=False, visible=True)
        window['tab_group'].Widget.select(2)
        window['login_window'].Update(disabled=True, visible=False)
        window['new_chat_window'].Update(disabled=True, visible=False)
        window['chat_window'].Update(disabled=True, visible=False)
        window_controller.main_while()

    @staticmethod
    def update_main_window():
        window.extend_layout(window['main_window'], [[pg.Text(chatroom.get_list_of_chatnames()[-1],
                                                              font=("Helvetica", 18),

                                                              size=(25, 1)),
                                                      pg.Button('Message',
                                                                key=('join' + chatroom.get_list_of_chatnames()[-1]),

                                                                pad=((80, 1), 0))]])

    @staticmethod
    def transfer_to_register_window():
        print("transfering to register page")

        window['register_window'].Update(disabled=False, visible=True)
        window['tab_group'].Widget.select(1)
        window['login_window'].Update(disabled=True, visible=False)
        window_controller.register_while()

    @staticmethod
    def transfer_to_login_window():
        window['login_window'].Update(disabled=False, visible=True)
        window['tab_group'].Widget.select(0)
        window['register_window'].Update(disabled=True, visible=False)
        window_controller.login_while()

    @staticmethod
    def transfer_to_chat_window(chat_name):
        window['chat_window'].Update(disabled=False, visible=True)
        window['tab_group'].Widget.select(3)
        window['main_window'].Update(disabled=True, visible=False)

        window_controller.chatroom_while(chat_name)

    @staticmethod
    def transfer_to_create_new_chat_window():
        window['new_chat_window'].Update(disabled=False, visible=True)
        window['tab_group'].Widget.select(4)
        window['main_window'].Update(disabled=True, visible=False)

        window_controller.new_chat_while()

    @staticmethod
    def transfer_to_admin_panel_window():
        window['admin_panel_window'].Update(disabled=False, visible=True)
        window['tab_group'].Widget.select(5)
        window['login_window'].Update(disabled=True, visible=False)

    @staticmethod
    def login_while():

        while True:
            event, values = window.read()

            if event == 'Exit' or event == pg.WINDOW_CLOSED:
                window.close()
                break



            elif event == 'reg_button':
                window_controller.transfer_to_register_window()


            elif event == 'login_key':
                if window_controller.check_login_fields(values):
                    username, password = values['username'], encryption.generate_hash(values['password'], 6, 7, 64)
                    print("sending login details from GUI")

                    current_user.try_login(username,password)
                else:
                    window['login_error_text'].Update('Please,fill all the fields')
                    print('not everything filled')

    @staticmethod
    def register_while():
        while True:
            event, values = window.read()

            if event == pg.WINDOW_CLOSED:
                window.close()
                break

            elif event == 'register_button':
                current_user.register(values)



            elif event == 'transfer_to_login_button':
                window_controller.transfer_to_login_window()

    @staticmethod
    def main_while():

        while True:
            event, values = window.read()

            if event == pg.WINDOW_CLOSED:
                window.close()
                break
            elif event == 'log_out_button':

                os.execl(sys.executable, sys.executable, *sys.argv)

            elif event[:4] == 'join':
                chat_name = event[4:]
                window_controller.display_messages_in_chat(chat_name, 'all')
                window_controller.transfer_to_chat_window(chat_name)
            elif event == "new_chat_button":
                window_controller.transfer_to_create_new_chat_window()

    @staticmethod
    def chatroom_while(chatroom_name):

        while True:
            event, values = window.read()

            if event == pg.WINDOW_CLOSED:
                window.close()
                break

            elif event == "chat_window_back_button":
                window_controller.transfer_to_main_window_no_upate()


            elif event == 'send_button':
                message_to_send = values['text_to_send']
                if values['save_messages_checkbox'] == True:
                    current_user.send_message(chatroom_name, message_to_send)
                else:
                    current_user.send_message_without_saving_to_database(chatroom_name, message_to_send)

            elif event == 'send_file_button':
                file_name = values['file_browser']

                current_user.send_file(file_name,chatroom_name)

    @staticmethod
    def new_chat_while():

        while True:
            event, values = window.read()

            if event == pg.WINDOW_CLOSED:
                window.close()
                break

            elif event == 'back_button':
                window_controller.transfer_to_main_window_no_upate()

            elif event == 'search_button':
                search_input = values['user_search_input']

                current_user.search_username(search_input)

            elif event == 'new_chat_add_button':
                try:
                    selected_user = values['possible_users_listbox'][0]


                    current_possible_users_list = window['possible_users_listbox'].get_list_values()
                    new_possible_users_list = current_possible_users_list.copy()
                    new_possible_users_list.remove(selected_user)
                    window_controller.append_user_to_added_users_listbox(selected_user)
                    window_controller.update_search_listbox(new_possible_users_list)
                except:
                    window['new_chat_error_text'].Update('No user selected to add')

            elif event == 'new_chat_remove_button':
                try:
                    selected_user = values['added_users_listbox'][0]
                    current_possible_users_list = window['possible_users_listbox'].get_list_values()
                    new_possible_users_list = current_possible_users_list.copy()
                    new_possible_users_list.append(selected_user)
                    window_controller.remove_user_from_added_users_listbox(selected_user)
                    window_controller.update_search_listbox(new_possible_users_list)
                except:
                    window['new_chat_error_text'].Update('No user selected to remove')



            elif event == 'create_chat_button':
                chat_num = chatroom.get_chat_num()
                if window_controller.check_new_chat_fields(values) == True:

                    chatname = values['new_chat_name']
                    users_list = window['added_users_listbox'].get_list_values().copy()
                    #print("chat created")
                    current_user.create_new_chat_request(chatname,users_list)

                if chatroom.get_chat_num() > chat_num:
                    window_controller.transfer_to_main_window_no_upate()


    @staticmethod
    def admin_panel_while():

        while True:
            event, values = window.read()

            if event == pg.WINDOW_CLOSED:
                window.close()
                break
            elif event == 'admin_panel_logout_button':
                os.execl(sys.executable, sys.executable, *sys.argv)

            elif event == 'admin_panel_user_search_button':
                search_input = values['admin_panel_user_search_input']

                current_admin.search_for_user(search_input)

            elif event == 'admin_panel_chat_search_button':

                search_input = values['admin_panel_chat_search_input']

                current_admin.search_for_chat(search_input)


            elif event == 'admin_panel_delete_user_button':
                user_to_delete = values['admin_panel_users_listbox'][0]

                current_admin.delete_user(user_to_delete)

            elif event== 'admin_panel_delete_chat_button':
                chat_to_delete = values['admin_panel_chats_listbox'][0]

                current_admin.delete_chat(chat_to_delete)


#-------------------------------------------------------
# ---------------------ADMIN_CLASS----------------------
# ------------------------------------------------------


class Admin():
    def __init__(self):
        self.s = None
        self.Sym_Key = None
        self.user = ''
        self.password = ''

    def receive_msg(self):

        data = self.s.recv(65536).decode()

        message = encryption.decrypt_sym(data, self.Sym_Key)
        #print('admin recieve msg: ', message)

        self.handle_incoming_data(message)

    def handle_incoming_data(self,message):
        command = message.split("|")[0]
        #print("Admin command: ",command)
        request = message.split("|")[1]
        #print("Admin request: ",request)

        if command == 'FOUND USERNAMES':
            list_of_possible_usernames = request.split(',')
            list_of_possible_usernames.pop(-1)
            #print("ADMIN list of possible usernames: ",list_of_possible_usernames)
            window_controller.update_admin_panel_users_listbox(list_of_possible_usernames)

        elif command == 'FOUND CHATS':
            list_of_possible_chats = request.split(',')
            list_of_possible_chats.pop(-1)
            #print("ADMIN list of possible chats: ",list_of_possible_chats)
            window_controller.update_admin_panel_chats_listbox(list_of_possible_chats)

        elif command == 'DELETE USER OK':
            deleted_user = request

            #print("user " + deleted_user + " was successfully deleted")

            listbox_values = window['admin_panel_users_listbox'].get_list_values()


            listbox_values.remove(deleted_user)


            window['admin_panel_users_listbox'].Update(values = listbox_values)

        elif command == 'DELETE CHAT OK':
            deleted_chat = request
            #print("chat "+ deleted_chat + " was successfully deleted")

            listbox_values = window['admin_panel_chats_listbox'].get_list_values()

            listbox_values.remove(deleted_chat)

            window['admin_panel_chats_listbox'].Update(listbox_values)

    def search_for_user(self,search_input):
        command = str("SEARCH USERNAME" + "|" + search_input)

        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())

        self.receive_msg()

    def search_for_chat(self,search_input):
        command = str("SEARCH CHAT" + "|" + search_input)

        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())

        self.receive_msg()

    def delete_user(self,user_to_delete):
        command = str("DELETE USER" + "|" + user_to_delete)

        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())

        self.receive_msg()

    def delete_chat(self,chat_to_delete):
        command = str("DELETE CHAT" + "|" + chat_to_delete )

        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())

        self.receive_msg()


# ------------------------------------------------------
# ---------------------CLIENT_CLASS---------------------
# ------------------------------------------------------


class Client():
    def __init__(self):
        self.s, self.Sym_Key = self.connect('localhost', 8080)
        self.username = ''
        self.password = ''
        self.message_sending = ''

        #attributes required for file transfers
        self.receive_file_flag = False
        self.file_name_to_receive = ''

    def get_username(self):
        return self.username

    @staticmethod
    def receive_msg_loop(s, Sym_Key):
        while True:
            if not current_user.receive_file_flag:    # receive request mode
                data = s.recv(200000).decode()

                message = encryption.decrypt_sym(data, Sym_Key)
                #print('recieve msg: ', message)

                Client.handle_incoming_data(message)

            elif current_user.receive_file_flag == True:   # receive file mode


                with open(current_user.file_name_to_receive, "wb") as f:
                    while True:
                        bytes_read = s.recv(1024)
                        #print(bytes_read)
                        if bytes_read[-4:] == b"DONE":
                            bytes_read = bytes_read[:-4]
                            break
                        f.write(bytes_read)
                        #print("writen")
                    f.write(bytes_read)
                    f.close()
                print("receiving finished")

                # setting attributes to default

                current_user.receive_file_flag = False
                current_user.file_name_to_receive = ''

    @staticmethod
    def handle_incoming_data(message):
        command = message.split("|")[0]
        #print(command)
        request = message.split("|")[1]
        #print(request)

        if command == "SEND MSG" and request == 'OK':
            print("message sent sucessfully")
            window['text_to_send'].Update('')
            current_user.message_sending = ''
        elif command == "CHATS":
            splitted_data = current_user.receive_and_process_startup_data(request)
            if splitted_data != '':
                chatroom.create_chats(splitted_data)
            recv_loop.start()
            window_controller.transfer_to_main_window()





        elif command == 'NEW MESSAGE':
            request = request.split(",", 2)
            #print('request: ', request)

            sender_username = request[0]
            chatroom_sending_to = request[1]
            text_sending = request[2]

            chatroom.append_message_to_chatroom_object(chatroom_sending_to, sender_username, text_sending)

            window_controller.display_messages_in_chat(chatroom_sending_to, '1')

        elif command == 'FOUND USERNAMES':
            list_of_possible_usernames = request.split(',')
            list_of_possible_usernames.pop(-1)
            #print("list of possible usernames: ",list_of_possible_usernames)

            window_controller.update_search_listbox(list_of_possible_usernames)

        elif command == "NEW CHAT":
            new_chats_name = request.split(":")[0]

            chat_creator = request.split(":")[1]

            Client.proccesss_new_chat(new_chats_name,chat_creator)
        elif command == "CHAT CREATE FAILED":
            window['new_chat_error_text'].Update("Chat name already taken")

            #window_controller.transfer_to_create_new_chat_window()

        elif command == "CHAT CREATE OK":
            window['new_chat_error_text'].Update("Chat successfully created")


        elif command == "PREPARE TO RECEIVE FILE":
            file_name = "(received)"
            file_name += request

            current_user.receive_file_flag = True
            current_user.file_name_to_receive = file_name


            msg = "READY TO RECEIVE FILE DATA"       # sending response

            current_user.s.send(encryption.encrypt_sym(msg, current_user.Sym_Key).encode())

    def connect(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((ip, port))

        Sym_Key = Client.exchange_keys(s)

        return s, Sym_Key

    @staticmethod
    def exchange_keys(s):

        ############FIRST STAGE################################
        print("Listening to incoming data: ")
        try:
            msg = (s.recv(2024).decode())

            if msg[0:2] == "PK":

                Public_Key = msg[3:-1]
                Public_Key = Public_Key.split(',')
                for i in range(len(Public_Key)):
                    Public_Key[i] = int(Public_Key[i])

                #print("Public_Key: ", Public_Key)

                ##########################SECOND STAGE###################################
                print("\nSending SymKey encrypted with public key...")

                Sym_Key = encryption.gen_SymKey(64)
                print("Sym_Key before encryption: ",Sym_Key)

               #sending symkey encrypted by public key
                cipher_sym_key = rsa.encrypt(Public_Key, str(Sym_Key))
                s.send(("SK" + cipher_sym_key).encode())

                try:
                    data = (s.recv(2048)).decode()
                    if encryption.decrypt_sym(data, Sym_Key) == "ACK":
                        print("Keys exchanged succesfully")
                except:
                    print("not succesfull key exchange")
                    s.close()

                return Sym_Key
        except:
            print('no public key recieved')
            s.close()

    def request_startup_data(self): #sends a request to the server to send back data about all the chats and messeges related to this user
        self.s.send(encryption.encrypt_sym(("SEND_STARTUP_DATA|" + self.username), self.Sym_Key).encode())
        self.receive_msg_loop(self.s,self.Sym_Key)

    def receive_and_process_startup_data(self,message):   #parses data received from server
            if message != '':
                message = message[2:]
                #print(message)
                message = message.split("--")

                for i in range(len(message)):
                    message[i] = message[i].split(":")

                for i in range(len(message)):
                    message[i][1] = message[i][1].replace('(', "")
                    message[i][1] = message[i][1].replace("'", "")
                    message[i][1] = message[i][1].replace("),", "|")
                    message[i][1] = message[i][1].replace(")", "")
                    message[i][1] = message[i][1].split("|")

                splitted_data_chats_n_messages = message
                #print("splited data: ", splitted_data_chats_n_messages)      <------- uncomment
                #                                                       will show complex array structure when run
                #                                                       (used to hold data about chats and messages in them
                #                                                         created by parsing incoming data form server)

                return splitted_data_chats_n_messages
            else:
                return ''

    def receive_msg(self):     #recieves data and decrypts when called
        data = self.s.recv(32768).decode()
        msg = encryption.decrypt_sym(data, self.Sym_Key)
        return msg

    def login_request(self, username, password):      #sends credentials to the server and waits for response if they are valid or not
        self.s.send(encryption.encrypt_sym(('LOGIN|' + username + '|' + password), self.Sym_Key).encode())

        msg = self.receive_msg()
        print(msg)
        if msg == "LOGIN OK":

            return True
        elif msg == "LOGIN FAILED":
            window['login_error_text'].Update('Incorrect username or password')
            return False
        elif msg == "ADMIN LOGIN OK":
            return "ADMIN"

    def try_login(self,username,password):      #calls window controler to transfer to another page if login credentials are approved by the server

        if self.login_request(username, password) == True:
            self.username = username
            self.password = password
            self.request_startup_data()


        elif self.login_request(username, password) == "ADMIN":
            print("ADMIN CREATED")

            current_admin.s = self.s
            current_admin.Sym_Key = self.Sym_Key


            window_controller.transfer_to_admin_panel_window()

            window_controller.admin_panel_while()

    def register(self, values):            #reads values input on the register tab and sends request to the server to create a new account with this credentials
        new_user_username, new_user_password = values['new_user_username'], encryption.generate_hash(
            values['new_user_password'], 6, 7, 64)
        if self.register_request(new_user_username, new_user_password):
            self.username = new_user_username
            self.password = new_user_password
            window_controller.transfer_to_main_window()

    def register_request(self, username, password):    # sends new account request and waits for the response if it went succesfully or not
        msg_to_send = encryption.encrypt_sym('REG|' + username + '|' + password, self.Sym_Key).encode()
        self.s.send(msg_to_send)
        data = self.s.recv(1024).decode()
        message = encryption.decrypt_sym(data, self.Sym_Key)
        if message == "REG OK":
            return True
        elif message == "REG FAILED":
            window["register_error_text"].Update("Username already exists,please try another one")
            return False

    def send_message(self, chat, message):          # sends a request to the server saying there is a new message in a given chat from this user
        print("sending message: " + message)
        command = str("SEND TEXT" + "|" + self.username + "|" + chat + "|" + message)
        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())
        self.message_sending = message

    def send_message_without_saving_to_database(self,chat, message):  # alternative of sens_message() does the same but requests server to not save the new message to the database
        print("sending message (incognito): " + message)
        command = str("SEND TEXT NS" + "|" + self.username + "|" + chat + "|" + message)
        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())
        self.message_sending = message

    def send_file_transfer_warning(self,file_name,chatroom_name):   # sends a warning to the server that the next thing sent is going to be a file
        msg = "PREPARE TO RECEIVE FILE" + "|" + file_name.split("/")[-1] + "," + self.username + "," + chatroom_name

        self.s.send(encryption.encrypt_sym(msg, self.Sym_Key).encode())

    def send_file(self,file_name,chatroom_name):            # sends a file to the server
        self.send_file_transfer_warning(file_name,chatroom_name)

        with open(file_name, "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                self.s.sendall(bytes_read)

            print("all bytes sent")
            self.s.send(b"DONE")
            f.close()

    def search_username(self, search_input):              # sends a request to send back a list of usernames which are similar to the 'search_input'
        command = str("SEARCH USERNAME" + "|" + search_input)

        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())

    def create_new_chat_request(self,chat_name,users_list):      # sends a request to the server to create new chat with the given list of users in it
        users_list.append(self.username)
        user_string = ''

        for i in range(len(users_list)):
            if i+1 != len(users_list):
                user_string += str(users_list[i]) + ","
            else:
                user_string += str(users_list[i])

        #print("user_list_string: ",user_string)
        command = str('CREATE NEW CHAT'+'|'+ chat_name + '|' + user_string)

        self.s.send(encryption.encrypt_sym(command, self.Sym_Key).encode())

        #print("command: ",command)

    @staticmethod
    def proccesss_new_chat(chat_name,chat_creator):

        chatroom.add_chat(chat_name,chat_creator)

        window_controller.update_main_window()






Main()
