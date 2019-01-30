<<<<<<< HEAD
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
import pickle
import glob
import base64
import os
import sqlite3
import datetime
#pip install pycryptodomex
from Cryptodome import Random
from Cryptodome.Cipher import AES
#already installed
import hashlib
from tkinter import ttk
import uuid
import subprocess

#What to add:
#Add folder / category creation
#Add min size for the window
#Add backup to gdrive / onedrive
#redesign settings menu (again)

#Main Window
root = Tk()
root.title('SafeKey Password Manager')
root.grid_propagate(False)
#root.minsize(width=846,height=400)

#Generate a unique IV from the Computer UUID
def iv_from_uuid():
    i = 0
    the_iv = ''
    iv = str(subprocess.check_output('wmic csproduct get UUID'))
    for letter in iv:
        i = i+1
        if i > 46 and letter != '-':
            the_iv = the_iv + letter
    print(the_iv)
    the_iv = the_iv[:16]
    the_iv = the_iv.encode()
    return(the_iv)

#Check if config file exists
def load_settings():
    #Check if settings file exists and if not, create it. if exists proceed to look over it
    if os.path.isfile('sfky_cnfg.pkl'):
        config_file = open('sfky_cnfg.pkl', 'rb')
        config_file.close()
    else:
        #iv = Random.new().read(AES.block_size)
        iv = iv_from_uuid()
#        os.makedirs('accounts')
        current_directory = os.getcwd()
        config_file = open('sfky_cnfg.pkl', 'wb')
        config_elements = {'file_location':f'db.sqlite',
                           'master_key':'key_string',
                           'key_file_location':'file_path',
                           'use_key_file':'false',
                           'key_type':'None',
                           'encryption_format':'BASE64',
                           'aes_iv':iv,
                           'geometry':'100x19+900+520',
                           'width':'846',
                           'height':'400',
                           'x_pos':'x',
                           'y_pos':'y'
                           }
        pickle.dump(config_elements,config_file)
        config_file.close()
    #Check if folder location has been set
    print('\n===Settings===')
    print(f'Loading config file: sfky_cnfg.pkl')
    with open('sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
    document_path = config_elements['file_location']
#    if document_path == 'db.sqlite':
#        print('File location is not set, switching to default directory')
#        current_directory = os.getcwd()
#        document_path = f'{current_directory}\\accounts'
#    else:
#        print(f'File location set: {document_path}')
    #check to see wheather to use the the key from the file
    if config_elements["use_key_file"] == True and config_elements["master_key"] != 'key_string':
        master_key_str = config_elements["master_key"]
    else:
        master_key_str = ''
    global geometry,width,height,encryption,key_file_path,window_x,window_y
    geometry = config_elements["geometry"]
    width = config_elements["width"]
    height = config_elements["height"]
    encryption = config_elements["encryption_format"]
    key_file_path = config_elements["key_file_location"]
    window_x = config_elements["x_pos"]
    window_y = config_elements["y_pos"]
    print(f'Database file: {document_path}')
    print(f'Master key from file: {config_elements["master_key"]}')
    print(f'Key file location: {config_elements["key_file_location"]}')
    print(f'Encryption: {config_elements["encryption_format"]}')
    print(f'AES IV: {config_elements["aes_iv"]}')
    print(f'Use key file: {config_elements["use_key_file"]}')
    print(f'Key type: {config_elements["key_type"]}')
    print(f'Window Geometry: {config_elements["geometry"]}')
    print('===Settings===')
    config_file.close()
    return document_path,master_key_str,geometry


#Database variable definition
global sqlite_file
sqlite_file = load_settings()
sqlite_file = sqlite_file[0]

#Resize
root.geometry(f'{geometry}')
root.config(height=height,width=width)
root.update_idletasks()



#Connect to DB function
def database_connection(sqlite_file):
    global connection,c
    connection = sqlite3.connect(sqlite_file)
    c = connection.cursor()
    # Check if DB file is new and if not create the tables inside
    if os.stat(sqlite_file).st_size <= 0:
        print('DB file is empty, making necessary tables')
        c.execute(f'CREATE TABLE accounts (id INTEGER PRIMARY KEY,name TEXT,information TEXT,encryption TEXT, last_edit TEXT)')
        connection.commit()
#run the DB function
database_connection(sqlite_file)

#define global variables
#global document_path
#document_path = load_settings()
#document_path = document_path[0]
document_path = ''
global master_key_str
master_key_str = load_settings()
master_key_str = master_key_str[1]

current_selected_item = ''
current_selected_item_index = ''


#vigenere cypher start encode and decode functions
def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

#aes encryption functions
def aes_encode(message):
    with open('sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
    iv = config_elements["aes_iv"]
    obj = AES.new(master_key_str, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))


def aes_decode(cipher):
    with open('sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
    iv = config_elements["aes_iv"]
    obj2 = AES.new(master_key_str, AES.MODE_CFB, iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))


def view_entries():
    #New SQL database code, fetch entry names from DB.sqlite file
    global selection_array
    selection_array = []
    c.execute('SELECT name,information,encryption,last_edit FROM accounts')
    name_row = c.fetchall()
    for name in name_row:
        selection_array.append(name[0])
#       listmenu.insert(END, name[0])
        listmenu2.insert('','end',values=(f'{name[0]}',f'{name[2]}',f'{name[3]}'))
    return selection_array


#This is for listbox
#def entry_select(event):
#    list = listmenu.get(0)
#    if list == '':
#        pass
#    else:
#        doubleclick = event.widget
#        index = int(doubleclick.curselection()[0])
#        value = doubleclick.get(index)
#        print (f'\nYou selected item {value}')
#        entry_window(value)
        #gloval variables for the selected item and its index in the list

#This runs whenever you click on an entry, for treeview not listbox
#def selectItem():
#    #Gets the item that is currently focused
#    curItem = listmenu2.focus()
#    item_dictionary = listmenu2.item(curItem)
#    value = item_dictionary["values"][0]
#    print(f'\nYou selected item {value}')
#Opens up a window with the info inside to edit and save
#    entry_window(value)


def entry_window(file_name):
    entry_window_root = Toplevel(root)
    entry_window_root.title(f'Entry Information: {file_name}')
    entry_window_root.resizable(width=False,height=False)
    entry_window_root.geometry('495x320+902+600')
    #Entry Field and placement
    e = Entry(entry_window_root,width=50)
    e.grid(column=0,row=0,sticky=W,padx=(5,5),pady=(5,2))
    e.insert(END, file_name)
    stringvar = tkinter.StringVar()
    options = ['AES','BASE64']
    stringvar.set(options[1])
    dropdown = OptionMenu(entry_window_root,stringvar,*options)
    dropdown.configure(width=6)
    dropdown.grid(row=0,column=0,sticky=E,padx=(0,5),pady=5)
    account_field = Text(entry_window_root,width=60,height=15)
    account_field.grid(sticky=W,padx=(5,5))
    account_field.focus_force()
    account_field.config(state=NORMAL)
    #button label and placement
    update_account_button = Button(entry_window_root,text='Update',width=13,command=lambda:update_entry(e,file_name,account_field,update_account_button,entry_window_root))
    update_account_button.grid(sticky=S+E,padx=(5,5),pady=(2,2),column=0,row=2)
    #Fetch info from file after decoding
#    print(f'Fetching {document_path}//{file_name}.txt')
#    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'r')
#    account_info = account_info_encrypted.read()
    c.execute(f"SELECT information FROM accounts WHERE name = '{file_name}'")
    account_info = c.fetchone()
    account_info = account_info[0]
    #Checks for the key
    if len(master_key_str) > 0:
        account_info = decode(master_key_str,account_info)
        account_field.insert(END,account_info)
    else:
        print(account_info)
        account_field.insert(END,account_info)
        update_account_button.config(state=DISABLED)
#    account_info_encrypted.close()


def update_entry(name_entry,file_name,account_field,update_account_button,entry_window_root):
    new_name = name_entry.get()
    new_text = account_field.get(1.0,END)
    new_text_encrypted = encode(master_key_str, new_text)
#    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'w')
#    account_info_encrypted.write(new_text_encrypted)
#    account_info_encrypted.close
    now = datetime.datetime.now()
    current_time = f'{now.day}/{now.month}/{now.year}'
    c.execute(f"UPDATE accounts SET information='{new_text_encrypted}' WHERE name='{file_name}'")
    c.execute(f"UPDATE accounts SET last_edit='{current_time}' WHERE name='{file_name}'")
    c.execute(f"UPDATE accounts set name='{new_name}' WHERE name='{file_name}'")
    connection.commit()
    update_account_button.config(text='Done')
    print(f'Updating info with {new_text_encrypted}')
    #Stupid list magic, seriously I dont know why this is even necessary but it is because the list changes after the list gets reloaded, srsly? why??
    selected_item = listmenu2.selection()[0]
    all_items = listmenu2.get_children()
    selected_item_index = all_items.index(selected_item)
    #Check if the search is empty, if its not then do a reload
    reload_list(view_entries(), searchentry, reload=0)
    all_items = listmenu2.get_children()
    selected_item = all_items[selected_item_index]
    listmenu2.see(selected_item)
    listmenu2.selection_set(selected_item)
    listmenu2.focus(selected_item)
    #End list magic
    close_window(entry_window_root, current_selected_item, current_selected_item_index)




#Settings window start==================================================================================================


#Function name should get changed to database_select, too lazy to change it. Will eventually.
def folder_select(file_entry):
    #Ask to select folder where to look for files
    global document_path
    current_directory = os.getcwd()
    document_path = filedialog.askopenfilename()
    if document_path == '':
        document_path = f'{current_directory}\\db.sqlite'
    file_entry.delete(0, END)
    file_entry.insert(0,document_path)
    file_entry.focus()
    #Output the db file location to a dictionary to reload on future launch
    with open(f'sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
        config_elements['file_location'] = document_path
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    config_file.close()
    database_connection(sqlite_file=document_path)
    reload_list(view_entries(), searchentry, reload=1)
#   return document_path


def settings(document_path,sqlite_file):
    x = recalc_position()[0]
    y = recalc_position()[1]
    file_window_root = Toplevel(root)
    file_window_root.title('Settings')
    file_window_root.resizable(width=False,height=False)
    file_window_root.geometry(f'577x125+{x}+{y}')
    #Entry Field and placement
    file_entry = Entry(file_window_root,width=60)
    file_entry.focus()
    #Fill in file path with current into stored inside the sfky_cnfg.pkl file
    file_entry.insert(0, sqlite_file)
    file_entry.grid(sticky=E,row=0,column=1,pady=(2,2),padx=(5,5))
    #Button Label and placement
    file_label = Label(file_window_root, text="Database file")
    file_label.grid(sticky=E,row=0,pady=(2,2))
    #Button and placement
    file_button = Button(file_window_root, text="Browse",width=11,command=lambda:folder_select(file_entry))
    file_button.grid(sticky=W,row=0,column=2,pady=(2,2))
    file_window_root.focus_force()
    #use a key file
    key_location_label = Label(file_window_root, text='Master Key file')
    key_location_label.grid(sticky=E,row=1)
    key_location_entry = Entry(file_window_root,width=60)
    key_location_entry.grid(sticky=W,row=1,column=1,pady=(8,10),padx=(5,5))
    key_file_button = Button(file_window_root, text='Browse',width=11,command=lambda:key_select(key_location_entry,stringvar,enc_change=0))
    key_file_button.grid(sticky=W, row=1,column=2)
    #Select encryption type
    #with open(f'sfky_cnfg.pkl', 'rb') as config_file:
    #    config_elements = pickle.load(config_file)
    #    encryption = config_elements['encryption_format']
    #stringvar = tkinter.StringVar()
    #options = ['AES','BASE64']
    #stringvar.set(encryption)
    #dropdown = OptionMenu(file_window_root,stringvar,*options,command=lambda x:change_encryption(key_location_entry,stringvar,file_window_root,checkbox,key_file=0,enc_change=1))
    #dropdown.configure(width=6)
    #dropdown.grid(row=3,column=1,sticky=W,padx=(2,0))
    #encryption_label = Label(file_window_root, text='Encryption Type')
    #encryption_label.grid(row=3,column=0,sticky=E)
    #select if to use key file on load
    checkbox_value = IntVar()
    checkbox_label = Label(file_window_root, text='Use key file on boot')
    checkbox_label.grid(row=2,column=0,sticky=E)
    checkbox = Checkbutton(file_window_root, variable=checkbox_value,command=lambda:checkbox_action(checkbox_value))
    checkbox.grid(row=2,column=1,sticky=W)
    #checkoff the checkbox with the info stored in the config file
    with open(f'sfky_cnfg.pkl', 'rb') as config_file:
        config_elements = pickle.load(config_file)
        if config_elements['use_key_file'] == True:
            checkbox.select()
        else:
            checkbox.deselect()
        if config_elements['key_file_location'] != 'file_path':
            key_location_entry.insert(0, config_elements['key_file_location'])
        else:
            pass
    apply_button = Button(file_window_root, text="Ok",width=11,command=lambda:close_window(file_window_root,current_selected_item,current_selected_item_index))
    apply_button.grid(row=4,column=2)




def change_encryption(key_location_entry,stringvar,key_file,enc_change):
    global encryption,master_key_str
    #If encryption is being changed by button then reset all settings
    if enc_change == 1:
        master_key_str = ''
        tkinter.messagebox.showinfo('SafeKey Password Manager','Encryption type has been changed, the master key has been reset. Please enter new master key or select a key file.')
        #file_window_root.focus()
        #Change key file back to null
        key_select(key_location_entry,stringvar,enc_change=1)
        #Set checkox back to null
        #checkbox.deselect()
        checkbox_value = IntVar()
        checkbox_value.set(0)
        checkbox_action(checkbox_value)
        encryption_type = stringvar.get()
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['encryption_format'] = encryption_type
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        encryption = encryption_type
        print(f'\n\nEncryption changed to: {encryption_type}')
    #If encryption is being changed by file change settings accordingly
    elif enc_change == 0:
        #Remove key when switching encryption
        if master_key_str != '' and key_file == 0:
            master_key_str = ''
            tkinter.messagebox.showinfo('SafeKey Password Manager','Encryption type has been changed, the master key has been reset. Please enter new master key or select a key file.')
            #file_window_root.focus()
        encryption_type = stringvar.get()
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['encryption_format'] = encryption_type
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        encryption = encryption_type
        print(f'\n\nEncryption changed to: {encryption_type}')
    status_update(master_key_str,found_amount=0,search_update=0)
    global encryption_change




def checkbox_action(checkbox_value):
    value = checkbox_value.get()
    if value == 1:
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['use_key_file'] = True
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        print(f'Use_Key_File set to: {config_elements["use_key_file"]}')
        config_file.close()
    elif value == 0:
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['use_key_file'] = False
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        print(f'Use_Key_File set to: {config_elements["use_key_file"]}')
        config_file.close()


def key_select(key_location_entry,stringvar,enc_change):
    if enc_change == 0:
        global master_key_str
        key_path = filedialog.askopenfilename()
        if key_path == '':
            key_path = 'file_path'
        if key_path != 'file_path':
            key_location_entry.insert(0, key_path)
        key_location_entry.focus()
    #    try:
            #grab info from the key file
        with open(f'{key_path}', 'rb') as key_file:
            key_properties = pickle.load(key_file)
            if 'AES' in key_properties:
                master_key_str = key_properties['AES']
                key_type = 'AES'
            elif 'BASE64' in key_properties:
                master_key_str = key_properties['BASE64']
                key_type = 'BASE64'
        stringvar.set(key_type)
        change_encryption(key_location_entry,stringvar,key_file=1,enc_change=0)
            #dump info into config file
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['key_file_location'] = key_path
            config_elements['master_key'] = master_key_str
            config_elements['key_type'] = key_type
            config_elements['Encryption'] = key_type
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
    #        config_file.close()
        print(f'\nLoading key: {master_key_str}')
        status_update(master_key_str, found_amount=0, search_update=0)
    #    except:
    #        print('Key location not chosen')
    #        pass
        return master_key_str
    elif enc_change == 1:
        #key_location_entry.delete(0, 'end')
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['key_file_location'] = 'file_path'
            config_elements['master_key'] = 'key_string'
            config_elements['key_type'] = 'None'
            config_elements['Encryption'] = stringvar.get()
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)


def create_key_file_window():
    key_window_root = Toplevel(root)
    key_window_root.title('Create Encryption Key File')
    key_window_root.resizable(width=False, height=False)
    key_window_root.geometry('545x73+902+605')
    key_window_root.focus()
    key_label = Label(key_window_root,text='Key String')
    key_label.grid(padx=(5,10),pady=(5,10))
    key_text_entry = Entry(key_window_root,width=60)
    key_text_entry.insert(0,master_key_str)
    key_text_entry.grid(padx=(3,10),pady=(8,10),column=1,row=0,sticky=W)
    key_text_entry.focus()
    key_format = Label(key_window_root,text='Encryption')
    key_format.grid(row=1)
    submit_button = Button(key_window_root,text='Create',width=11,command=lambda:create_key_file(key_window_root,key_text_entry,stringvar))
    submit_button.grid(column=2,row=0,padx=(0,50))
#   create_button = Button(key_window_root,text='Create',width=15)
#   create_button.grid(column=2,row=1,sticky=W)
    stringvar = tkinter.StringVar()
    options = ['AES','BASE64']
    dropdown = OptionMenu(key_window_root,stringvar,*options)
    stringvar.set(options[1])
    dropdown.configure(width=6)
    dropdown.grid(row=1,column=1,sticky=W)
    #Check if key field is empty
    check_if_key_field_empty(submit_button, key_text_entry)
    key_text_entry.bind("<KeyRelease>", lambda x:check_if_key_field_empty(submit_button,key_text_entry))


def check_if_key_field_empty(submit_button,key_text_entry):
    key_text_entry = key_text_entry.get()
    if len(key_text_entry) > 0:
        submit_button.config(state=NORMAL)
    else:
        submit_button.config(state=DISABLED)


def create_key_file(window,key_text_entry,encryption):
    encryption = encryption.get()
    master_key_str = key_text_entry.get()
    if encryption == 'AES':
        #Convert to byte value and add padding to the key
        password = master_key_str.encode()
        master_key_str = hashlib.sha256(password).digest()
    elif encryption == 'BASE64':
        master_key_str = str(master_key_str)
    print(f'\nCreating key file with string: {master_key_str}')
    selected_folder_path = filedialog.askdirectory()
    file = open(f'{selected_folder_path}//{encryption}_safekey.pkl', 'wb')
    key_with_encryption = {f'{encryption}':master_key_str}
    pickle.dump(key_with_encryption, file)
    file.close()
    window.destroy()
    tkinter.messagebox.showinfo('SafeKey Password Manager',f'{encryption} Master Key file created.')
    print(f'{encryption} Master key file created.')


def resize():
    root.update_idletasks()
    geometry = root.winfo_geometry()
    width = root.winfo_width()
    height = root.winfo_height()
    return geometry,width,height

#Get the position and the width and length of the window right before it gets closed to save for letter
def dump_geometry():
    geometry = resize()
    geometry = geometry[0]
    window_width = resize()
    window_width = window_width[1]
    window_height = resize()
    window_height = window_height[2]
    print(f'Dumping window size and position: {geometry}')
    with open(f'sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
        config_elements['geometry'] = geometry
        config_elements['height'] = window_height
        config_elements['width'] = window_width
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    root.destroy()

#Check the position of the window every time it is moved
def dump_position():
    window_x = root.winfo_x()
    window_y = root.winfo_y()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    #print(f'x: {window_x} y: {window_y}')
    with open(f'sfky_cnfg.pkl','rb') as config_file:
        config_elements['x_pos'] = window_x
        config_elements['y_pos'] = window_y
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    return window_x,window_y,window_width,window_height

#Settings window end==================================================================================================

def close_window(window_root,current_selected_item,current_selected_item_index):
    if len(current_selected_item) <= 0:
        window_root.destroy()
        pass
    else:
        try:
#    reload_list(view_entries(document_path), searchentry, reload=1)
            window_root.destroy()
         #reload the current list and select the previously selected item or different item
#        listmenu.selection_clear(0, END)
#        listmenu.selection_set(current_selected_item_index,current_selected_item_index)
#        listmenu.activate(current_selected_item_index)
            mirror_info_to_side(current_selected_item)
#        listmenu.see(current_selected_item_index)
        except:
            pass



def close_window_and_input_key(key_entry,key_button,key_window_root):
    master_key(key_entry,key_button)
    close_window(key_window_root,current_selected_item,current_selected_item_index)


def recalc_position():
    position = dump_position()
    #Get new x-coordinate
    width_adj = int(position[2]) / 3.5
    x = str(round(int(position[0]) + width_adj))
    #Get new y-coordinate
    height_adj = int(position[3]) / 2.4
    y = str(round(int(position[1]) + height_adj))
    return x,y


def master_key_window():
    #grab x,y coordinates relative to size and position of main window
    x = recalc_position()[0]
    y = recalc_position()[1]
    key_window_root = Toplevel(root)
    key_window_root.title('Input Master Key')
    key_window_root.resizable(width=False,height=False)
    key_window_root.geometry(f'531x30+{x}+{y}')
    #Button Label and placement
    key_label = Label(key_window_root, text="Master Key: ")
    key_label.grid(sticky=E,row=0,pady=(2,2),)
    #Entry Field and placement
    key_entry = Entry(key_window_root,width=60)
    key_entry.grid(sticky=E,row=0,column=1,pady=(2,2),padx=(0,1))
    key_entry.focus()
    key_entry.bind('<Return>', lambda x:close_window_and_input_key(key_entry,key_button,key_window_root))
    #Button and placement
    key_button = Button(key_window_root, text="Submit",width=11,command=lambda:close_window_and_input_key(key_entry,key_button,key_window_root))
    key_button.grid(sticky=W,row=0,column=2,pady=(2,2),padx=(5,10))
    #Close window event
    key_window_root.protocol("WM_DELETE_WINDOW", lambda:close_window(key_window_root,current_selected_item,current_selected_item_index))
    key_window_root.bind('<Escape>', lambda x:close_window(key_window_root,current_selected_item,current_selected_item_index))


def master_key(key_entry,key_button):
    global master_key_str
    if encryption == 'BASE64':
        #Grab key from the entry field and change the button text and color
        master_key_str = key_entry.get()
        key_button.config(text="Done")
    elif encryption == 'AES':
        master_key_str = key_entry.get()
        master_key_str = master_key_str.encode()
        #Add padding to the key
        master_key_str = hashlib.sha256(master_key_str).digest()
    status_update(master_key_str,found_amount=0,search_update=0)
    print(f'Encoded master key: {master_key_str}')
    return master_key_str



def info_popup():
    tkinter.messagebox.showinfo('SafeKey Password Manager','Created by Ilya Shevchenko, 2018 \nPlease report any bugs to ilya.93@hotmail.com')


def reload_list(selection_array,searchentry,reload):
    search_update = 1
    #Clear search bar if reloading
    if reload == 1:
        searchentry.delete(0,END)
    search_word = searchentry.get()
    selection_array = [ x.lower() for x in selection_array ]
    found_items = [item for item in selection_array if search_word in item]
    if len(found_items) == 0:
        print('No account infos found')
        update_listbox(found_items)
    status_update(master_key_str,len(found_items),search_update)
    update_listbox(found_items)
#    listmenu.selection_set(0,0)
#    listmenu.activate(0)
    items = [listmenu2.get_children()]
    try:
        listmenu2.selection_set(f'{items[0][0]}')
        listmenu2.focus(f'{items[0][0]}')
        if reload == 1:
            listmenu2.see(f'{items[0][0]}')
        listmenu2.event_generate('<<TreeviewSelect>>')
    except:
        pass

def update_listbox(selection_array):
#    listmenu.delete(0, END)
    listmenu2.delete(*listmenu2.get_children())
    if len(selection_array) == 0:
        listmenu2.delete(*listmenu2.get_children())
    else:
        for item in selection_array:
            c.execute(f"SELECT last_edit FROM accounts WHERE name = '{item}'")
            edit_date = c.fetchone()
            edit_date = edit_date[0]
            c.execute(f"SELECT encryption FROM accounts WHERE name = '{item}'")
            encryption_select = c.fetchone()
            encryption_select = encryption_select[0]
            listmenu2.insert('', 'end', values=(f'{item}', f'{encryption_select}', f'{edit_date}'))


def status_update(master_key,found_amount,search_update):
    encryption_update = f'Encryption: {encryption},  '
    if master_key != '' and search_update == 0:
        status = f'{encryption_update}Master Key Loaded     '
        statustext.config(text=status,fg='green')
    elif master_key == '' and search_update == 0:
        status = f'{encryption_update}No Master Key     '
        statustext.config(text=status,fg='red')
    elif found_amount >= 0 and search_update == 1:
        print(f'{encryption_update}Found {found_amount} entries     ')
        status = f'{encryption_update}Found {found_amount} Entries     '
        statustext.config(text=status,fg='black')


def check_if_search_empty(searchentry):
        if len(searchentry.get()) == 1:
            print('Search is empty, refreshing.')
            reload_list(view_entries(), searchentry,reload=0)
        else:
            pass


#New account panel
def new_account_window():
    x = recalc_position()[0]
    y = recalc_position()[1]
    newpanel = Toplevel(root)
    newpanel.resizable(width=False,height=False)
    newpanel.geometry(f'330x158+{x}+{y}')
    namelabel = Label(newpanel,text='Service:')
    namelabel.grid(row=1,padx=(31,0))
    label2 = Label(newpanel,text='Information:')
    label2.grid(row=2,padx=(5,0),sticky=N)
    servicelabel_entry = Entry(newpanel, width=40)
    servicelabel_entry.focus()
    servicelabel_entry.grid(row=1,column=1,padx=(1,1),pady=(1,0))
    entrybox = Text(newpanel,width=30,height=6)
    entrybox.grid(column=1,row=2,pady=(1,0))
    servicebutton = Button(newpanel,text='Submit',command=lambda:create_entry(servicelabel_entry,entrybox,servicebutton,newpanel,encryption,selection_array))
    servicebutton.grid(row=3,column=1,padx=(197,5),pady=(5,5))
    if len(master_key_str) == 0:
        servicebutton.config(state=DISABLED)



def create_entry(servicelabel_entry,entrybox,servicebutton,window,encryption,selection_array):
    now = datetime.datetime.now()
    now_time = f'{now.day}/{now.month}/{now.year}'
    service_name = servicelabel_entry.get()
    if service_name in selection_array:
        print('Entry with that name already exists')
        #Fnd the existing entry and select it to show that it exists
        iid_selection_array = listmenu2.get_children()
        i = selection_array.index(service_name)
        listmenu2.selection_set(iid_selection_array[i])
        listmenu2.focus(iid_selection_array[i])
        listmenu2.see(iid_selection_array[i])
        tkinter.messagebox.showinfo('SafeKey Password Manager','ERROR: Entry with this name already exists.')
    else:
        service_information = entrybox.get('1.0', END)
        print(f'Encryption type: {encryption}')
        if encryption == 'BASE64':
            service_information_encoded = encode(master_key_str,service_information)
        elif encryption == 'AES':
            service_information_encoded = aes_encode(service_information)
        print(f'Created String: {service_information_encoded}')
        #new_file = open(f'{document_path}/{service_name}.txt', 'w+')
        #new_file.write(service_information_encoded)
        #new_file.close()
        #SQL
        connection.execute("INSERT INTO accounts (name,information,encryption,last_edit) VALUES (?,?,?,?)",(service_name,service_information_encoded,encryption,now_time))
        connection.commit()
        #SQL
        servicebutton.config(text='Done')
        servicelabel_entry.delete(0,END)
        entrybox.delete('1.0',END)
        #Find newly added entry and select it
        reload_list(view_entries(), searchentry, reload=0)
        items = [listmenu2.get_children()]
        listmenu2.selection_set(items[0][-1])
        listmenu2.focus(items[0][-1])
        listmenu2.event_generate('<<TreeviewSelect>>')
        listmenu2.see(items[0][-1])
    #    all_entries = [ listmenu.get(0, END) ]
    #    all_entries = all_entries[0]
    #    new_file_index = all_entries.index(service_name)
    #    print(f'Selecting entry number {new_file_index}')
    #    close_window(window,current_selected_item=service_name)


#Side account info panel code
def info_side_show(event):
#    try:
#        click = event.widget
#        index = int(click.curselection()[0])
#        value = click.get(index)
#        print(f'\nYou selected item {value}')
#        mirror_info_to_side(value)
#        global current_selected_item,current_selected_item_index
#        current_selected_item = value
#        current_selected_item_index = index
#    except IndexError:
#        pass
    try:
        curItem = listmenu2.focus()
        item_dictionary = listmenu2.item(curItem)
        value = item_dictionary["values"][0]
        mirror_info_to_side(value)
        global current_selected_item,current_selected_item_index
        current_selected_item = value
        current_selected_item_index = selection_array.index(value)
    except IndexError:
        pass



def mirror_info_to_side(file_name):
    sidebox.delete('1.0',END)
#    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'r')
#    account_info = account_info_encrypted.read()
    c.execute(f"SELECT information FROM accounts WHERE name='{file_name}'")
    account_info = c.fetchone()
    account_info = account_info[0]
    #Checks for the key, decodes if key exists
    if len(master_key_str) > 0:
        if encryption == 'BASE64':
            if type(account_info) is str:
                account_info = decode(master_key_str,account_info)
        elif encryption == 'AES':
            if type(account_info) is bytes:
                account_info = aes_decode(account_info)
        sidebox.insert(END,account_info)
    else:
        print(account_info)
        sidebox.insert(END,account_info)



def rclick_menu_open(event):
        #Get selected item
        rightclick = event.widget
#        curItem = listmenu.focus()
#        item_dictionary = listmenu2.item(curItem)
#        item = item_dictionary["values"][0]
        #Get rowID
        rowID = listmenu2.identify('item', event.x, event.y)
        listmenu2.selection_set(rowID)
        listmenu2.focus((rowID))
        info_side_show(event)
#        widget = event.widget
#        index = widget.nearest(event.y)
#        _, yoffset, _, height = widget.bbox(index)
#        if event.y > height + yoffset + 5:  # XXX 5 is a niceness factor :)
            # Outside of widget.
#            return
        #value = rightclick.get(index)
        #Select item on right click
#        item = widget.get(index)
#        list_array = listmenu.get(0,END)
#        item_index = list_array.index(item)
#        listmenu.selection_clear(0,END)
#        listmenu.activate(item_index)
#        listmenu.selection_set(item_index,item_index)
#        print (f'\nOpening right click menu for: {item}')
#        rclick_menu.tk_popup(event.x_root+48, event.y_root+15, 0)
#        rclick_menu.grab_release()
#        rclick_menu.post(event.x_root, event.y_root)
        iid = listmenu2.identify_row(event.y)
        if iid:
            #mouse pointer over item
            listmenu2.selection_set(iid)
            rclick_menu.post(event.x_root, event.y_root)
        else:
            pass


def rclick_delete_item_window(item):
    warning_window_root = Toplevel()
    warning_window_root.focus()
    warning_window_root.title('Warning')
    warning_window_root.geometry('300x125+1100+630')
    warning_window_root.resizable(width=False,height=False)
    warninglabel = Label(warning_window_root, text='Are you sure you want to delete this item?')
    warninglabel.grid(padx=(40,0),pady=(45,0))
    yes_button = Button(warning_window_root,text='Yes',width=10,command=lambda:delete_item(current_selected_item,warning_window_root))
    yes_button.grid(row=1,padx=(0,110),pady=(20,0))
    no_button = Button(warning_window_root,text='No',width=10,command=lambda:warning_window_root.destroy())
    no_button.grid(row=1,padx=(180,0),pady=(20,0))


def delete_item(current_selected_item,window):
    print(f'Deleting {current_selected_item}')
    c.execute(f"DELETE FROM accounts WHERE name='{current_selected_item}'")
    connection.commit()
 #   if os.path.isfile(f'{document_path}//{current_selected_item}.txt'):
 #       os.remove(f'{document_path}//{current_selected_item}.txt')
 #       print('Item has been removed')
 #   else:
 #       print('Error file not found')
    window.destroy()
    reload_list(view_entries(), searchentry, reload=1)



def rename_item(event):
    pass




##################################################################################################################
##############################START GUI CREATION##################################################################
#Top menu setup
topmenu = Menu(root)
root.config(menu=topmenu)




#Rightclick menu for every item
rclick = Menu(root)
rclick_menu = Menu(rclick, tearoff=False)
#rclick_menu.add_command(label='Rename')
rclick_menu.add_command(label='Edit', command=lambda:entry_window(current_selected_item))
rclick_menu.add_command(label='Delete', command=lambda:rclick_delete_item_window(current_selected_item))


#File
submenu = Menu(topmenu,tearoff=False)
topmenu.add_cascade(label="File",menu=submenu)
submenu.add_command(label="Settings",command=lambda:settings(document_path))
submenu.add_separator()
submenu.add_command(label="Create Key File",command=create_key_file_window)
submenu.add_separator()
submenu.add_command(label="Information",command=info_popup)
#submenu.add_command(label="Exit",command=lambda:exit)
#Edit
submenu2 = Menu(topmenu,tearoff=False)
topmenu.add_cascade(label='Edit',menu=submenu2)
submenu2.add_command(label='New Account',command=new_account_window)
submenu2.add_command(label="Master Key",command=master_key_window)
#View
topmenu.add_cascade(label='View')


#Main listbox on root
def sort():
    print('potato')

listmenu = Listbox(root, height=19,width=100,setgrid=1,selectmode=SINGLE)
#listmenu.grid(row=1,column=0,rowspan=5,sticky=W,pady=(0,10))
#listmenu.config(yscrollcommand=scrollbar.set)
#listmenu.bind('<Double-Button-1>', entry_select)
#listmenu.bind('<<ListboxSelect>>', info_side_show)
#listmenu.bind('<Button-3>', rclick_menu_open)
scrollbar = Scrollbar(root)
scrollbar.grid(column=1,sticky=N+S,row=1,rowspan=5)
listmenu2 = ttk.Treeview(root,height=30)
listmenu2.config(yscrollcommand=scrollbar.set)
listmenu2["columns"] = ("Service","Encryption","Last Edited")
listmenu2["show"] = "headings"
listmenu2.heading('Service',text='Title',command=sort)
listmenu2.heading('Encryption',text='Encryption')
listmenu2.heading('Last Edited',text='Last Edited')
#listmenu2.column('Service', stretch=True)
#listmenu2.column('Encryption', stretch=True)
#listmenu2.column('Last Edited', stretch=True)
listmenu2.grid(row=1,column=0,sticky=N+W+S+E,pady=(0,1),rowspan=2)
scrollbar.config(command=listmenu2.yview)
listmenu2.bind('<Double-Button-1>',rename_item)
listmenu2.bind('<<TreeviewSelect>>', info_side_show)
listmenu2.bind('<Button-3>', rclick_menu_open)
listmenu2.column('Encryption', anchor='center')
listmenu2.column('Last Edited', anchor='center')




#Menu buttons creation and placement
#button1 = Button(text='View',width=15,height=1,relief=RAISED,overrelief=GROOVE,font=("TkDefaultDont", 11),command=lambda:)


#Auto generate list on start
#button1.invoke()
#reload_image = 'reload_big.png'
#the_reload_image = PhotoImage(file=reload_image)

#Search panel entry for text
searchlabel = Label(root,text='Search')
searchlabel.grid(row=6,sticky=W,pady=(10,10),padx=(10,10))
global searentry
searchentry = Entry(root,width=30)
searchentry.grid(row=6,pady=(10,10),sticky=W,padx=(60,0))
#Search panel clear button
#searchbutton = Button(root,width=5,text='Reload',command=lambda:reload_list(view_entries(),searchentry,reload=1))
#searchbutton.grid(row=6,pady=(0,10),sticky=W,padx=(255,0))
#Bind search panel events key presses, Enter, Backspace
searchentry.focus()
searchentry.bind('<BackSpace>', lambda x:check_if_search_empty(searchentry))
searchentry.bind('<KeyRelease>', lambda x:reload_list(view_entries(),searchentry,reload=0))

#Side view
sidebox = Text(root,width=26,height=17,borderwidth=1,relief=GROOVE,selectborderwidth=1)
sidebox.grid(columnspan=3,rowspan=2,column=2,row=1,padx=(0,10),sticky=N+W+S+E,pady=(0,0))

#Bottom status bar
statustext = Label(root, bd=1, relief=SUNKEN,anchor=E)
statustext.grid(sticky=W+E,columnspan=6)


#Toolbar
button_image = 'key3.png'
image_for_button = PhotoImage(file=button_image)
#image_for_button = image_for_button.zoom(9)
#image_for_button = image_for_button.subsample(60)

setting_image = 'gears2.png'
image_for_button2 = PhotoImage(file=setting_image)

add_image = 'plus2.png'
image_for_button3 = PhotoImage(file=add_image)

toolbar = Frame(root)
toolbar.grid(row=0,sticky=E+W)
key_button = Button(toolbar,image=image_for_button,width=32,height=30,relief=GROOVE, command=master_key_window)
key_button.grid(sticky=W,padx=(1,0))
setting_button = Button(toolbar,image=image_for_button2,width=32,height=30,relief=GROOVE,command=lambda:settings(document_path,sqlite_file))
setting_button.grid(sticky=W,padx=(1,0),column=2,row=0)
add_button = Button(toolbar,image=image_for_button3,width=32,height=30,relief=GROOVE,command=new_account_window)
add_button.grid(sticky=W,padx=(1,0),column=1,row=0)


#Change icon
root.iconbitmap('safekey.ico')

root.grid_columnconfigure(0,weight=1)
#root.grid_columnconfigure(1,weight=1)
root.grid_columnconfigure(2,weight=1)
root.grid_columnconfigure(4,weight=1)
#root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)

#Resize event
#root.bind("<Configure>", resize)
root.protocol("WM_DELETE_WINDOW", dump_geometry)
#root.bind("<Configure>", dump_position)

#Show GUI
status_update(master_key_str,found_amount=0,search_update=0)

#Show the change encryption button1
with open(f'sfky_cnfg.pkl', 'rb') as config_file:
    config_elements = pickle.load(config_file)
    encryption = config_elements['encryption_format']
stringvar = tkinter.StringVar()
options = ['AES','BASE64']
stringvar.set(encryption)
dropdown = OptionMenu(root,stringvar,*options,command=lambda x:change_encryption(key_file_path,stringvar,key_file=0,enc_change=1))
dropdown.configure(width=6)
dropdown.grid(row=0,column=4,sticky=E,padx=(0,9))
#encryption_label = Label(file_window_root, text='Encryption Type')
#encryption_label.grid(row=3,column=0,sticky=E)

#Select first item and show its contents
#listmenu.selection_set(0,0)
#listmenu.activate(0)
view_entries()
items = [listmenu2.get_children()]
sg = ttk.Sizegrip(root)
sg.grid(row=7,column=4,sticky=E)
try:
    listmenu2.selection_set(f'{items[0][0]}')
    listmenu2.focus(f'{items[0][0]}')
    listmenu2.event_generate('<<TreeviewSelect>>')
except:
    pass




root.mainloop()
=======
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
import pickle
import glob
import base64
import os
import sqlite3
import datetime
#pip install pycryptodomex
from Cryptodome import Random
from Cryptodome.Cipher import AES
#already installed
import hashlib
from tkinter import ttk
import uuid
import subprocess

#What to add:
#Add folder / category creation
#Add min size for the window
#Add backup to gdrive / onedrive
#redesign settings menu (again)

#Main Window
root = Tk()
root.title('SafeKey Password Manager')
root.grid_propagate(False)
#root.minsize(width=846,height=400)

#Generate a unique IV from the Computer UUID
def iv_from_uuid():
    i = 0
    the_iv = ''
    iv = str(subprocess.check_output('wmic csproduct get UUID'))
    for letter in iv:
        i = i+1
        if i > 46 and letter != '-':
            the_iv = the_iv + letter
    print(the_iv)
    the_iv = the_iv[:16]
    the_iv = the_iv.encode()
    return(the_iv)

#Check if config file exists
def load_settings():
    #Check if settings file exists and if not, create it. if exists proceed to look over it
    if os.path.isfile('sfky_cnfg.pkl'):
        config_file = open('sfky_cnfg.pkl', 'rb')
        config_file.close()
    else:
        #iv = Random.new().read(AES.block_size)
        iv = iv_from_uuid()
#        os.makedirs('accounts')
        current_directory = os.getcwd()
        config_file = open('sfky_cnfg.pkl', 'wb')
        config_elements = {'file_location':f'db.sqlite',
                           'master_key':'key_string',
                           'key_file_location':'file_path',
                           'use_key_file':'false',
                           'key_type':'None',
                           'encryption_format':'BASE64',
                           'aes_iv':iv,
                           'geometry':'100x19+900+520',
                           'width':'846',
                           'height':'400',
                           'x_pos':'x',
                           'y_pos':'y'
                           }
        pickle.dump(config_elements,config_file)
        config_file.close()
    #Check if folder location has been set
    print('\n===Settings===')
    print(f'Loading config file: sfky_cnfg.pkl')
    with open('sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
    document_path = config_elements['file_location']
#    if document_path == 'db.sqlite':
#        print('File location is not set, switching to default directory')
#        current_directory = os.getcwd()
#        document_path = f'{current_directory}\\accounts'
#    else:
#        print(f'File location set: {document_path}')
    #check to see wheather to use the the key from the file
    if config_elements["use_key_file"] == True and config_elements["master_key"] != 'key_string':
        master_key_str = config_elements["master_key"]
    else:
        master_key_str = ''
    global geometry,width,height,encryption,key_file_path,window_x,window_y
    geometry = config_elements["geometry"]
    width = config_elements["width"]
    height = config_elements["height"]
    encryption = config_elements["encryption_format"]
    key_file_path = config_elements["key_file_location"]
    window_x = config_elements["x_pos"]
    window_y = config_elements["y_pos"]
    print(f'Database file: {document_path}')
    print(f'Master key from file: {config_elements["master_key"]}')
    print(f'Key file location: {config_elements["key_file_location"]}')
    print(f'Encryption: {config_elements["encryption_format"]}')
    print(f'AES IV: {config_elements["aes_iv"]}')
    print(f'Use key file: {config_elements["use_key_file"]}')
    print(f'Key type: {config_elements["key_type"]}')
    print(f'Window Geometry: {config_elements["geometry"]}')
    print('===Settings===')
    config_file.close()
    return document_path,master_key_str,geometry


#Database variable definition
global sqlite_file
sqlite_file = load_settings()
sqlite_file = sqlite_file[0]

#Resize
root.geometry(f'{geometry}')
root.config(height=height,width=width)
root.update_idletasks()



#Connect to DB function
def database_connection(sqlite_file):
    global connection,c
    connection = sqlite3.connect(sqlite_file)
    c = connection.cursor()
    # Check if DB file is new and if not create the tables inside
    if os.stat(sqlite_file).st_size <= 0:
        print('DB file is empty, making necessary tables')
        c.execute(f'CREATE TABLE accounts (id INTEGER PRIMARY KEY,name TEXT,information TEXT,encryption TEXT, last_edit TEXT)')
        connection.commit()
#run the DB function
database_connection(sqlite_file)

#define global variables
#global document_path
#document_path = load_settings()
#document_path = document_path[0]
document_path = ''
global master_key_str
master_key_str = load_settings()
master_key_str = master_key_str[1]

current_selected_item = ''
current_selected_item_index = ''


#vigenere cypher start encode and decode functions
def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

#aes encryption functions
def aes_encode(message):
    with open('sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
    iv = config_elements["aes_iv"]
    obj = AES.new(master_key_str, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))


def aes_decode(cipher):
    with open('sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
    iv = config_elements["aes_iv"]
    obj2 = AES.new(master_key_str, AES.MODE_CFB, iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))


def view_entries():
    #New SQL database code, fetch entry names from DB.sqlite file
    global selection_array
    selection_array = []
    c.execute('SELECT name,information,encryption,last_edit FROM accounts')
    name_row = c.fetchall()
    for name in name_row:
        selection_array.append(name[0])
#       listmenu.insert(END, name[0])
        listmenu2.insert('','end',values=(f'{name[0]}',f'{name[2]}',f'{name[3]}'))
    return selection_array


#This is for listbox
#def entry_select(event):
#    list = listmenu.get(0)
#    if list == '':
#        pass
#    else:
#        doubleclick = event.widget
#        index = int(doubleclick.curselection()[0])
#        value = doubleclick.get(index)
#        print (f'\nYou selected item {value}')
#        entry_window(value)
        #gloval variables for the selected item and its index in the list

#This runs whenever you click on an entry, for treeview not listbox
#def selectItem():
#    #Gets the item that is currently focused
#    curItem = listmenu2.focus()
#    item_dictionary = listmenu2.item(curItem)
#    value = item_dictionary["values"][0]
#    print(f'\nYou selected item {value}')
#Opens up a window with the info inside to edit and save
#    entry_window(value)


def entry_window(file_name):
    entry_window_root = Toplevel(root)
    entry_window_root.title(f'Entry Information: {file_name}')
    entry_window_root.resizable(width=False,height=False)
    entry_window_root.geometry('495x320+902+600')
    #Entry Field and placement
    e = Entry(entry_window_root,width=50)
    e.grid(column=0,row=0,sticky=W,padx=(5,5),pady=(5,2))
    e.insert(END, file_name)
    stringvar = tkinter.StringVar()
    options = ['AES','BASE64']
    stringvar.set(options[1])
    dropdown = OptionMenu(entry_window_root,stringvar,*options)
    dropdown.configure(width=6)
    dropdown.grid(row=0,column=0,sticky=E,padx=(0,5),pady=5)
    account_field = Text(entry_window_root,width=60,height=15)
    account_field.grid(sticky=W,padx=(5,5))
    account_field.focus_force()
    account_field.config(state=NORMAL)
    #button label and placement
    update_account_button = Button(entry_window_root,text='Update',width=13,command=lambda:update_entry(e,file_name,account_field,update_account_button,entry_window_root))
    update_account_button.grid(sticky=S+E,padx=(5,5),pady=(2,2),column=0,row=2)
    #Fetch info from file after decoding
#    print(f'Fetching {document_path}//{file_name}.txt')
#    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'r')
#    account_info = account_info_encrypted.read()
    c.execute(f"SELECT information FROM accounts WHERE name = '{file_name}'")
    account_info = c.fetchone()
    account_info = account_info[0]
    #Checks for the key
    if len(master_key_str) > 0:
        account_info = decode(master_key_str,account_info)
        account_field.insert(END,account_info)
    else:
        print(account_info)
        account_field.insert(END,account_info)
        update_account_button.config(state=DISABLED)
#    account_info_encrypted.close()


def update_entry(name_entry,file_name,account_field,update_account_button,entry_window_root):
    new_name = name_entry.get()
    new_text = account_field.get(1.0,END)
    new_text_encrypted = encode(master_key_str, new_text)
#    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'w')
#    account_info_encrypted.write(new_text_encrypted)
#    account_info_encrypted.close
    now = datetime.datetime.now()
    current_time = f'{now.day}/{now.month}/{now.year}'
    c.execute(f"UPDATE accounts SET information='{new_text_encrypted}' WHERE name='{file_name}'")
    c.execute(f"UPDATE accounts SET last_edit='{current_time}' WHERE name='{file_name}'")
    c.execute(f"UPDATE accounts set name='{new_name}' WHERE name='{file_name}'")
    connection.commit()
    update_account_button.config(text='Done')
    print(f'Updating info with {new_text_encrypted}')
    #Stupid list magic, seriously I dont know why this is even necessary but it is because the list changes after the list gets reloaded, srsly? why??
    selected_item = listmenu2.selection()[0]
    all_items = listmenu2.get_children()
    selected_item_index = all_items.index(selected_item)
    #Check if the search is empty, if its not then do a reload
    reload_list(view_entries(), searchentry, reload=0)
    all_items = listmenu2.get_children()
    selected_item = all_items[selected_item_index]
    listmenu2.see(selected_item)
    listmenu2.selection_set(selected_item)
    listmenu2.focus(selected_item)
    #End list magic
    close_window(entry_window_root, current_selected_item, current_selected_item_index)




#Settings window start==================================================================================================


#Function name should get changed to database_select, too lazy to change it. Will eventually.
def folder_select(file_entry):
    #Ask to select folder where to look for files
    global document_path
    current_directory = os.getcwd()
    document_path = filedialog.askopenfilename()
    if document_path == '':
        document_path = f'{current_directory}\\db.sqlite'
    file_entry.delete(0, END)
    file_entry.insert(0,document_path)
    file_entry.focus()
    #Output the db file location to a dictionary to reload on future launch
    with open(f'sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
        config_elements['file_location'] = document_path
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    config_file.close()
    database_connection(sqlite_file=document_path)
    reload_list(view_entries(), searchentry, reload=1)
#   return document_path


def settings(document_path,sqlite_file):
    x = recalc_position()[0]
    y = recalc_position()[1]
    file_window_root = Toplevel(root)
    file_window_root.title('Settings')
    file_window_root.resizable(width=False,height=False)
    file_window_root.geometry(f'577x125+{x}+{y}')
    #Entry Field and placement
    file_entry = Entry(file_window_root,width=60)
    file_entry.focus()
    #Fill in file path with current into stored inside the sfky_cnfg.pkl file
    file_entry.insert(0, sqlite_file)
    file_entry.grid(sticky=E,row=0,column=1,pady=(2,2),padx=(5,5))
    #Button Label and placement
    file_label = Label(file_window_root, text="Database file")
    file_label.grid(sticky=E,row=0,pady=(2,2))
    #Button and placement
    file_button = Button(file_window_root, text="Browse",width=11,command=lambda:folder_select(file_entry))
    file_button.grid(sticky=W,row=0,column=2,pady=(2,2))
    file_window_root.focus_force()
    #use a key file
    key_location_label = Label(file_window_root, text='Master Key file')
    key_location_label.grid(sticky=E,row=1)
    key_location_entry = Entry(file_window_root,width=60)
    key_location_entry.grid(sticky=W,row=1,column=1,pady=(8,10),padx=(5,5))
    key_file_button = Button(file_window_root, text='Browse',width=11,command=lambda:key_select(key_location_entry,stringvar,enc_change=0))
    key_file_button.grid(sticky=W, row=1,column=2)
    #Select encryption type
    #with open(f'sfky_cnfg.pkl', 'rb') as config_file:
    #    config_elements = pickle.load(config_file)
    #    encryption = config_elements['encryption_format']
    #stringvar = tkinter.StringVar()
    #options = ['AES','BASE64']
    #stringvar.set(encryption)
    #dropdown = OptionMenu(file_window_root,stringvar,*options,command=lambda x:change_encryption(key_location_entry,stringvar,file_window_root,checkbox,key_file=0,enc_change=1))
    #dropdown.configure(width=6)
    #dropdown.grid(row=3,column=1,sticky=W,padx=(2,0))
    #encryption_label = Label(file_window_root, text='Encryption Type')
    #encryption_label.grid(row=3,column=0,sticky=E)
    #select if to use key file on load
    checkbox_value = IntVar()
    checkbox_label = Label(file_window_root, text='Use key file on boot')
    checkbox_label.grid(row=2,column=0,sticky=E)
    checkbox = Checkbutton(file_window_root, variable=checkbox_value,command=lambda:checkbox_action(checkbox_value))
    checkbox.grid(row=2,column=1,sticky=W)
    #checkoff the checkbox with the info stored in the config file
    with open(f'sfky_cnfg.pkl', 'rb') as config_file:
        config_elements = pickle.load(config_file)
        if config_elements['use_key_file'] == True:
            checkbox.select()
        else:
            checkbox.deselect()
        if config_elements['key_file_location'] != 'file_path':
            key_location_entry.insert(0, config_elements['key_file_location'])
        else:
            pass
    apply_button = Button(file_window_root, text="Ok",width=11,command=lambda:close_window(file_window_root,current_selected_item,current_selected_item_index))
    apply_button.grid(row=4,column=2)




def change_encryption(key_location_entry,stringvar,key_file,enc_change):
    global encryption,master_key_str
    #If encryption is being changed by button then reset all settings
    if enc_change == 1:
        master_key_str = ''
        tkinter.messagebox.showinfo('SafeKey Password Manager','Encryption type has been changed, the master key has been reset. Please enter new master key or select a key file.')
        #file_window_root.focus()
        #Change key file back to null
        key_select(key_location_entry,stringvar,enc_change=1)
        #Set checkox back to null
        #checkbox.deselect()
        checkbox_value = IntVar()
        checkbox_value.set(0)
        checkbox_action(checkbox_value)
        encryption_type = stringvar.get()
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['encryption_format'] = encryption_type
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        encryption = encryption_type
        print(f'\n\nEncryption changed to: {encryption_type}')
    #If encryption is being changed by file change settings accordingly
    elif enc_change == 0:
        #Remove key when switching encryption
        if master_key_str != '' and key_file == 0:
            master_key_str = ''
            tkinter.messagebox.showinfo('SafeKey Password Manager','Encryption type has been changed, the master key has been reset. Please enter new master key or select a key file.')
            #file_window_root.focus()
        encryption_type = stringvar.get()
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['encryption_format'] = encryption_type
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        encryption = encryption_type
        print(f'\n\nEncryption changed to: {encryption_type}')
    status_update(master_key_str,found_amount=0,search_update=0)
    global encryption_change




def checkbox_action(checkbox_value):
    value = checkbox_value.get()
    if value == 1:
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['use_key_file'] = True
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        print(f'Use_Key_File set to: {config_elements["use_key_file"]}')
        config_file.close()
    elif value == 0:
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['use_key_file'] = False
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
        print(f'Use_Key_File set to: {config_elements["use_key_file"]}')
        config_file.close()


def key_select(key_location_entry,stringvar,enc_change):
    if enc_change == 0:
        global master_key_str
        key_path = filedialog.askopenfilename()
        if key_path == '':
            key_path = 'file_path'
        if key_path != 'file_path':
            key_location_entry.insert(0, key_path)
        key_location_entry.focus()
    #    try:
            #grab info from the key file
        with open(f'{key_path}', 'rb') as key_file:
            key_properties = pickle.load(key_file)
            if 'AES' in key_properties:
                master_key_str = key_properties['AES']
                key_type = 'AES'
            elif 'BASE64' in key_properties:
                master_key_str = key_properties['BASE64']
                key_type = 'BASE64'
        stringvar.set(key_type)
        change_encryption(key_location_entry,stringvar,key_file=1,enc_change=0)
            #dump info into config file
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['key_file_location'] = key_path
            config_elements['master_key'] = master_key_str
            config_elements['key_type'] = key_type
            config_elements['Encryption'] = key_type
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)
    #        config_file.close()
        print(f'\nLoading key: {master_key_str}')
        status_update(master_key_str, found_amount=0, search_update=0)
    #    except:
    #        print('Key location not chosen')
    #        pass
        return master_key_str
    elif enc_change == 1:
        #key_location_entry.delete(0, 'end')
        with open(f'sfky_cnfg.pkl', 'rb') as config_file:
            config_elements = pickle.load(config_file)
            config_elements['key_file_location'] = 'file_path'
            config_elements['master_key'] = 'key_string'
            config_elements['key_type'] = 'None'
            config_elements['Encryption'] = stringvar.get()
        with open(f'sfky_cnfg.pkl', 'wb') as config_file:
            pickle.dump(config_elements, config_file)


def create_key_file_window():
    key_window_root = Toplevel(root)
    key_window_root.title('Create Encryption Key File')
    key_window_root.resizable(width=False, height=False)
    key_window_root.geometry('545x73+902+605')
    key_window_root.focus()
    key_label = Label(key_window_root,text='Key String')
    key_label.grid(padx=(5,10),pady=(5,10))
    key_text_entry = Entry(key_window_root,width=60)
    key_text_entry.insert(0,master_key_str)
    key_text_entry.grid(padx=(3,10),pady=(8,10),column=1,row=0,sticky=W)
    key_text_entry.focus()
    key_format = Label(key_window_root,text='Encryption')
    key_format.grid(row=1)
    submit_button = Button(key_window_root,text='Create',width=11,command=lambda:create_key_file(key_window_root,key_text_entry,stringvar))
    submit_button.grid(column=2,row=0,padx=(0,50))
#   create_button = Button(key_window_root,text='Create',width=15)
#   create_button.grid(column=2,row=1,sticky=W)
    stringvar = tkinter.StringVar()
    options = ['AES','BASE64']
    dropdown = OptionMenu(key_window_root,stringvar,*options)
    stringvar.set(options[1])
    dropdown.configure(width=6)
    dropdown.grid(row=1,column=1,sticky=W)
    #Check if key field is empty
    check_if_key_field_empty(submit_button, key_text_entry)
    key_text_entry.bind("<KeyRelease>", lambda x:check_if_key_field_empty(submit_button,key_text_entry))


def check_if_key_field_empty(submit_button,key_text_entry):
    key_text_entry = key_text_entry.get()
    if len(key_text_entry) > 0:
        submit_button.config(state=NORMAL)
    else:
        submit_button.config(state=DISABLED)


def create_key_file(window,key_text_entry,encryption):
    encryption = encryption.get()
    master_key_str = key_text_entry.get()
    if encryption == 'AES':
        #Convert to byte value and add padding to the key
        password = master_key_str.encode()
        master_key_str = hashlib.sha256(password).digest()
    elif encryption == 'BASE64':
        master_key_str = str(master_key_str)
    print(f'\nCreating key file with string: {master_key_str}')
    selected_folder_path = filedialog.askdirectory()
    file = open(f'{selected_folder_path}//{encryption}_safekey.pkl', 'wb')
    key_with_encryption = {f'{encryption}':master_key_str}
    pickle.dump(key_with_encryption, file)
    file.close()
    window.destroy()
    tkinter.messagebox.showinfo('SafeKey Password Manager',f'{encryption} Master Key file created.')
    print(f'{encryption} Master key file created.')


def resize():
    root.update_idletasks()
    geometry = root.winfo_geometry()
    width = root.winfo_width()
    height = root.winfo_height()
    return geometry,width,height

#Get the position and the width and length of the window right before it gets closed to save for letter
def dump_geometry():
    geometry = resize()
    geometry = geometry[0]
    window_width = resize()
    window_width = window_width[1]
    window_height = resize()
    window_height = window_height[2]
    print(f'Dumping window size and position: {geometry}')
    with open(f'sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
        config_elements['geometry'] = geometry
        config_elements['height'] = window_height
        config_elements['width'] = window_width
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    root.destroy()

#Check the position of the window every time it is moved
def dump_position():
    window_x = root.winfo_x()
    window_y = root.winfo_y()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    #print(f'x: {window_x} y: {window_y}')
    with open(f'sfky_cnfg.pkl','rb') as config_file:
        config_elements['x_pos'] = window_x
        config_elements['y_pos'] = window_y
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    return window_x,window_y,window_width,window_height

#Settings window end==================================================================================================

def close_window(window_root,current_selected_item,current_selected_item_index):
    if len(current_selected_item) <= 0:
        window_root.destroy()
        pass
    else:
        try:
#    reload_list(view_entries(document_path), searchentry, reload=1)
            window_root.destroy()
         #reload the current list and select the previously selected item or different item
#        listmenu.selection_clear(0, END)
#        listmenu.selection_set(current_selected_item_index,current_selected_item_index)
#        listmenu.activate(current_selected_item_index)
            mirror_info_to_side(current_selected_item)
#        listmenu.see(current_selected_item_index)
        except:
            pass



def close_window_and_input_key(key_entry,key_button,key_window_root):
    master_key(key_entry,key_button)
    close_window(key_window_root,current_selected_item,current_selected_item_index)


def recalc_position():
    position = dump_position()
    #Get new x-coordinate
    width_adj = int(position[2]) / 3.5
    x = str(round(int(position[0]) + width_adj))
    #Get new y-coordinate
    height_adj = int(position[3]) / 2.4
    y = str(round(int(position[1]) + height_adj))
    return x,y


def master_key_window():
    #grab x,y coordinates relative to size and position of main window
    x = recalc_position()[0]
    y = recalc_position()[1]
    key_window_root = Toplevel(root)
    key_window_root.title('Input Master Key')
    key_window_root.resizable(width=False,height=False)
    key_window_root.geometry(f'531x30+{x}+{y}')
    #Button Label and placement
    key_label = Label(key_window_root, text="Master Key: ")
    key_label.grid(sticky=E,row=0,pady=(2,2),)
    #Entry Field and placement
    key_entry = Entry(key_window_root,width=60)
    key_entry.grid(sticky=E,row=0,column=1,pady=(2,2),padx=(0,1))
    key_entry.focus()
    key_entry.bind('<Return>', lambda x:close_window_and_input_key(key_entry,key_button,key_window_root))
    #Button and placement
    key_button = Button(key_window_root, text="Submit",width=11,command=lambda:close_window_and_input_key(key_entry,key_button,key_window_root))
    key_button.grid(sticky=W,row=0,column=2,pady=(2,2),padx=(5,10))
    #Close window event
    key_window_root.protocol("WM_DELETE_WINDOW", lambda:close_window(key_window_root,current_selected_item,current_selected_item_index))
    key_window_root.bind('<Escape>', lambda x:close_window(key_window_root,current_selected_item,current_selected_item_index))


def master_key(key_entry,key_button):
    global master_key_str
    if encryption == 'BASE64':
        #Grab key from the entry field and change the button text and color
        master_key_str = key_entry.get()
        key_button.config(text="Done")
    elif encryption == 'AES':
        master_key_str = key_entry.get()
        master_key_str = master_key_str.encode()
        #Add padding to the key
        master_key_str = hashlib.sha256(master_key_str).digest()
    status_update(master_key_str,found_amount=0,search_update=0)
    print(f'Encoded master key: {master_key_str}')
    return master_key_str



def info_popup():
    tkinter.messagebox.showinfo('SafeKey Password Manager','Created by Ilya Shevchenko, 2018 \nPlease report any bugs to ilya.93@hotmail.com')


def reload_list(selection_array,searchentry,reload):
    search_update = 1
    #Clear search bar if reloading
    if reload == 1:
        searchentry.delete(0,END)
    search_word = searchentry.get()
    selection_array = [ x.lower() for x in selection_array ]
    found_items = [item for item in selection_array if search_word in item]
    if len(found_items) == 0:
        print('No account infos found')
        update_listbox(found_items)
    status_update(master_key_str,len(found_items),search_update)
    update_listbox(found_items)
#    listmenu.selection_set(0,0)
#    listmenu.activate(0)
    items = [listmenu2.get_children()]
    try:
        listmenu2.selection_set(f'{items[0][0]}')
        listmenu2.focus(f'{items[0][0]}')
        if reload == 1:
            listmenu2.see(f'{items[0][0]}')
        listmenu2.event_generate('<<TreeviewSelect>>')
    except:
        pass

def update_listbox(selection_array):
#    listmenu.delete(0, END)
    listmenu2.delete(*listmenu2.get_children())
    if len(selection_array) == 0:
        listmenu2.delete(*listmenu2.get_children())
    else:
        for item in selection_array:
            c.execute(f"SELECT last_edit FROM accounts WHERE name = '{item}'")
            edit_date = c.fetchone()
            edit_date = edit_date[0]
            c.execute(f"SELECT encryption FROM accounts WHERE name = '{item}'")
            encryption_select = c.fetchone()
            encryption_select = encryption_select[0]
            listmenu2.insert('', 'end', values=(f'{item}', f'{encryption_select}', f'{edit_date}'))


def status_update(master_key,found_amount,search_update):
    encryption_update = f'Encryption: {encryption},  '
    if master_key != '' and search_update == 0:
        status = f'{encryption_update}Master Key Loaded     '
        statustext.config(text=status,fg='green')
    elif master_key == '' and search_update == 0:
        status = f'{encryption_update}No Master Key     '
        statustext.config(text=status,fg='red')
    elif found_amount >= 0 and search_update == 1:
        print(f'{encryption_update}Found {found_amount} entries     ')
        status = f'{encryption_update}Found {found_amount} Entries     '
        statustext.config(text=status,fg='black')


def check_if_search_empty(searchentry):
        if len(searchentry.get()) == 1:
            print('Search is empty, refreshing.')
            reload_list(view_entries(), searchentry,reload=0)
        else:
            pass


#New account panel
def new_account_window():
    x = recalc_position()[0]
    y = recalc_position()[1]
    newpanel = Toplevel(root)
    newpanel.resizable(width=False,height=False)
    newpanel.geometry(f'330x158+{x}+{y}')
    namelabel = Label(newpanel,text='Service:')
    namelabel.grid(row=1,padx=(31,0))
    label2 = Label(newpanel,text='Information:')
    label2.grid(row=2,padx=(5,0),sticky=N)
    servicelabel_entry = Entry(newpanel, width=40)
    servicelabel_entry.focus()
    servicelabel_entry.grid(row=1,column=1,padx=(1,1),pady=(1,0))
    entrybox = Text(newpanel,width=30,height=6)
    entrybox.grid(column=1,row=2,pady=(1,0))
    servicebutton = Button(newpanel,text='Submit',command=lambda:create_entry(servicelabel_entry,entrybox,servicebutton,newpanel,encryption,selection_array))
    servicebutton.grid(row=3,column=1,padx=(197,5),pady=(5,5))
    if len(master_key_str) == 0:
        servicebutton.config(state=DISABLED)



def create_entry(servicelabel_entry,entrybox,servicebutton,window,encryption,selection_array):
    now = datetime.datetime.now()
    now_time = f'{now.day}/{now.month}/{now.year}'
    service_name = servicelabel_entry.get()
    if service_name in selection_array:
        print('Entry with that name already exists')
        #Fnd the existing entry and select it to show that it exists
        iid_selection_array = listmenu2.get_children()
        i = selection_array.index(service_name)
        listmenu2.selection_set(iid_selection_array[i])
        listmenu2.focus(iid_selection_array[i])
        listmenu2.see(iid_selection_array[i])
        tkinter.messagebox.showinfo('SafeKey Password Manager','ERROR: Entry with this name already exists.')
    else:
        service_information = entrybox.get('1.0', END)
        print(f'Encryption type: {encryption}')
        if encryption == 'BASE64':
            service_information_encoded = encode(master_key_str,service_information)
        elif encryption == 'AES':
            service_information_encoded = aes_encode(service_information)
        print(f'Created String: {service_information_encoded}')
        #new_file = open(f'{document_path}/{service_name}.txt', 'w+')
        #new_file.write(service_information_encoded)
        #new_file.close()
        #SQL
        connection.execute("INSERT INTO accounts (name,information,encryption,last_edit) VALUES (?,?,?,?)",(service_name,service_information_encoded,encryption,now_time))
        connection.commit()
        #SQL
        servicebutton.config(text='Done')
        servicelabel_entry.delete(0,END)
        entrybox.delete('1.0',END)
        #Find newly added entry and select it
        reload_list(view_entries(), searchentry, reload=0)
        items = [listmenu2.get_children()]
        listmenu2.selection_set(items[0][-1])
        listmenu2.focus(items[0][-1])
        listmenu2.event_generate('<<TreeviewSelect>>')
        listmenu2.see(items[0][-1])
    #    all_entries = [ listmenu.get(0, END) ]
    #    all_entries = all_entries[0]
    #    new_file_index = all_entries.index(service_name)
    #    print(f'Selecting entry number {new_file_index}')
    #    close_window(window,current_selected_item=service_name)


#Side account info panel code
def info_side_show(event):
#    try:
#        click = event.widget
#        index = int(click.curselection()[0])
#        value = click.get(index)
#        print(f'\nYou selected item {value}')
#        mirror_info_to_side(value)
#        global current_selected_item,current_selected_item_index
#        current_selected_item = value
#        current_selected_item_index = index
#    except IndexError:
#        pass
    try:
        curItem = listmenu2.focus()
        item_dictionary = listmenu2.item(curItem)
        value = item_dictionary["values"][0]
        mirror_info_to_side(value)
        global current_selected_item,current_selected_item_index
        current_selected_item = value
        current_selected_item_index = selection_array.index(value)
    except IndexError:
        pass



def mirror_info_to_side(file_name):
    sidebox.delete('1.0',END)
#    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'r')
#    account_info = account_info_encrypted.read()
    c.execute(f"SELECT information FROM accounts WHERE name='{file_name}'")
    account_info = c.fetchone()
    account_info = account_info[0]
    #Checks for the key, decodes if key exists
    if len(master_key_str) > 0:
        if encryption == 'BASE64':
            if type(account_info) is str:
                account_info = decode(master_key_str,account_info)
        elif encryption == 'AES':
            if type(account_info) is bytes:
                account_info = aes_decode(account_info)
        sidebox.insert(END,account_info)
    else:
        print(account_info)
        sidebox.insert(END,account_info)



def rclick_menu_open(event):
        #Get selected item
        rightclick = event.widget
#        curItem = listmenu.focus()
#        item_dictionary = listmenu2.item(curItem)
#        item = item_dictionary["values"][0]
        #Get rowID
        rowID = listmenu2.identify('item', event.x, event.y)
        listmenu2.selection_set(rowID)
        listmenu2.focus((rowID))
        info_side_show(event)
#        widget = event.widget
#        index = widget.nearest(event.y)
#        _, yoffset, _, height = widget.bbox(index)
#        if event.y > height + yoffset + 5:  # XXX 5 is a niceness factor :)
            # Outside of widget.
#            return
        #value = rightclick.get(index)
        #Select item on right click
#        item = widget.get(index)
#        list_array = listmenu.get(0,END)
#        item_index = list_array.index(item)
#        listmenu.selection_clear(0,END)
#        listmenu.activate(item_index)
#        listmenu.selection_set(item_index,item_index)
#        print (f'\nOpening right click menu for: {item}')
#        rclick_menu.tk_popup(event.x_root+48, event.y_root+15, 0)
#        rclick_menu.grab_release()
#        rclick_menu.post(event.x_root, event.y_root)
        iid = listmenu2.identify_row(event.y)
        if iid:
            #mouse pointer over item
            listmenu2.selection_set(iid)
            rclick_menu.post(event.x_root, event.y_root)
        else:
            pass


def rclick_delete_item_window(item):
    warning_window_root = Toplevel()
    warning_window_root.focus()
    warning_window_root.title('Warning')
    warning_window_root.geometry('300x125+1100+630')
    warning_window_root.resizable(width=False,height=False)
    warninglabel = Label(warning_window_root, text='Are you sure you want to delete this item?')
    warninglabel.grid(padx=(40,0),pady=(45,0))
    yes_button = Button(warning_window_root,text='Yes',width=10,command=lambda:delete_item(current_selected_item,warning_window_root))
    yes_button.grid(row=1,padx=(0,110),pady=(20,0))
    no_button = Button(warning_window_root,text='No',width=10,command=lambda:warning_window_root.destroy())
    no_button.grid(row=1,padx=(180,0),pady=(20,0))


def delete_item(current_selected_item,window):
    print(f'Deleting {current_selected_item}')
    c.execute(f"DELETE FROM accounts WHERE name='{current_selected_item}'")
    connection.commit()
 #   if os.path.isfile(f'{document_path}//{current_selected_item}.txt'):
 #       os.remove(f'{document_path}//{current_selected_item}.txt')
 #       print('Item has been removed')
 #   else:
 #       print('Error file not found')
    window.destroy()
    reload_list(view_entries(), searchentry, reload=1)



def rename_item(event):
    pass




##################################################################################################################
##############################START GUI CREATION##################################################################
#Top menu setup
topmenu = Menu(root)
root.config(menu=topmenu)




#Rightclick menu for every item
rclick = Menu(root)
rclick_menu = Menu(rclick, tearoff=False)
#rclick_menu.add_command(label='Rename')
rclick_menu.add_command(label='Edit', command=lambda:entry_window(current_selected_item))
rclick_menu.add_command(label='Delete', command=lambda:rclick_delete_item_window(current_selected_item))


#File
submenu = Menu(topmenu,tearoff=False)
topmenu.add_cascade(label="File",menu=submenu)
submenu.add_command(label="Settings",command=lambda:settings(document_path))
submenu.add_separator()
submenu.add_command(label="Create Key File",command=create_key_file_window)
submenu.add_separator()
submenu.add_command(label="Information",command=info_popup)
#submenu.add_command(label="Exit",command=lambda:exit)
#Edit
submenu2 = Menu(topmenu,tearoff=False)
topmenu.add_cascade(label='Edit',menu=submenu2)
submenu2.add_command(label='New Account',command=new_account_window)
submenu2.add_command(label="Master Key",command=master_key_window)
#View
topmenu.add_cascade(label='View')


#Main listbox on root
def sort():
    print('potato')

listmenu = Listbox(root, height=19,width=100,setgrid=1,selectmode=SINGLE)
#listmenu.grid(row=1,column=0,rowspan=5,sticky=W,pady=(0,10))
#listmenu.config(yscrollcommand=scrollbar.set)
#listmenu.bind('<Double-Button-1>', entry_select)
#listmenu.bind('<<ListboxSelect>>', info_side_show)
#listmenu.bind('<Button-3>', rclick_menu_open)
scrollbar = Scrollbar(root)
scrollbar.grid(column=1,sticky=N+S,row=1,rowspan=5)
listmenu2 = ttk.Treeview(root,height=30)
listmenu2.config(yscrollcommand=scrollbar.set)
listmenu2["columns"] = ("Service","Encryption","Last Edited")
listmenu2["show"] = "headings"
listmenu2.heading('Service',text='Title',command=sort)
listmenu2.heading('Encryption',text='Encryption')
listmenu2.heading('Last Edited',text='Last Edited')
#listmenu2.column('Service', stretch=True)
#listmenu2.column('Encryption', stretch=True)
#listmenu2.column('Last Edited', stretch=True)
listmenu2.grid(row=1,column=0,sticky=N+W+S+E,pady=(0,1),rowspan=2)
scrollbar.config(command=listmenu2.yview)
listmenu2.bind('<Double-Button-1>',rename_item)
listmenu2.bind('<<TreeviewSelect>>', info_side_show)
listmenu2.bind('<Button-3>', rclick_menu_open)
listmenu2.column('Encryption', anchor='center')
listmenu2.column('Last Edited', anchor='center')




#Menu buttons creation and placement
#button1 = Button(text='View',width=15,height=1,relief=RAISED,overrelief=GROOVE,font=("TkDefaultDont", 11),command=lambda:)


#Auto generate list on start
#button1.invoke()
#reload_image = 'reload_big.png'
#the_reload_image = PhotoImage(file=reload_image)

#Search panel entry for text
searchlabel = Label(root,text='Search')
searchlabel.grid(row=6,sticky=W,pady=(10,10),padx=(10,10))
global searentry
searchentry = Entry(root,width=30)
searchentry.grid(row=6,pady=(10,10),sticky=W,padx=(60,0))
#Search panel clear button
#searchbutton = Button(root,width=5,text='Reload',command=lambda:reload_list(view_entries(),searchentry,reload=1))
#searchbutton.grid(row=6,pady=(0,10),sticky=W,padx=(255,0))
#Bind search panel events key presses, Enter, Backspace
searchentry.focus()
searchentry.bind('<BackSpace>', lambda x:check_if_search_empty(searchentry))
searchentry.bind('<KeyRelease>', lambda x:reload_list(view_entries(),searchentry,reload=0))

#Side view
sidebox = Text(root,width=26,height=17,borderwidth=1,relief=GROOVE,selectborderwidth=1)
sidebox.grid(columnspan=3,rowspan=2,column=2,row=1,padx=(0,10),sticky=N+W+S+E,pady=(0,0))

#Bottom status bar
statustext = Label(root, bd=1, relief=SUNKEN,anchor=E)
statustext.grid(sticky=W+E,columnspan=6)


#Toolbar
button_image = 'key3.png'
image_for_button = PhotoImage(file=button_image)
#image_for_button = image_for_button.zoom(9)
#image_for_button = image_for_button.subsample(60)

setting_image = 'gears2.png'
image_for_button2 = PhotoImage(file=setting_image)

add_image = 'plus2.png'
image_for_button3 = PhotoImage(file=add_image)

toolbar = Frame(root)
toolbar.grid(row=0,sticky=E+W)
key_button = Button(toolbar,image=image_for_button,width=32,height=30,relief=GROOVE, command=master_key_window)
key_button.grid(sticky=W,padx=(1,0))
setting_button = Button(toolbar,image=image_for_button2,width=32,height=30,relief=GROOVE,command=lambda:settings(document_path,sqlite_file))
setting_button.grid(sticky=W,padx=(1,0),column=2,row=0)
add_button = Button(toolbar,image=image_for_button3,width=32,height=30,relief=GROOVE,command=new_account_window)
add_button.grid(sticky=W,padx=(1,0),column=1,row=0)


#Change icon
root.iconbitmap('safekey.ico')

root.grid_columnconfigure(0,weight=1)
#root.grid_columnconfigure(1,weight=1)
root.grid_columnconfigure(2,weight=1)
root.grid_columnconfigure(4,weight=1)
#root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)

#Resize event
#root.bind("<Configure>", resize)
root.protocol("WM_DELETE_WINDOW", dump_geometry)
#root.bind("<Configure>", dump_position)

#Show GUI
status_update(master_key_str,found_amount=0,search_update=0)

#Show the change encryption button1
with open(f'sfky_cnfg.pkl', 'rb') as config_file:
    config_elements = pickle.load(config_file)
    encryption = config_elements['encryption_format']
stringvar = tkinter.StringVar()
options = ['AES','BASE64']
stringvar.set(encryption)
dropdown = OptionMenu(root,stringvar,*options,command=lambda x:change_encryption(key_file_path,stringvar,key_file=0,enc_change=1))
dropdown.configure(width=6)
dropdown.grid(row=0,column=4,sticky=E,padx=(0,9))
#encryption_label = Label(file_window_root, text='Encryption Type')
#encryption_label.grid(row=3,column=0,sticky=E)

#Select first item and show its contents
#listmenu.selection_set(0,0)
#listmenu.activate(0)
view_entries()
items = [listmenu2.get_children()]
sg = ttk.Sizegrip(root)
sg.grid(row=7,column=4,sticky=E)
try:
    listmenu2.selection_set(f'{items[0][0]}')
    listmenu2.focus(f'{items[0][0]}')
    listmenu2.event_generate('<<TreeviewSelect>>')
except:
    pass




root.mainloop()
>>>>>>> 19e0d976084ad6ed9ef5ad0555928975266cba8a
