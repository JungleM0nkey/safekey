from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
import pickle
import glob
import base64
import os
import sqlite3

#
#Database variable definition
sqlite_file = 'db.sqlite'
sqlite_table_accounts = 'table_accounts'
#Columns
name_field = 'name'
id_field = 'ID'
field_type_int = 'INTEGER'
field_type_txt = 'TEXT'
#Connect to DB
connection = sqlite3.connect(sqlite_file)
c = connection.cursor()
#Check if DB file is new and if not create the tables inside
if os.stat(sqlite_file).st_size <= 0:
    c.execute(f'CREATE TABLE accounts (id INTEGER PRIMARY KEY,name TEXT,information TEXT)')
    connection.commit()
    connection.close()
#Main Window
root = Tk()
root.title('SafeKey Password Manager')
#Window size and opening location
root.resizable(width=False,height=False)
root.geometry('100x19+900+520')


#Check if config file exists
def load_settings():
    #Check if settings file exists and if not, create it. if exists proceed to look over it
    if os.path.isfile('sfky_cnfg.pkl'):
        config_file = open('sfky_cnfg.pkl', 'rb')
        config_file.close()
    else:
        config_file = open('sfky_cnfg.pkl', 'wb')
        config_elements = {'file_location':'file_path',
                           'master_key':'key_string',
                           'key_file_location':'file_path',
                           'use_key_file':'boolean',
                           'encryption_format':'name'
                           }
        pickle.dump(config_elements,config_file)
        config_file.close()
    #Check if folder location has been set
    print('\n===Settings===')
    print(f'Loading config file: sfky_cnfg.pkl')
    with open('sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
    document_path = config_elements['file_location']
    if document_path == 'file_path':
        print('File location is not set')
        document_path = ''
    else:
        print(f'File location set: {document_path}')
    #check to see wheather to use the the key from the file
    if config_elements["use_key_file"] == True and config_elements["master_key"] != 'key_string':
        master_key_str = config_elements["master_key"]
    else:
        master_key_str = ''
    print(f'Master key from file: {config_elements["master_key"]}')
    print(f'Key file location: {config_elements["key_file_location"]}')
    print(f'Use key file: {config_elements["use_key_file"]}')
    print('===Settings===')
    config_file.close()
    return document_path,master_key_str

#define global variables
global document_path
document_path = load_settings()
document_path = document_path[0]

global master_key_str
master_key_str = load_settings()
master_key_str = master_key_str[1]




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

def filter_out_entry_name(file_array):
    i = 0
    selection_array = []
    if len(file_array) > 1:
        for full_path in file_array:
            i += 1
            path_array = full_path.split("\\")
            name_show_format = path_array[-1]
            name_show_noformat = name_show_format.split(".")
            selection_array.append(name_show_noformat[0].lower())
#           item_index = selection_array.index(name_show_noformat)
#           print("\n" + f'[{item_index+1}]' + " " + name_show_noformat[0])
    else:
            print('No Files in Directory, exiting.')
            exit()
#        file = file_array[0]
#        path_array = file.split("\\")
#        name_show_format = path_array[-1]
#        name_show_noformat = name_show_format.split(".")
#        selection_array.append(name_show_noformat)
#        print("\n[1] " + name_show_noformat[0])
    return selection_array


def view_entries(document_path):
    if document_path == '':
        pass
    else:
        listmenu.delete(0, END)
        print(f'\nLooking through: {document_path}')
        file_array = glob.glob(f"{document_path}//*.txt")
        selection_array = filter_out_entry_name(file_array)
        for item in selection_array:
            listmenu.insert(END,item)
        return selection_array




def entry_select(event):
    list = listmenu.get(0)
    if list == '':
        pass
    else:
        doubleclick = event.widget
        index = int(doubleclick.curselection()[0])
        value = doubleclick.get(index)
        print (f'\nYou selected item {value}')
        entry_window(value)
        #gloval variables for the selected item and its index in the list

def entry_window(file_name):
    entry_window_root = Toplevel(root)
    entry_window_root.title(f'Entry Information: {file_name}')
    entry_window_root.resizable(width=False,height=False)
    entry_window_root.geometry('495x289+902+600')
    #Entry Field and placement
    account_field = Text(entry_window_root,width=60,height=15)
    account_field.grid(sticky=W,pady=5,padx=(5,5))
    account_field.focus()
    #button label and placement
    update_account_button = Button(entry_window_root,text='Update',width=13,command=lambda:update_entry(file_name,account_field,update_account_button))
    update_account_button.grid(sticky=S+E,padx=(5,5),pady=(2,2),column=0,row=1)
    #Fetch info from file after decoding
    print(f'Fetching {document_path}//{file_name}.txt')
    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'r')
    account_info = account_info_encrypted.read()
    #Checks for the key
    if len(master_key_str) > 0:
        account_info = decode(master_key_str,account_info)
        account_field.insert(END,account_info)
    else:
        print(account_info)
        account_field.insert(END,account_info)
        update_account_button.config(state=DISABLED)
    account_info_encrypted.close()




def update_entry(file_name,account_field,update_account_button):
    new_text = account_field.get(1.0,END)
    new_text_encrypted = encode(master_key_str, new_text)
    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'w')
    account_info_encrypted.write(new_text_encrypted)
    account_info_encrypted.close
    update_account_button.config(text='Done')
    print(f'Updating info with {new_text_encrypted}')



#Settings window start==================================================================================================

def folder_select(file_entry):
    #Ask to select folder where to look for files
    global document_path
    document_path = filedialog.askdirectory()
    file_entry.delete(0, END)
    file_entry.insert(0,document_path)
    file_entry.focus()
    #Output the folder location to a dictionary to reload on future launch
    with open(f'sfky_cnfg.pkl','rb') as config_file:
        config_elements = pickle.load(config_file)
        config_elements['file_location'] = document_path
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    config_file.close()
    reload_list(view_entries(document_path), searchentry, reload=1)
    return document_path


def settings(document_path):
    file_window_root = Toplevel(root)
    file_window_root.title('Settings')
    file_window_root.resizable(width=False,height=False)
    file_window_root.geometry('550x100+902+605')
    #Entry Field and placement
    file_entry = Entry(file_window_root,width=60)
    file_entry.focus()
    #Fill in file path with current into stored inside the sfky_cnfg.pkl file
    file_entry.insert(0, document_path)
    file_entry.grid(sticky=E,row=0,column=1,pady=(2,2),padx=(0,5))
    #Button Label and placement
    file_label = Label(file_window_root, text="Files Directory")
    file_label.grid(sticky=EW,row=0,pady=(2,2),)
    #Button and placement
    file_button = Button(file_window_root, text="Browse",width=11,command=lambda:folder_select(file_entry))
    file_button.grid(sticky=W,row=0,column=2,pady=(2,2),)
    file_window_root.focus_force()
    #use a key file
    key_location_label = Label(file_window_root, text='Key Location')
    key_location_label.grid(sticky=EW,row=1,padx=(5,10))
    key_location_entry = Entry(file_window_root,width=60)
    key_location_entry.grid(sticky=W,row=1,column=1,pady=(8,10))
    key_file_button = Button(file_window_root, text='Browse',width=11,command=lambda:key_select(key_location_entry))
    key_file_button.grid(sticky=W, row=1,column=2)
    checkbox_value = IntVar()
    checkbox = Checkbutton(file_window_root, text='Use master key file ', variable=checkbox_value,command=lambda:checkbox_action(checkbox_value))
    checkbox.grid(row=2,column=1,sticky=E)
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
    apply_button.grid(row=2,column=2)



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


def key_select(key_location_entry):
    global master_key_str
    key_path = filedialog.askopenfilename()
    key_location_entry.insert(0, key_path)
    key_location_entry.focus()
    key_file = open(f'{key_path}', 'rb')
    master_key = pickle.load(key_file)
    master_key_str = str(master_key)
    key_file.close()
    with open(f'sfky_cnfg.pkl', 'rb') as config_file:
        config_elements = pickle.load(config_file)
        config_elements['key_file_location'] = key_path
        config_elements['master_key'] = master_key_str
    with open(f'sfky_cnfg.pkl', 'wb') as config_file:
        pickle.dump(config_elements, config_file)
    config_file.close()
    print(f'\nLoading key: {master_key_str}')
    status_update(master_key_str, found_amount=0, search_update=0)
    return master_key_str


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
    submit_button = Button(key_window_root,text='Create',width=11,command=lambda:create_key_file(key_window_root,key_text_entry))
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


def create_key_file(window,key_text_entry):
    master_key_str = key_text_entry.get()
    print(f'\nCreating key file with string: {master_key_str}')
    selected_folder_path = filedialog.askdirectory()
    file = open(f'{selected_folder_path}//safekey.pkl', 'wb')
    pickle.dump(master_key_str, file)
    file.close()
    window.destroy()
    tkinter.messagebox.showinfo('SafeKey Password Manager','Master Key file created.')
    print('Master key file created.')

#Settings window end==================================================================================================

def close_window(window_root,current_selected_item,current_selected_item_index):
    reload_list(view_entries(document_path), searchentry, reload=1)
    window_root.destroy()
    #reload the current list and select the previously selected item or different item
    listmenu.selection_clear(0, END)
    listmenu.selection_set(current_selected_item_index,current_selected_item_index)
    listmenu.activate(current_selected_item_index)
    mirror_info_to_side(current_selected_item)
    listmenu.see(current_selected_item_index)


def close_window_and_input_key(key_entry,key_button,key_window_root):
    master_key(key_entry,key_button)
    close_window(key_window_root,current_selected_item,current_selected_item_index)



def master_key_window():
    key_window_root = Toplevel(root)
    key_window_root.title('Input Master Key')
    key_window_root.resizable(width=False,height=False)
    key_window_root.geometry('531x30+902+605')
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
    #Grab key from the entry field and change the button text and color
    master_key_str = key_entry.get()
    key_button.config(text="Done")
    status_update(master_key_str,found_amount=0,search_update=0)
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
    print(found_items)
    status_update(master_key_str,len(found_items),search_update)
    update_listbox(found_items)
    listmenu.selection_set(0,0)
    listmenu.activate(0)
    listmenu.event_generate('<<ListboxSelect>>')

def update_listbox(selection_array):
    listmenu.delete(0, END)
    if len(selection_array) == 0:
        listmenu.delete(0, END)
    else:
        for item in selection_array:
            listmenu.insert(END, item)

def status_update(master_key,found_amount,search_update):
    if master_key != '' and search_update == 0:
        status = 'Master Key Loaded '
        statustext.config(text=status,fg='green')
    elif master_key == '' and search_update == 0:
        status = 'No Master Key '
        statustext.config(text=status,fg='red')
    elif found_amount >= 0 and search_update == 1:
        print(f'Found {found_amount} entries')
        status = f'Found {found_amount} Entries '
        statustext.config(text=status,fg='black')


def check_if_search_empty(searchentry):
        if len(searchentry.get()) == 1:
            print('Search is empty, refreshing.')
            reload_list(view_entries(document_path), searchentry,reload=0)
        else:
            pass


#New account panel

def new_account_window():
    newpanel = Toplevel(root)
    newpanel.resizable(width=False,height=False)
    newpanel.geometry('330x158+900+569')
    namelabel = Label(newpanel,text='Service:')
    namelabel.grid(row=1,padx=(31,0))
    label2 = Label(newpanel,text='Information:')
    label2.grid(row=2,padx=(5,0),sticky=N)
    servicelabel_entry = Entry(newpanel, width=40)
    servicelabel_entry.focus()
    servicelabel_entry.grid(row=1,column=1,padx=(1,1),pady=(1,0))
    entrybox = Text(newpanel,width=30,height=6)
    entrybox.grid(column=1,row=2,pady=(1,0))
    servicebutton = Button(newpanel,text='Submit',command=lambda:create_entry(servicelabel_entry,entrybox,servicebutton,newpanel))
    servicebutton.grid(row=3,column=1,padx=(197,5),pady=(5,5))
    if len(master_key_str) == 0:
        servicebutton.config(state=DISABLED)


def create_entry(servicelabel_entry,entrybox,servicebutton,window):
    service_name = servicelabel_entry.get()
    service_information = entrybox.get('1.0', END)
    service_information_encoded = encode(master_key_str,service_information)
    new_file = open(f'{document_path}/{service_name}.txt', 'w+')
    new_file.write(service_information_encoded)
    new_file.close()
    servicebutton.config(text='Done')
    servicelabel_entry.delete(0,END)
    entrybox.delete('1.0',END)
    #Find newly added entry and select it
    reload_list(view_entries(document_path), searchentry, reload=1)
    all_entries = [ listmenu.get(0, END) ]
    all_entries = all_entries[0]
    new_file_index = all_entries.index(service_name)
    print(f'Selecting entry number {new_file_index}')
    close_window(window,current_selected_item=service_name,current_selected_item_index=new_file_index)


#Side account info panel code
def info_side_show(event):
    click = event.widget
    index = int(click.curselection()[0])
    value = click.get(index)
    print(f'\nYou selected item {value}')
    mirror_info_to_side(value)
    global current_selected_item,current_selected_item_index
    current_selected_item = value
    current_selected_item_index = index



def mirror_info_to_side(file_name):
    sidebox.delete('1.0',END)
    #Fetch info from file after decoding
    print(f'Fetching {document_path}//{file_name}.txt')
    account_info_encrypted = open(f'{document_path}//{file_name}.txt', 'r')
    account_info = account_info_encrypted.read()
    #Checks for the key, decodes if key exists
    if len(master_key_str) > 0:
        account_info = decode(master_key_str,account_info)
        sidebox.insert(END,account_info)
    else:
        print(account_info)
        sidebox.insert(END,account_info)



def rclick_menu_open(event):
        #rightclick = event.widget
        #index = int(rightclick.curselection()[0])
        info_side_show(event)
        widget = event.widget
        index = widget.nearest(event.y)
        _, yoffset, _, height = widget.bbox(index)
        if event.y > height + yoffset + 5:  # XXX 5 is a niceness factor :)
            # Outside of widget.
            return
        #value = rightclick.get(index)
        #Select item on right click
        global item
        item = widget.get(index)
        list_array = listmenu.get(0,END)
        item_index = list_array.index(item)
        listmenu.selection_clear(0,END)
        listmenu.activate(item_index)
        listmenu.selection_set(item_index,item_index)
        print (f'\nOpening right click menu for: {item}')
        #rclick_menu.tk_popup(event.x_root+48, event.y_root+15, 0)
        #rclick_menu.grab_release()
        rclick_menu.post(event.x_root, event.y_root)



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
    if os.path.isfile(f'{document_path}//{current_selected_item}.txt'):
        os.remove(f'{document_path}//{current_selected_item}.txt')
        print('Item has been removed')
    else:
        print('Error file not found')
    window.destroy()
    reload_list(view_entries(document_path), searchentry, reload=1)



##################################################################################################################
##############################START GUI CREATION##################################################################
#Top menu setup
topmenu = Menu(root)
root.config(menu=topmenu)

#Rightclick menu for every item
rclick = Menu(root)
rclick_menu = Menu(rclick, tearoff=False)
rclick_menu.add_command(label='Rename')
rclick_menu.add_command(label='Delete', command=lambda:rclick_delete_item_window(current_selected_item))


#File
submenu = Menu(topmenu,tearoff=False)
topmenu.add_cascade(label="File",menu=submenu)
submenu.add_command(label="Settings",command=lambda:settings(document_path))
submenu.add_separator()
submenu.add_command(label="Create Key File",command=create_key_file_window)
submenu.add_separator()
submenu.add_command(label="Information",command=info_popup)
submenu.add_command(label="Exit",command=exit)
#Edit
submenu2 = Menu(topmenu,tearoff=False)
topmenu.add_cascade(label='Edit',menu=submenu2)
submenu2.add_command(label='New Account',command=new_account_window)
submenu2.add_command(label="Master Key",command=master_key_window)
#View
topmenu.add_cascade(label='View')


#Main listbox on root
scrollbar = Scrollbar(root)
scrollbar.grid(column=3,sticky=N+S+W,row=1,rowspan=5)
listmenu = Listbox(root, height=19,width=100,setgrid=1,selectmode=SINGLE)
listmenu.grid(row=1,column=0,rowspan=5,sticky=W,pady=(0,10))
listmenu.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listmenu.yview)
listmenu.bind('<Double-Button-1>', entry_select)
listmenu.bind('<<ListboxSelect>>', info_side_show)
listmenu.bind('<Button-3>', rclick_menu_open)

#Menu buttons creation and placement
button1 = Button(text='View',width=15,height=1,relief=RAISED,overrelief=GROOVE,font=("TkDefaultDont", 11),command=lambda:view_entries(document_path))


#Auto generate list on start
button1.invoke()


#Search panel entry for text
searchlabel = Label(root,text='Search')
searchlabel.grid(row=6,sticky=W,pady=(0,10),padx=(10,10))
searchentry = Entry(root,width=30)
searchentry.grid(row=6,pady=(0,10),sticky=W,padx=(60,0))
#Search panel clear button
searchbutton = Button(root,text='Reload',width=5,command=lambda:reload_list(view_entries(document_path),searchentry,reload=1))
searchbutton.grid(row=6,pady=(0,10),sticky=W,padx=(255,0))
#Bind search panel events key presses, Enter, Backspace
searchentry.focus()
searchentry.bind('<BackSpace>', lambda x:check_if_search_empty(searchentry))
searchentry.bind('<KeyRelease>', lambda x:reload_list(view_entries(document_path),searchentry,reload=0))

#Side view
sidebox = Text(root,width=26,height=19)
sidebox.grid(column=4,row=1,padx=(0,10),sticky=W+E+N,pady=(0,0))

#Bottom status bar
statustext = Label(root, bd=1, relief=SUNKEN,anchor=E)
statustext.grid(sticky=W+E,columnspan=6)


#Toolbar
button_image = 'key_button.png'
image_for_button = PhotoImage(file=button_image)

setting_image = 'setting.png'
image_for_button2 = PhotoImage(file=setting_image)

toolbar = Frame(root)
toolbar.grid(row=0,sticky=E+W)
key_button = Button(toolbar,image=image_for_button,width=60,height=25,relief=GROOVE, command=master_key_window)
key_button.grid(sticky=W,padx=(1,0))
setting_button = Button(toolbar,image=image_for_button2,width=60,height=25,relief=GROOVE,command=lambda:settings(document_path))
setting_button.grid(sticky=W,padx=(1,0),column=1,row=0)




#Show GUI
status_update(master_key_str,found_amount=0,search_update=0)


#Select first item and show its contents
listmenu.selection_set(0,0)
listmenu.activate(0)
listmenu.event_generate('<<ListboxSelect>>')

root.mainloop()



