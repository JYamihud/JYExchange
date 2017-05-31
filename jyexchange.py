# -*- coding: utf-8 -*-
# J.Y. Exchange
# version 0.1
# Using pyGTK and python 2.7 not 3 lol

import gtk
import threading
import os
import socket
import random
import glib
import datetime
import pango
import zipfile

VERSION = 0.21 # A software version for the updater

def main_quit(widget):
    gtk.main_quit()

#ZIP DEFS
def zip_folder(folder_path, output_path):
    """Zip the contents of an entire folder (with that folder included
    in the archive). Empty subfolders will be included in the archive
    as well.
    """
    parent_folder = os.path.dirname(folder_path)
    # Retrieve the paths of the folder contents.
    contents = os.walk(folder_path)
    try:
        zip_file = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
        for root, folders, files in contents:
            # Include all subfolders, including empty ones.
            for folder_name in folders:
                absolute_path = os.path.join(root, folder_name)
                relative_path = absolute_path.replace(parent_folder + '/',
                                                      '')
                
                zip_file.write(absolute_path, relative_path)
            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                relative_path = absolute_path.replace(parent_folder + '/',
                                                      '')
                
                zip_file.write(absolute_path, relative_path)
        
    except IOError, message:
        print message
        sys.exit(1)
    except OSError, message:
        print message
        sys.exit(1)
    except zipfile.BadZipfile, message:
        print message
        sys.exit(1)
    finally:
        zip_file.close()


#ok let's make our window

mainwindow = gtk.Window()
mainwindow.connect("destroy", main_quit)
mainwindow.set_title("J.Y. EXCHANGE ")
mainwindow.set_default_size(500, 500)
mainwindow.set_position(gtk.WIN_POS_CENTER)
#mainwindow.maximize()

gtk.window_set_default_icon_from_file("py_data/icon.png")

box1 = gtk.VBox(False, 5)

#paaned I guess

vpaned = gtk.VPaned()
mainwindow.add(vpaned)

# "J.Y. EXCHANGE console... No input... Outpur only"
CONSOLEBOX = gtk.VBox(False)
CONSOLEBOX.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))

def treeview_changed(widget, thatsecondone):
    
    global consolescroller
    
    adj = consolescroller.get_vadjustment()
    adj.set_value( adj.upper - adj.page_size )


consolescroller = gtk.ScrolledWindow()
consolescroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
consolescroller.set_size_request(100, 100)
consolescroller.set_shadow_type(gtk.SHADOW_NONE)




CONSOLEBOX.pack_start(consolescroller, True)

vpaned.pack1(box1, True, False)
vpaned.pack2(CONSOLEBOX, True, False)

def Print(text, error=False):
    
    global console
    global consoleview
    
    text = str(text)
    
    if text.find("\n") > 0:
        text = text.replace("\n", "\n              ")
    
    
    
    end = console.get_end_iter()
    
    hour = str(datetime.datetime.now().hour)
    minute = str(datetime.datetime.now().minute)
    second = str(datetime.datetime.now().second)
    
    if len(hour) == 1:
        hour = "0"+hour
    if len(minute) == 1:
        minute = "0"+minute
    if len(second) == 1:
        second = "0"+second
    
    time = hour+":"\
          +minute+":"\
          +second
    
    tmp = "["+time+"]    "+text+"\n"
    
    global e_tag
    global m_tag
    global r_tag
    global h_tag
    
    
    
    tag = False
    tagging = False
    
    if error == True:
        tag = e_tag
        tagging = True
    elif error == "m":
        
        tag = m_tag
        tagging = True
    
    elif error == "r":
        tag = r_tag
        tagging = True
    
    elif error == "h":
        tag = h_tag
        tagging = True
    
    
    
    #COMPLICATED MARCKUPS
    
    
    
    if tmp.find("<h>") > 0:
        
        
        
        
        
        tmp = text.split("<h>",1)
        
        
        
        tmp[0] = "["+time+"]    "+tmp[0]
        
        if tagging == True:
            console.insert_with_tags(end, tmp[0], tag)
            console.insert_with_tags(end, tmp[1]+"\n", h_tag)
        else:
            console.insert(end, tmp[0])
            console.insert_with_tags(end, tmp[1]+'\n', h_tag)
        
        tagging = None
        
    if tagging == True:
        console.insert_with_tags(end, tmp, tag)
    elif tagging == None:
        pass
    else:
        console.insert(end, tmp)
    
    
    



consoleview = gtk.TextView()
consoleview.set_editable(False)



consoleview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
consoleview.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#00AA00"))
fontdesc = pango.FontDescription("Courier Bold")
consoleview.modify_font(fontdesc)

consoleview.connect("size-allocate", treeview_changed)

console = consoleview.get_buffer()
console.set_text("")

e_tag = console.create_tag("colored", foreground="#FF0000")
m_tag = console.create_tag("message", foreground="#AAAA00")
r_tag = console.create_tag("recieved", foreground="#FFFF00")
h_tag = console.create_tag("help", foreground="#2222FF")

##little console intpu thing

INPUTBOX = gtk.HBox(False)


def consoleinput(widget):
    
    hour = str(datetime.datetime.now().hour)
    minute = str(datetime.datetime.now().minute)
    second = str(datetime.datetime.now().second)
    
    if len(hour) == 1:
        hour = "0"+hour
    if len(minute) == 1:
        minute = "0"+minute
    if len(second) == 1:
        second = "0"+second
    
    time = hour+":"\
          +minute+":"\
          +second
    
    text = widget.get_text()
    
    global client
    
    # SAY: sending a message
    
    if text.startswith("SAY:"):
        
        widget.set_text("SAY: ")
        widget.set_position(-1)
        
        if not text[5:]:
        
            Print("COMMAND [SAY:] ERROR! [NO SENDING ARGUMENT]", True)
            return
        try:
            client.send(text)
            
            Print("SENT: "+text[5:], "m")
            
            
        except:
            Print("CONNECTION ERROR", True)
    
    elif text.startswith("UPDATE"):
        update()
    
    elif text.startswith("SNAKE"):
        Print("THE BITCHY PYTHON", True)
        import snake
    # CONNECT
    
    elif text.startswith("CONNECT"):
        
        global CONNECTED
        
        if CONNECTED == False:
        
            ONuprefresh(True)
        else:
            Print("ALREADY CONNECTED", True)
        
        
        widget.set_text("")
    
    elif text.startswith("HELP"):
        
        Print("HELP! \n"\
             +"SAY: argument     - sending message\n"\
             +"CONNECT           - connecting to IP, PORT specified at the top\n"\
             +"UPDATE            - update the software using github link\n"\
             +"SNAKE             - play snake (works just ones during runtime)\n"\
             +"PYTHON: argument  - executes python command and returns the value\n"\
             +"SAVE              - saving text from this console to .txt file at\n"\
             +"                    a directory specified for Dowloading.\n"\
             +"SAVE TO: argument - saving text from this conlose to custom directory", "h" )
        
        widget.set_text("")
    
    
    elif text.startswith("PYTHON:"):
        
        
        
        widget.set_text("PYTHON: ")
        widget.set_position(-1)
        
        
        for k, v in list(globals().iteritems()):
            
            if k in text:
                
                for i in ["=", "del","append"]:
                    
                    if i in text:
                        
                        Print("PYTHON: ERROR [ATTEMPT TO MODIFY PROGRAM DATA STOPPED]", True)
                        return
        
        
        if not text[8:]:
        
            Print("COMMAND [PYTHON:] ERROR! [NO ARGUMENT]", True)
            return
        
        try:
            Print( "PYTHON: "+str(eval(text[8:])), "m")
        except:
            Print("PYTHON: ERROR", True)
            raise
    
    elif text.startswith("SAVE"):
        
        
        path = dfolrerentry.get_text()
        
        if text.startswith("SAVE TO:"):
            
            if not text[9:]:
                
                Print("FORGOT TO TYPE IN A PATH", True)
                
                return
                
                
            path = text[9:]
            
            
        
        elif text == "SAVE":
        
            path = dfolrerentry.get_text()
        
        
        if not os.path.exists(path):
            
            try:
                os.makedirs(path)
            except:
                Print("ERROR! UNABLE TO MAKE DIRECTORY ["+path+"]", True)
                return
        
        filename =  "/"+str(datetime.datetime.now()).replace(" ", "_").replace(".","_")+"_CONSOLE_LOG.txt" 
        savelog = open(path+filename, "w")
        
        savelog.write("J.Y.EXCHANGE SAVED LOG ["+text+"]\n")
        savelog.write("VERSION "+str(VERSION)+"\n\n")
        savelog.write("TIME: "+str(datetime.datetime.now())+"\n\n")
        
        start = console.get_start_iter()
        end = console.get_end_iter()
        
        
        
        consoletext = str( console.get_text(start, end) )
        savelog.write(consoletext)
        
        savelog.close()
        
        Print("SAVED TO: "+path+filename)
        
        widget.set_text("")
    
    else:
        if text.find(" ") > 0:
            
            Print("ERROR! COMMAND: ["+text[:text.find(" ")]+"] IS UNKNOWN\nTRY <h>HELP", True)
        else:
            
            Print("ERROR! COMMAND: ["+text+"] IS UNKNOWN\nTRY <h>HELP", True)
        widget.set_text("")

def sayyellow(widget):
    
    text = text = widget.get_text()
    
    if text == "SAY:":
        
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AAAA00"))
    
    elif text.startswith("SAY: "):
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFF00"))
    
    elif text.startswith("CONNECT"):
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AAAA00"))
    
    elif text.startswith("HELP"):
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#2222FF"))
    
    elif text.startswith("UPDATE"):
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AAAA00"))
    elif text.startswith("SNAKE"):
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AAAA00"))
    
    elif text == "PYTHON:":
        
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AAAA00"))
    elif text.startswith("PYTHON: "):
        
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFF00"))
    
    elif text == "SAVE":
        
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AAAA00"))
    
    
    
        
        
    elif text == "SAVE TO:":
        
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AAAA00"))
        
    elif text.startswith("SAVE TO: "):
        
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFF00"))
        
        
    elif text.startswith("SAVE"):
        
        
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#555500"))
    
    else:
        widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#00AA00"))
    
    
    
    
INPUT = gtk.Entry()

INPUT.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
INPUT.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#00AA00"))
INPUT.modify_font(fontdesc)
INPUT.set_has_frame(False)

INPUT.connect("activate", consoleinput)
INPUT.connect("changed", sayyellow)


INPUTBOX.pack_end(INPUT, True)

CONSOLEBOX.pack_end(INPUTBOX, False)



consolescroller.add_with_viewport(consoleview)
Print("START UP")


### place ultra main tools here

settingsframe = gtk.Frame("Settings")
box1.pack_start(settingsframe, False)

settingsbox = gtk.HBox(False)
settingsframe.add(settingsbox)

ticks_frame = gtk.Frame("Server Tick")
settingsbox.pack_start(ticks_frame, False)

tickbox = gtk.HBox(False)
ticks_frame.add(tickbox)

tickl1 = gtk.Label("Each")
tickl2 = gtk.Label("ms")

tickbox.pack_start(tickl1, False)


TICKSPEED = 100

def onupdatetick(widget):
    
    global TICKSPEED
    
    TICKSPEED = int(widget.get_value())


tickadj = gtk.Adjustment(1.0, 1.0, 500.0, 1.0, 5.0, 0.0)
ticksbutton = gtk.SpinButton(tickadj, 0, 0)
ticksbutton.set_value(TICKSPEED)
ticksbutton.connect("value-changed", onupdatetick)
ticksbutton.set_wrap(True)
tickbox.pack_start(ticksbutton)

tickbox.pack_end(tickl2, False)

updateframe = gtk.Frame("Local Update")
settingsbox.pack_end(updateframe, False)

updatebox = gtk.HBox(False)
updateframe.add(updatebox)

updatelabel = gtk.Label("Version :"+str(VERSION)+" Avalable: Non ")
updatebox.pack_start(updatelabel, False)

update = gtk.Button()

updateicon = gtk.Image()
updateicon.set_from_file("py_data/icons/save.png")
updateblabel = gtk.Label("Localy Update")

updatebuttonbox = gtk.HBox()
updatebuttonbox.pack_start(updateicon, False)
updatebuttonbox.pack_start(updateblabel, False)

update.add(updatebuttonbox)

update.set_tooltip_text("Dowloading Avalable Version and updates to it\nRequire restart of the programm")
update.set_sensitive(False)
updatebox.pack_start(update, False)






bigbox = gtk.HPaned()
box1.pack_start(bigbox)

serverbox = gtk.VBox(False)
bigbox.pack1(serverbox, True, False)

serverframe = gtk.Frame("Upload")
serverbox.pack_start(serverframe)

upt1box = gtk.VBox(False)
serverframe.add(upt1box)

upsockettools = gtk.HBox(False)
upt1box.pack_start(upsockettools, False)

upsbox = None

#RELOAD SOCKET BUTTON

def socksetrefresh(widget):
    
    global upsbox
    global upsockettools
    
    
    upsbox.destroy()
    
    upsbox = gtk.HBox(False)
    upsockettools.pack_start(upsbox)
    
    upsocketsettings()
    
    upsbox.show_all()
    
# to make it work lol
def glibrefrservsocketthreadsshit():
    
    socksetrefresh(True)
    glib.timeout_add(TICKSPEED, glibrefrservsocketthreadsshit)
    
glib.timeout_add(1, glibrefrservsocketthreadsshit)



upsbox = gtk.HBox(False)
upsockettools.pack_start(upsbox)

upport = random.randint(1000, 10000)

curwpf = "file://"+os.getcwd()+"/"+__file__ 

upfiles = [[curwpf, str(VERSION), False ]]
uplock = False
serverdone = False


def servering():
    
    global upport
    
    
    
    
    server = socket.socket()
    while True:
        
        Print("TRYING MAKING SERVER AT PORT: "+str(upport))
        
        try:
        
        
            server.bind(("",upport))
            
            global upportentry
            
            try:
                upportentry.set_text(str(upport))
            except:
                pass
            
            global serverdone
            serverdone = True
                
            
            
            break
        except:
            
            old = upport
            upport = random.randint(1000, 10000)
            Print( "PORT "+str(old)+" FAILED: REFUSED CONNECTION! NEW PORT:"+str(upport), True )
            #raise
            
            
    if True:
        if serverdone == True:
            
            server.listen(1)
            
            import commands
            serverip = commands.getoutput("hostname -I")
            
            if serverip not in ["", " ", "\n", " \n"]:
                Print( "CONNECTION ESTABLISHED! SERVER STARTED")
            else:
                Print( "SERVER BINED BUT NO INTERNET CONNECTION. WAITING FOR CONNECTION", True)
            c, addr = server.accept()
            
            Print( "CLIENT HAS CONNECTED : [ IP: " +str(addr[0]) + "  PORT: "+str(addr[1])+ "]")
            
            
            # MAIN SERVER TALK
            
            while True:
                
                r = c.recv(1024)
                
                
                
                
                # REFRESH REQUEST
                if r == "REFRESH_REQUEST":
                
                    global upfiles
                
                    upfilessend = "FILES:\n"
                
                    for i in upfiles:
                        
                        lock = "LOCK"
                        folder = "FILE"
                        
                        if i[2] == False:
                            lock = "UNLOCK"
                        if os.path.isdir(i[0][7:].replace("%20", " ")):
                            folder = "FOLDER"
                        
                        
                        upfilessend = upfilessend+i[0]+"\n"+i[1]+"\n"+lock+"\n"+folder+"\n"
            
                    upfilessend = upfilessend+"END:\n"
                    
                    amount = str(len(upfilessend))
                    
                    c.send(amount)
                    
                elif r == "REQUEST_FILES_LIST":
                    
                    
                    
                    c.send(upfilessend)
                        
                        
                        
                # SAY:
                
                elif r.startswith("SAY: "):
                    
                    Print("MESSAGE: "+r[5:], "r")
                
                
                
                # REQUEST_DOWLOAD
                
                elif r == "REQUEST_DOWLOAD":
                    
                    c.send("URL?")
                    
                    rurl = c.recv(1024)
                    
                    Print("CLIENT REQUESRS "+rurl[7:])
                    
                    found = False
                    
                    for i in upfiles:
                        
                        if rurl in i:
                            
                            found = True
                            
                            if i[2] == False:
                                
                                if os.path.isdir(rurl[7:].replace("%20", " ")):
                                    c.send("FOLDER")
                                else:
                                    c.send("FILE")
                                
                                # REQUEST_SIZE
                                
                                
                            elif i[2] == True:
                                c.send("PASSWORD?")
                                
                                r = c.recv(1024)
                                
                                if r == uppassword.get_text():
                                    
                                    Print("CLIENT'S REQUESTED PASSWORDED FILE/FOLDER!    [GOOD]   PASSWORD RECIEVED CORRECT")
                                    
                                    if os.path.isdir(rurl[7:].replace("%20", " ")):
                                        c.send("FOLDER")
                                    else:
                                        c.send("FILE")
                                else:
                                    Print("CLIENT'S REQUESTED PASSWORDED FILE/FOLDER!    [BAD]   PASSWORD RECIEVED NOT CORRECT", True)
                                    c.send("ACCESS DENIED")
                                    break
                            
                            r = c.recv(1024)
                            
                            if r == "REQUEST_SIZE":
                                
                                filesize = os.path.getsize(rurl[7:].replace("%20", " "))
                                
                                c.send(str(filesize))
                                
                                r = c.recv(1024)
                                
                                if r == "REQUEST_BINARY":
                                    
                                    Print("TO CLIENT "+str(addr[0])+" SENDING: FILE ["+rurl+"]")
                                    
                                    sendfile = open(rurl[7:].replace("%20", " "), "r")
                                    
                                    while True:
                                        c.send(sendfile.read(524288))
                                        
                                        answer = c.recv(4)
                                        
                                        
                                        if answer == "MORE":
                                            continue
                                        else:
                                            break
                                    
                                    break
                            
                            # IF IT'S FOLDER
                            elif r == "REQUEST_ZIP":
                                
                                zip_folder(rurl[7:].replace("%20", " "), 'temp.zip')
                                
                                c.send("ZIP_DONE")
                                
                                r = c.recv(1024)
                                
                                if r == "REQUEST_ZIP_SIZE":
                                    
                                    zipsize = os.path.getsize('temp.zip')
                                    
                                    
                                    
                                    c.send(str(zipsize))
                                    
                                    r = c.recv(1024)
                                    
                                    if r == "REQUEST_ZIP_BINARY":
                                        
                                        Print("TO CLIENT "+str(addr[0])+" SENDING: ZIPPED FOLDER ["+rurl+"]")
                                        
                                        sendfile = open('temp.zip', "r")
                                        
                                        while True:
                                            c.send(sendfile.read(524288))
                                            answer = c.recv(4)
                                            
                                            
                                            if answer == "MORE":
                                                continue
                                            else:
                                                break
                                        os.remove('temp.zip')
                                        
                                        break
                            
                            
                            
                            
                            
                            
                    if found == False:
                        c.send("ACCESS DENIED")
                        Print("REQUESTED FILE IN NOT ON THE LIST! REQUEST WAS DENIED", True)
                elif r != "":
                    Print("FROM CLIENT "+str(addr[0])+" RECIEVED : REQUEST ["+r+"]")
                
                if r == "":
                    
                    Print( "CLIENT HAS DISCONNECTED : [ IP: " +str(addr[0]) + "  PORT: "+str(addr[1])+ "]", True)
                    
                    server.close()
                    
                    servering()
                
    return True

server1 = threading.Thread(target=servering, args=())
server1.daemon = True
server1.start()

upportentry = None

def upsocketsettings():
    
    global upsockettools
    global upsbox
    global upport
    global upportentry
    
    
    # SOCKET TOOL FOR UPLOAD
    
    #finsing a current IP
    
    try:
        import commands
        serverip = commands.getoutput("hostname -I")
        
        if serverip in ["", " ", "\n", " \n"]:
            serverip = "NO CONNECTION"
    except:
        serverip = "NO CONNECTION"
    
    
    
    
    iplabel = gtk.Label("IP: "+serverip)
    
    upsbox.pack_start(iplabel)
    
    
    #Port:4564564
    
    upportbox = gtk.HBox()
    upsbox.pack_end(upportbox)
    
    
    upportlabel = gtk.Label("Port: ")
    upportbox.pack_start(upportlabel, False)
    
    upportentry = gtk.Label()
    upportentry.set_text(str(upport))
    upportbox.pack_start(upportentry, False)
    
    


upsocketsettings()



#making a port accepting thingy

#little separator
lilsep = gtk.HSeparator()
upt1box.pack_start(lilsep, False)

uptools = gtk.HBox(False)
upt1box.pack_start(uptools, False)





## here put tool



# ADD FILE BUTTON


def addbuttondialogrun(widget):
    
    widget.set_sensitive(False)
    
    addbuttondialog = gtk.FileChooserDialog("Open..",
                                     None,
                                     gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    addbuttondialog.set_default_response(gtk.RESPONSE_OK)
    
    response = addbuttondialog.run()
    if response == gtk.RESPONSE_OK:
        
        global upfiles
        global uplock
        
        get = addbuttondialog.get_filename()
        
        if ["file://"+get, get[get.rfind("/")+1:]] not in upfiles:
            upfiles.append(["file://"+get, get[get.rfind("/")+1:], uplock])
            
            refrashuploads()
        
    widget.set_sensitive(True)
    addbuttondialog.destroy()

addbutton = gtk.Button()
addbuttonicon = gtk.Image()
addbuttonicon.set_from_file("py_data/icons/add.png")
addbutton.add(addbuttonicon)
addbutton.set_tooltip_text("Add files to send")
addbutton.connect("clicked", addbuttondialogrun)
uptools.pack_start(addbutton, False)




# ADD FOLDER BUTTON

def addfolderbuttondialogrun(widget):
    
    widget.set_sensitive(False)
    
    addfolderbuttondialog = gtk.FileChooserDialog("Folder..",
                                     None,
                                     gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    addfolderbuttondialog.set_default_response(gtk.RESPONSE_OK)
    
    response = addfolderbuttondialog.run()
    if response == gtk.RESPONSE_OK:
        
        global upfiles
        global uplock
        
        get = addfolderbuttondialog.get_filename()
        
        if ["file://"+get, get[get.rfind("/")+1:]] not in upfiles:
            upfiles.append(["file://"+get, get[get.rfind("/")+1:], uplock])
            
            refrashuploads()
        
    widget.set_sensitive(True)
    addfolderbuttondialog.destroy()

addfolderbutton = gtk.Button()
addfolderbuttonicon = gtk.Image()
addfolderbuttonicon.set_from_file("py_data/icons/folder.png")
addfolderbutton.add(addfolderbuttonicon)
addfolderbutton.set_tooltip_text("Add folder to send")
addfolderbutton.connect("clicked", addfolderbuttondialogrun)
uptools.pack_start(addfolderbutton, False)

sep1 = gtk.VSeparator()
uptools.pack_start(sep1, False)


# PASSWORD FIELD

uppasswordlabel = gtk.Label(" Password:")
uptools.pack_start(uppasswordlabel, False)

uppassword = gtk.Entry()
uppassword.set_tooltip_text("Set Password")
uppassword.set_visibility(False)
uptools.pack_start(uppassword, False)


def seeuppassword(widget):
    if uppassword.get_visibility() == False:
        uppassword.set_visibility(True)
    else:
        uppassword.set_visibility(False)
        
#/usr/share/icons/gnome/16x16/status/stock_lock.png
uppasswodbutton = gtk.Button()
uppasswodbuttonicon = gtk.Image()
uppasswodbuttonicon.set_from_file("py_data/icons/stock_lock.png")
uppasswodbutton.add(uppasswodbuttonicon)
uppasswodbutton.set_tooltip_text("See Password")
uppasswodbutton.connect("clicked", seeuppassword)
uptools.pack_start(uppasswodbutton, False)

sep2 = gtk.VSeparator()
uptools.pack_start(sep2, False)


#### CLEAR FILES LIST

def clearupfiles(widget):
    global upfiles
    
    
    upfiles = [[curwpf, str(VERSION), False ]]
    
    refrashuploads()

clearupbutton = gtk.Button()
clearupbuttonicon = gtk.Image()
clearupbuttonicon.set_from_file("py_data/icons/edit-delete.png")
clearupbutton.add(clearupbuttonicon)
clearupbutton.set_tooltip_text("Clear")
clearupbutton.connect("clicked", clearupfiles)
uptools.pack_end(clearupbutton, False)

##### CHECK BUTTON


def uplockcheck(widget):
    
    global uplock
    global upfiles
    
    if uplock == False:
        uplock = True
        
        
        
    else:
        uplock = False
    
    for x, i in enumerate(upfiles):
       
       if x == 0:
            continue
       
       upfiles[x][2] = uplock
    
    refrashuploads()

checkupbutton = gtk.CheckButton("Lock")
checkupbutton.set_active(uplock)
checkupbutton.set_tooltip_text("Lock/Unlcok All")
checkupbutton.connect("clicked", uplockcheck)
uptools.pack_end(checkupbutton, False)




# LIST OF FILES UPLOAD

upscroll = gtk.ScrolledWindow()
upt1box.pack_start(upscroll)



serfbox = gtk.VBox(False)
upscroll.add_with_viewport(serfbox)




def motion_cb(wid, context, x, y, time):
    
    context.drag_status(gtk.gdk.ACTION_COPY, time)
    return True
def drop_cb(wid, context, x, y, time):
    wid.drag_get_data(context, context.targets[-1], time)
    return True
def got_data_cb(wid, context, x, y, data, info, time):
    
    
    global uplock
    
    filenames = data.get_text()[data.get_text().rfind("/")+1:].replace("%20", " ").split("\n")
    urls = data.get_text().split("\n")
    
    global upfiles
    
    for x, i in enumerate(urls):
        url = urls[x]
        
        
        
        if [url, url[url.rfind("/")+1:].replace("%20", " ")] not in upfiles and i is not urls[-1]:
            upfiles.append([url, url[url.rfind("/")+1:].replace("%20", " "), uplock])
    
    #refrashing it
    refrashuploads()
    
    context.finish(True, False, time)
    
    
    
    
    
    
def refrashuploads():
    
    global serfbox
    global upfileslist
    
    upfileslist.destroy()
    
    upfileslist = gtk.VBox(False)
    serfbox.pack_start(upfileslist)
    
    drawfilelist()

serfbox.drag_dest_set(0,[],0)
serfbox.connect("drag_motion", motion_cb)
serfbox.connect("drag_drop", drop_cb)
serfbox.connect("drag_data_received", got_data_cb)


upfileslist = gtk.VBox(False)
serfbox.pack_start(upfileslist)

#draw file list
def drawfilelist():
    
    global upfiles
    global upfileslist
    
    
    tmplist = [[curwpf, str(VERSION), False ]]
    for i in upfiles:
        if i not in tmplist:
            tmplist.append(i)
    
    upfiles = tmplist
    
    for x, i in enumerate(upfiles):
        
        if x == 0:
            continue
        
        n = str(x)
        url, filename, filelock = i
        
        
        #main item box
        com = "mainupb_"+n+" = gtk.VBox(False)"
        exec(com) in globals(), locals()
        
        com = "upfileslist.pack_start(mainupb_"+n+", False)"
        exec(com) in globals(), locals()
        
        #firt raw box
        com = "upfirstraw_"+n+" = gtk.HBox(False, 5)"
        exec(com) in globals(), locals()
        
        com = "mainupb_"+n+".pack_start(upfirstraw_"+n+", False)"
        exec(com) in globals(), locals()
        
        #icon
        
        com = "upficon_"+n+" = gtk.Image()"
        exec(com) in globals(), locals()
        
        #setting the icon
        
        if filename[filename.rfind(".")+1:] in ["png", "jpg", "jiff","bmp","tiff"]:
            com = "upficon_"+n+".set_from_file('py_data/icons/image.png')"
            
        elif filename[filename.rfind(".")+1:] in ["avi", "mp4", "mpg","ogv","mod", "flv", "webm"]:
            com = "upficon_"+n+".set_from_file('py_data/icons/video.png')"
        
        elif filename[filename.rfind(".")+1:] in ["blend", "blend1", "blend2","blend3","blen_tc"]:
            com = "upficon_"+n+".set_from_file('py_data/icons/application-x-blender.png')"
        
        elif filename[filename.rfind(".")+1:] in ["hcw", "hc2"]:
            com = "upficon_"+n+".set_from_file('py_data/HCWicon.png')"
        
        
        elif filename[filename.rfind(".")+1:] in ["zip", "tz", "7z","tar","rar", "deb", "rpm"]:
            com = "upficon_"+n+".set_from_file('py_data/icons/deb.png')"
        
        elif filename[filename.rfind(".")+1:] in ["ogg", "mp3", "wav","aup","flac"]:
            com = "upficon_"+n+".set_from_file('py_data/icons/audio-x-generic.png')"
        
        elif filename[filename.rfind(".")+1:] in ["py", "exe", "c","html","jar"]:
            com = "upficon_"+n+".set_from_file('py_data/icons/binary.png')"
        
        
        #folder
        
        elif os.path.isdir(url[7:].replace("%20", " ")):
            
            com = "upficon_"+n+".set_from_file('py_data/icons/folder.png')"
        
        # ELSE
        else:
            com = "upficon_"+n+".set_from_file('py_data/icons/unknown.png')"
            
        
        
        exec(com) in globals(), locals()
        
        com = "upfrun_"+n+" = gtk.Button()"
        exec(com) in globals(), locals()
        
        com = "upfrun_"+n+".connect('clicked', lambda w: os.system(\"xdg-open "+url.replace("%20", " ")[7:]+"\"))"
        exec(com) in globals(), locals()
        
        com = "upfrun_"+n+".set_tooltip_text('Open the file')"
        exec(com) in globals(), locals()
        
        
        com = "upfirstraw_"+n+".pack_start(upfrun_"+n+", False)"
        exec(com) in globals(), locals()
        
        com = "upfrun_"+n+".add(upficon_"+n+")"
        exec(com) in globals(), locals()
        
        putname = filename
        if len(putname) > 20:
            putname = putname[:17]+"..."
        
        
        com = "upfname_"+n+" = gtk.Label(\""+putname+"\")"
        exec(com) in globals(), locals()
        
        com = "upfname_"+n+".set_selectable(True)"
        exec(com) in globals(), locals()
        
        com = "upfname_"+n+".set_tooltip_text(\""+filename+"\\n \\n"+url[7:]+"\")"
        exec(com) in globals(), locals()
        
        com = "upfirstraw_"+n+".pack_start(upfname_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        
        
        
        com = "deletebutton_"+n+" = gtk.Button()"
        exec(com) in globals(), locals()
        
        def deletebutton(widget, item):
            
            global upfiles
            
            upfiles.remove(item)
            
            refrashuploads()
        
        com = "deletebutton_"+n+".connect('clicked', deletebutton, i )"
        exec(com) in globals(), locals()
        
        com = "deletebuttonicon_"+n+" = gtk.Image()"
        exec(com) in globals(), locals()
                                    
        com = "deletebuttonicon_"+n+".set_from_file('py_data/icons/edit-delete.png')"
        exec(com) in globals(), locals()
                                    
        com = "deletebutton_"+n+".add(deletebuttonicon_"+n+")"
        exec(com) in globals(), locals()
                                    
        com = "deletebutton_"+n+".set_tooltip_text('Delete')"
        exec(com) in globals(), locals()
        
        com = "upfirstraw_"+n+".pack_end(deletebutton_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        
        def on_lockup(widget, item):
            
            global upfiles
            
            
            upfiles[item][2] = widget.get_active()
            
            
        
        
        com = "lockup_"+n+" = gtk.CheckButton('Lock')"
        exec(com) in globals(), locals()
        
        com = "lockup_"+n+".connect('clicked', on_lockup, x)"
        exec(com) in globals(), locals()
        
        com = "lockup_"+n+".set_active(filelock)"
        exec(com) in globals(), locals()
        
        com = "upfirstraw_"+n+".pack_end(lockup_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        com = "separatorup_"+n+" = gtk.HSeparator()"
        exec(com) in globals(), locals()
        com = "mainupb_"+n+".pack_start(separatorup_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        
        upfileslist.show_all()
        
drawfilelist()






clientbox = gtk.VBox(False)
bigbox.pack2(clientbox, True, False)

clientframe = gtk.Frame("Download")
clientbox.pack_start(clientframe)

cbox1 = gtk.VBox(False)
clientframe.add(cbox1)

cNET = gtk. HBox(False)
cbox1.pack_start(cNET, False)



dfiles = []



### DOWNLOAD TOOLS

#ip

dipl = gtk.Label("IP: ")
cNET.pack_start(dipl, False)

import commands
dip = commands.getoutput("hostname -I")
if dip == "":

    dip = "127.1.1.0"
dport = "6000"

def ONdipentry(widget):
    global dip
    
    
    dip = widget.get_text()
    

dipentry = gtk.Entry()
dipentry.connect("changed", ONdipentry)

dipentry.set_text(dip)
cNET.pack_start(dipentry, False)

# refresh/ connect button

client = None

def REFRESH_REQUEST():
    
    
    try:
        global client
        client.send("REFRESH_REQUEST")
        
        amount = client.recv(1024)
        
        client.send("REQUEST_FILES_LIST")
        
        cr = ""
        
        
        progress = dtoolsvbox.get_data("progress")
        progress.grab_add()
        
        
        while len(cr) <= int(amount)-1:
            cr = cr + client.recv(1024)
            
            #getting it to a progress bar
            
            frc =  float(float(len(cr))/(float(amount)-1.0))
            
            while gtk.events_pending():
                gtk.main_iteration_do(False)
            
            if frc > 1:
                frc = 1
            
            
            
            progress.set_fraction(frc)
            
            
            
            if len(cr) >= float(amount):
                
                refreshprogress.set_fraction(0)
                
                #print"CR______________________"
                #print cr
                #print"CR______________________"
                
                progress.grab_remove()
            
        
        if cr.startswith("FILES:") and len(cr) >= float(amount):
        
            
            
            global dfiles
            
            # url, name, lock, folder?, percent
            
            dfiles = []
            
            
            # parsing the recieved mess
            tmplist = cr.split("\n")
            
            tmplist.remove("FILES:")
            
            try:
                tmplist.remove("END:")
            except:
                print "No end was there"
            
            del tmplist[-1]
            
            n = 4
            
            tmplist = [tmplist[i:i+n] for i in range(0, len(tmplist), n)]
            
            
            # saving as dfiles
            
            for i in tmplist:
                
                tmp = []
                
                for b in i:
                    tmp.append(b)
                
                tmp.append(0)
                
                dfiles.append(tmp)
                
                
                
            
            if len(dfiles) == 0:
                dfiles = []
            
            
            if cr.startswith("FILES:") and len(cr) >= float(amount):
                reloaddfiles()
            Print("FROM SERVER "+str(dip)+" RECIEVED : FILES LIST ["+str(len(dfiles))+"]")
                
            global updatelabel
            global update
            
            
            updatelabel.set_text("Version :"+str(VERSION)+" Avalable: "+dfiles[0][1])
            update.set_sensitive(True)
            update.connect("clicked", lambda w: REQUEST_DOWLOAD(dfiles[0][0], True))
            
            
            
            
        else:
            try:
                Print("FROM SERVER "+str(dip)+" RECIEVED : ["+str(cr)+"]")
            except:
                pass
    except:
        Print("NO CONNECTION ESTABLISHED PLEASE CONNECT TO THE SERVER", True)
        raise
    
CONNECTED = False
def ONuprefresh(widget):
    
    
    
    def clientconnect():
        
        
        
        cNET.set_sensitive(False) # making button unclickable
        
        
        
        global client
        client = socket.socket()
        
        stop = 5
        
        while stop > 0:
            
            try:
                client.connect((dip, int(dport)))
                
                Print(  "CONNECTED TO SERVER COMPUTER" )
                
                break
            except:
                
                stop = stop - 1
        
        if stop == 0:
            client.close()
            client = None
            cNET.set_sensitive(True)
            
            
            Print("SOCKET ERROR!    PROBABLY : [WRONG IP OR PORT] CHECK TERMINAL FOR DETAILS", True)
            
            global CONNECTED
            CONNECTED == True
            
            
        else:
            
            btb.set_sensitive(True)
            
            REFRESH_REQUEST()
            
            
            
        
    client1 = threading.Thread(target=clientconnect, args=())
    client1.daemon = True
    client1.start()
    
    
dipentry.connect("activate", ONuprefresh) # FOR FUCK SAKE


uprefresh = gtk.Button()
uprefreshicon = gtk.Image()
uprefreshicon.set_from_file("py_data/icons/network.png")
uprefresh.add(uprefreshicon)

#uprefresh.set_sensitive(False) # needed to know OMG

uprefresh.set_tooltip_text("Connect")
uprefresh.connect("clicked", ONuprefresh)
cNET.pack_end(uprefresh, False)


# port

dportbox = gtk.HBox(False)
cNET.pack_end(dportbox, False)

dportlabel = gtk.Label("Port: ")
dportbox.pack_start(dportlabel, False)

def ONdportentry(widget):
    
    global dport
    
    
    dport = widget.get_text()

dportentry = gtk.Entry()
dportentry.connect("changed", ONdportentry)
dportentry.connect("activate", ONuprefresh)

#dportentry.set_property("editable", False)
#dportentry.set_has_frame(False)

dportentry.set_text(dport)
dportbox.pack_start(dportentry, False)

refreshprogress = gtk.ProgressBar()
refreshprogress.set_text("")



cbox1.pack_start(refreshprogress, False)



#### IF Connected tools

btb = gtk.HBox(False)
btb.set_sensitive(False)
cbox1.pack_start(btb, False)

REFRESHBIG = gtk.Button()

REFRESHBIGicon = gtk.Image()
REFRESHBIGicon.set_from_file("py_data/icons/reload_big.png")
REFRESHBIG.add(REFRESHBIGicon)
REFRESHBIG.connect("clicked", lambda w: REFRESH_REQUEST())
btb.pack_start(REFRESHBIG, False)





dtoolsvbox = gtk.VBox(False)



btb.pack_end(dtoolsvbox)

###little REFRESH PROGRESS BAR
dtoolsvbox.set_data("progress", refreshprogress)







dfolbox = gtk.HBox(False)
dtoolsvbox.pack_start(dfolbox, False)


dfollabel = gtk.Label("To Folder:")
dfolbox.pack_start(dfollabel, False)



def chosedownloadfolderdialog(widget):
    
    chosedfolder.set_sensitive(False)
    
    addfolderbuttondialog = gtk.FileChooserDialog("Folder..",
                                     None,
                                     gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    addfolderbuttondialog.set_default_response(gtk.RESPONSE_OK)
    
    response = addfolderbuttondialog.run()
    if response == gtk.RESPONSE_OK:
        
        global upfiles
        global uplock
        
        get = addfolderbuttondialog.get_filename()
        
        dfolrerentry.set_text(get)
        
    
    chosedfolder.set_sensitive(True)
    addfolderbuttondialog.destroy()



chosedfolder = gtk.Button()
chosedfoldericon = gtk.Image()
chosedfoldericon.set_from_file("py_data/icons/folder.png")
chosedfolder.add(chosedfoldericon)
chosedfolder.set_tooltip_text("Choose Download Folder")
chosedfolder.connect("clicked", chosedownloadfolderdialog)
dfolbox.pack_start(chosedfolder, False)

dfolrerentry = gtk.Entry()
dfolrerentry.set_editable(False)
dfolrerentry.set_text(os.getenv("HOME")+"/Downloads")
dfolbox.pack_end(dfolrerentry)


dpassbox = gtk.HBox()
dtoolsvbox.pack_end(dpassbox, False)

# PASSWORD FIELD

dpasswordlabel = gtk.Label(" Password:")
dpassbox.pack_start(dpasswordlabel, False)

dpassword = gtk.Entry()
dpassword.set_tooltip_text("Download Password")
dpassword.set_visibility(False)
dpassbox.pack_start(dpassword, False)


def seedpassword(widget):
    if dpassword.get_visibility() == False:
        dpassword.set_visibility(True)
    else:
        dpassword.set_visibility(False)

#/usr/share/icons/gnome/16x16/status/stock_lock.png
dpasswodbutton = gtk.Button()
dpasswodbuttonicon = gtk.Image()
dpasswodbuttonicon.set_from_file("py_data/icons/stock_lock.png")
dpasswodbutton.add(dpasswodbuttonicon)
dpasswodbutton.set_tooltip_text("See Password")
dpasswodbutton.connect("clicked", seedpassword)
dpassbox.pack_start(dpasswodbutton, False)


dscroller = gtk.ScrolledWindow()
cbox1.pack_start(dscroller)



# DOWNLOAD FUCKTION




    
def Drec_thread(url, updating=False):
    
    Print("REQUEST_DOWLOAD")
    
    
    
    try:
        global client
        
        
        
        
        # requesting the start download operation at server
        client.send("REQUEST_DOWLOAD")
        
        #if is works then the TRY will continue so to suspend
        #all buttons         In Other words
        
        
        #           SUSPENSION              #
        
        def buttonlock(true):
        
        
            global REFRESHBIG
            REFRESHBIG.set_sensitive(true)
        
            global dfolbox
            dfolbox.set_sensitive(true)
        
            global dpassbox
            dpassbox.set_sensitive(true)
            
            global dfilesbox
            dfilesbox.set_sensitive(true)
            
            #for x in range(1024):
            #    
            #    n = str(x)
            #    
            #    com = "dowload_"+n+".set_sensitive(true)"
            #    exec(com) in globals(), locals()
        
        buttonlock(False)
        
        ###### continuing the dowload task #####
        
        
        r = client.recv(1024)
        
        if r == "URL?":
            
            Print("TO SERVER : SENDING FILE URL")
            
            client.send(url)
            
            r = client.recv(1024)
            
            if r == "PASSWORD?":
                
                if dpassword.get_text() != "":
                    client.send(dpassword.get_text())
                else:
                    client.send(":(")
                
                r = client.recv(1024)
                
            if r == "FILE":
                
                client.send("REQUEST_SIZE")
                
                SIZE = client.recv(1024)
                
                Print("RECIEVED FILE SIZE : "+SIZE)
                print "RECIEVED FILE SIZE : "+SIZE
                
                if updating == False:
                
                    saveurl = dfolrerentry.get_text()+url[7:].replace("%20", " ")[url[7:].replace("%20", " ").rfind("/"):]
                else:
                    
                    if url == curwpf:
                        
                        Print("ERROR TRYING TO REWRITE THE SOURCE FILE", True)
                        
                        client.send("CANCEL")
                        
                        buttonlock(True)
                        
                        return
                    else:
                        saveurl = os.getcwd()+"/"+__file__
                
                
                
                client.send("REQUEST_BINARY")
                
                
                #### SAVING ####
                
                
                # url[7:].replace("%20", " ")
                
                
                Print("DOWLOADING AT:"+saveurl)
                
                
                savefile = open(saveurl, "w")
                savefile.close()
                
                
                
                RA = 0
                
                #progress bar stuff
                
                progress = dtoolsvbox.get_data("progress")
                progress.grab_add()
                
                
                while True:
                    
                    savefile = open(saveurl, "ab")
                    savefile.write(client.recv(524288))
                    savefile.close()
                    
                    
                    #RA = RA + 1024
                    
                    progress.set_fraction(float(os.path.getsize(saveurl))/float(SIZE))
                    #progress.set_text("Dowloaded "+str(int(os.path.getsize(saveurl)/524288/2))+" From "+str(int(int(SIZE)/524288/2))+ " MB ")
                    
                    while gtk.events_pending():
                        gtk.main_iteration_do(False)
                    
                    if os.path.getsize(saveurl) >= int(SIZE):
                        client.send("STOP")
                        break
                    else:
                        client.send("MORE")
                   
                    
                
                progress.set_fraction(0)
                progress.set_text("")
                progress.grab_remove()
                
                Print("FILE IS FINISHED DOWNLOADING")
                savefile.close()
                
            
            elif r == "FOLDER":
                
                client.send("REQUEST_ZIP")
                
                r = client.recv(1024)
                
                Print("WAITING TO REQUESTED FOLDER'S ZIP")
                
                if r == "ZIP_DONE":
                    
                    client.send("REQUEST_ZIP_SIZE")
                    
                    
                    SIZE = client.recv(1024)
                
                    Print("RECIEVED ZIP SIZE : "+SIZE)
                    print "RECIEVED ZIP SIZE : "+SIZE
                    
                    if updating == False:
                    
                        saveurl = dfolrerentry.get_text()+url[7:].replace("%20", " ")[url[7:].replace("%20", " ").rfind("/"):]
                    else:
                        
                        if url == curwpf:
                            
                            Print("ERROR TRYING TO REWRITE THE SOURCE FILE", True)
                            
                            client.send("CANCEL")
                            
                            buttonlock(True)
                            
                            return
                        else:
                            saveurl = os.getcwd()
                    
                    
                    
                    client.send("REQUEST_ZIP_BINARY")
                    
                    
                    #### SAVING ####
                    
                    
                    # url[7:].replace("%20", " ")
                    
                    
                    Print("DOWLOADING ZIPPED FOLDER AT:"+saveurl)
                    
                    
                    savefile = open('temp_recv.zip', "w")
                    savefile.close()
                    
                    
                    
                    RA = 0
                    
                    #progress bar stuff
                    
                    progress = dtoolsvbox.get_data("progress")
                    progress.grab_add()
                    
                    
                    while True:
                        
                        
                        
                        savefile = open('temp_recv.zip', "ab")
                        savefile.write(client.recv(524288))
                        
                        savefile.close()
                        
                        
                        #RA = RA + 1024
                        
                        progress.set_fraction(float(os.path.getsize(os.getcwd()+'/temp_recv.zip'))/float(SIZE))
                        progress.set_text("Dowloaded "+str(int(os.path.getsize(os.getcwd()+'/temp_recv.zip')/524288))+" From "+str(int(int(SIZE)/1024))+ " KB ")
                        
                        while gtk.events_pending():
                            gtk.main_iteration_do(False)
                        
                        if os.path.getsize(os.getcwd()+'/temp_recv.zip') >= int(SIZE):
                            
                            saveurl = saveurl[:saveurl.rfind("/")+1]
                            
                            zipfile.ZipFile('temp_recv.zip').extractall(saveurl)
                            
                            os.remove('temp_recv.zip')
                            client.send("STOP")
                            break
                        else:
                            client.send("MORE")
                    
                    progress.set_fraction(0)
                    progress.set_text("")
                    progress.grab_remove()
                    
                    Print("FILE IS FINISHED DOWNLOADING")
                    savefile.close()
                    
                
            elif r == "ACCESS DENIED":
                
                Print("ACCES TO THE FILE/FOLDER IS DENIED", True)
                
                #           SUSPENSION BACK             #
                
                
                buttonlock(True)
                
                return True
        
        
        #           SUSPENSION BACK             #
        
        
        buttonlock(True)
        
        
    
    except:
        raise

def REQUEST_DOWLOAD(url, updating=False):
    
    
    
    client2 = threading.Thread(target=Drec_thread, args=[url, updating])
    client2.daemon = True
    client2.start()

def dowload_forbuttons(widget, url):
    REQUEST_DOWLOAD(url)


# dowload as fucktion (later)





#### SHOWING THE FILES

dfilesbox = None

def reloaddfiles():
    
    
    
    global dscroller
    global dfilesbox
    
    dfilesbox.destroy()
    
    showdfiles()
    
    dfilesbox.show_all()
    



def showdfiles():
    
    global dscroller
    
    global dfilesbox
    
    
    dfilesbox = gtk.VBox()
    dscroller.add_with_viewport(dfilesbox)
    
    # url, name, lock, folder?, percent
    
    progress = dtoolsvbox.get_data("progress")
    progress.grab_add()
    
    for x, i in enumerate(dfiles):
        
        
        if x == 0:
            continue
        
        n = str(x)
        
        
        
        url, name, lock, folder, percent = i
        
        
        #box
        
        com = "filebox_"+n+" = gtk.HBox(False)"
        exec(com) in globals(), locals()
        
        com = "dfilesbox.pack_start(filebox_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        # START
        
        #icon
        
        com = "dficon_"+n+" = gtk.Image()"
        exec(com) in globals(), locals()
        
        
        if folder == "FOLDER":
            com = "dficon_"+n+".set_from_file('py_data/icons/folder.png')"
        else:
            com = "dficon_"+n+".set_from_file('py_data/icons/unknown.png')"
        
        
        
        
        
            if name[name.rfind(".")+1:] in ["png", "jpg", "jiff","bmp","tiff"]:
                com = "dficon_"+n+".set_from_file('py_data/icons/image.png')"
            
            elif name[name.rfind(".")+1:] in ["avi", "mp4", "mpg","ogv","mod", "flv", "webm"]:
                com = "dficon_"+n+".set_from_file('py_data/icons/video.png')"
        
            elif name[name.rfind(".")+1:] in ["blend", "blend1", "blend2","blend3","blen_tc"]:
                com = "dficon_"+n+".set_from_file('py_data/icons/application-x-blender.png')"
        
            elif name[name.rfind(".")+1:] in ["hcw", "hc2"]:
                com = "dficon_"+n+".set_from_file('py_data/HCWicon.png')"
        
        
            elif name[name.rfind(".")+1:] in ["zip", "tz", "7z","tar","rar", "deb", "rpm"]:
                com = "dficon_"+n+".set_from_file('py_data/icons/deb.png')"
        
            elif name[name.rfind(".")+1:] in ["ogg", "mp3", "wav","aup","flac"]:
                com = "dficon_"+n+".set_from_file('py_data/icons/audio-x-generic.png')"
        
            elif name[name.rfind(".")+1:] in ["py", "exe", "c","html","jar"]:
                com = "dficon_"+n+".set_from_file('py_data/icons/binary.png')"
        
        
        
        
        
        
        
        
        
        
        
        exec(com) in globals(), locals()
        
        com = "filebox_"+n+".pack_start(dficon_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        
        
        
        
        
        
        
        # label
        
        originalName = name
        
        if len(name) > 20:
            name = name[:17]+"..."
        
        name = " "+name
        
        com = "name_"+n+" = gtk.Label(name)"
        exec(com) in globals(), locals()
        
        com = "filebox_"+n+".pack_start(name_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        
        # END
        
        
        #download button
        
        com = "dowload_"+n+" = gtk.Button()"
        exec(com) in globals(), locals()
        
        com = "dowload_"+n+".connect('clicked', dowload_forbuttons, url)"
        exec(com) in globals(), locals()
        
        com = "dowloadicon_"+n+" = gtk.Image()"
        exec(com) in globals(), locals()
        
        com = "dowloadicon_"+n+".set_from_file('py_data/icons/save.png')"
        exec(com) in globals(), locals()
        
        com = "dowload_"+n+".add(dowloadicon_"+n+")"
        exec(com) in globals(), locals()
        
        com = "filebox_"+n+".pack_end(dowload_"+n+", False)"
        exec(com) in globals(), locals()
        
        
        
        
        
        
        #download as button
        
        com = "dowloadas_"+n+" = gtk.Button()"
        exec(com) in globals(), locals()
        
        com = "dowloadas_"+n+".set_sensitive(False)"
        exec(com) in globals(), locals()
        
        
        com = "dowloadasicon_"+n+" = gtk.Image()"
        exec(com) in globals(), locals()
        
        com = "dowloadasicon_"+n+".set_from_file('py_data/icons/save_as.png')"
        exec(com) in globals(), locals()
        
        com = "dowloadas_"+n+".add(dowloadasicon_"+n+")"
        exec(com) in globals(), locals()
        
        com = "filebox_"+n+".pack_end(dowloadas_"+n+", False)"
        exec(com) in globals(), locals()
        
        #icon of locked
        
        print lock
        
        if lock.startswith("LOCK"):
            
            com = "lockicon_"+n+" = gtk.Image()"
            exec(com) in globals(), locals()
            
            com = "lockicon_"+n+".set_from_file('py_data/icons/stock_lock.png')"
            exec(com) in globals(), locals()
            
            com = "filebox_"+n+".pack_end(lockicon_"+n+", False)"
            exec(com) in globals(), locals()
        
        
        
        
        
        #separator
        
        com = "sepdf_"+n+" = gtk.HSeparator()"
        exec(com) in globals(), locals()
        
        com = "dfilesbox.pack_start(sepdf_"+n+", False)"
        exec(com) in globals(), locals()
        
        progress.set_fraction(float(x)/float(len(dfiles)))
        
        while gtk.events_pending():
            gtk.main_iteration_do(True)
    
    progress.set_fraction(0)
    progress.grab_remove()


showdfiles()



    
    






mainwindow.show_all()

### Updater
def update():
    
    import urllib2
    
    Print("GETTING UPDATE...")
    
    
    updatefile = urllib2.urlopen("https://github.com/JYamihud/JYExchange/archive/master.zip")
    updatefile = updatefile.read()
    
    Print("SAVING UPDATE...")
    
    tmpzip = open("../tmpzip.zip", "w")
    tmpzip.write(updatefile)
    tmpzip.close()
    
    Print("UNPACKING AND INSTALLING UPDATE...")
    
    thedir = os.getcwd()
    
    #os.system("rm -rf py_data")
    
    
    #for i in os.listdir(thedir):
        #os.remove(i)
    
    zipfile.ZipFile('../tmpzip.zip').extractall(thedir)
    
    os.system("mv "+thedir+"/JYExchange-master/* "+thedir+"/ --force")
    os.system("rm -rf JYExchange-master")
    
    
    os.system("rm -rf .git")
    
    Print("RESTART TO APPLY CHANGES!!!", True)
    


try:
    
    import urllib2

    updatefile = urllib2.urlopen("https://raw.githubusercontent.com/JYamihud/JYExchange/master/UPDATES")
    updatefile = updatefile.read() 
    
    
    if float(updatefile.split("\n")[0]) > VERSION:
        
        Print("UPDATE AVALABLE !!! [VERSION: "+str(VERSION)+" AVAILABLE: "+updatefile.split("\n")[0]+" ]")
        
        #update window
        
        updwin = gtk.Window()
        updwin.set_title("Update Available !!!")
        updwin.set_position(gtk.WIN_POS_CENTER)
        
        updbox = gtk.VBox(False)
        updwin.add(updbox)
        
        uplabel = gtk.Label(updatefile)
        uplabel.modify_font(pango.FontDescription("Monospace"))
        
        
        updbox.pack_start(uplabel, False)
        
        def on_update(widget):
            updwin.destroy()
            update()
        
        
        updateb = gtk.Button("Update")
        updateb.connect("clicked", on_update)
        updbox.pack_start(updateb)        
        
        
        
        
        updwin.show_all()
        
        
except:
    pass








gtk.main()
