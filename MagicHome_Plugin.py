import socket, json, threading, time, sys, magichue, requests, webbrowser
from tkinter import *
from magichue import discover_bulbs
from magichue import Light


'''

Touch Portal MagicHome plugin

'''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 12136))

s.sendall(b'{"type":"pair","id":"TPMagicHome"}\n')
data = s.recv(1024)
print(repr(data))
settings = (json.loads(data.decode('utf-8')))["settings"]

try:
    permIps = []
    with open("Permanent_Ips.json") as jsonFile:
        for i in json.load(jsonFile):
            permIps.append(i)
except:
    permIps = []

Running = True


def DecimalToHex(decimal):
    return '#ff%02x%02x%02x' % (decimal[0], decimal[1], decimal[2])


def WriteServerData(serverInfo):
    """
    This Function makes it easier for write a log without repeating it
    """
    if settings[4]["Enable Log"] == 'On':
        currentTime = (time.strftime('[%I:%M:%S:%p] '))
        logfile = open('log.txt', 'a')
        logfile.write(currentTime + "%s" % serverInfo)
        logfile.write('\n')
        logfile.close()
    elif settings[4]["Enable Log"] == 'Off':
        print(serverInfo)


def StartUI():
    root = Tk()
    root.title("MagicHome - Permanent Ips")
    root.geometry("250x350")
    root.iconphoto(True, PhotoImage(file="icon.png"))

    myListBox = Listbox(root, width=20)
    myListBox.config(font=("Ariel", 11), justify="center")
    myListBox.pack(pady=15, padx=15)
    global permIps
    for ip in permIps:
        myListBox.insert(0, ip)

    def delete():
        global permIps
        WriteServerData(f"Deleting {myListBox.get(ANCHOR)} From Perm Devices")
        myListBox.delete(ANCHOR)
        permIps = []
        for ip in myListBox.get(0, END):
            permIps.append(ip)
        with open("Permanent_Ips.json", "w") as jsonFile:
            json.dump(permIps, jsonFile)

    def addIp():
        global permIps
        WriteServerData(f"Adding {text.get()} To Perm Devices")
        myListBox.insert(0, text.get())
        permIps = []
        for ip in myListBox.get(0, END):
            permIps.append(ip)
        with open("Permanent_Ips.json", "w") as jsonFile:
            json.dump(permIps, jsonFile)

    def helpButton():
        webbrowser.get().open_new_tab("https://github.com/ElyOshri/Touch-Portal-MagicHome-Plugin#permanent-devices-tutorial")

    Button(root, text="Delete", command=delete).pack(pady=0)
    Button(root, text="Add New Device", command=addIp).pack(pady=5)
    Button(root, text="?", command=helpButton, bg="gray", fg="white", font=("Ariel", 10)).pack(pady=5, padx=(5, 225), side=BOTTOM)
    text = StringVar(root, value="Enter Device Ip Here")
    Entry(root, textvariable=text, justify="center").pack(pady=5)

    root.mainloop()


if settings[5]["Enable Auto Update"] == "On":
    WriteServerData(f"Checking for updates")
    try:
        CheckingUpdateFile = requests.get("https://api.github.com/repos/ElyOshri/Touch-Portal-MagicHome-Plugin/tags", {"User-Agent": "MagicHome Plugin"}).json()
        if str(CheckingUpdateFile[0]['name']) != "v1.3":  #Todo: Change to new version
            WriteServerData(f"Found a updated version: {CheckingUpdateFile[0]['name']}")
            WriteServerData("New version is available please update")
            webbrowser.get().open_new_tab(f"https://github.com/ElyOshri/Touch-Portal-MagicHome-Plugin/releases/tag/{CheckingUpdateFile[0]['name']}")
        else:
            WriteServerData(f"No new version is available")
    except:
        WriteServerData("User Passed Update Check Rate Limit")


OLD_DeviceList = []
oldStates = []

if settings[3]["Permanent Devices UI"] == "On":
    threading.Thread(target=StartUI).start()


def updateStates():
    """
    This Function for sending data to TouchPortal, Creating new var and removing
    """
    global OLD_DeviceList
    global oldStates
    timer = threading.Timer(int(settings[0]["State Update Delay"]), updateStates)
    timer.start()
    if Running:
        DeviceList = permIps
        DeviceStates = []
        try:
            for i in discover_bulbs(int(settings[1]["Discover Devices Delay"])):
                if i not in DeviceList:
                    DeviceList.append(i)
        except:
            pass
        try:
            for i in range(len(DeviceList)):
                DeviceStates.append({DeviceList[i]: {"Power": Light(DeviceList[i]).on, "RGB": Light(DeviceList[i]).rgb, "Brightness": Light(DeviceList[i]).brightness, "Mode": Light(DeviceList[i]).mode, "Is_White": Light(DeviceList[i]).is_white}})

        except:
            pass
        for x in DeviceList:
            if x not in OLD_DeviceList:
                WriteServerData(f'Found New Device {x} creating a variable for it')
                s.sendall(('{"type":"createState", "id":"%s", "desc":"MagicHome %s ON or OFF", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "power", x)).encode())
                s.sendall(('{"type":"createState", "id":"%s", "desc":"MagicHome %s Brightness", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "brightness", x)).encode())
                s.sendall(('{"type":"createState", "id":"%s", "desc":"MagicHome %s RGB", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "rgb", x)).encode())
                s.sendall(('{"type":"createState", "id":"%s", "desc":"MagicHome %s Mode", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "mode", x)).encode())
                s.sendall(('{"type":"createState", "id":"%s", "desc":"MagicHome %s White", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "white", x)).encode())

                if x not in OLD_DeviceList:
                    OLD_DeviceList.append(x)

                s.sendall(('{"type":"choiceUpdate", "id":"TPPlugin.MagicHome.Actions.OnOFFTigger.Data.DeviceList", "value":%s}\n' % DeviceList).encode())
            if settings[2]["Enable Disconnected Devices"] == "Off":
                for j in OLD_DeviceList:
                    if j not in DeviceList:
                        WriteServerData(f'Removing {j} from the update states')
                        s.sendall(('{"type":"removeState", "id":"%s", "desc":"MagicHome %s ON or OFF", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "power", x)).encode())
                        s.sendall(('{"type":"removeState", "id":"%s", "desc":"MagicHome %s Brightness", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "brightness", x)).encode())
                        s.sendall(('{"type":"removeState", "id":"%s", "desc":"MagicHome %s RGB", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "rgb", x)).encode())
                        s.sendall(('{"type":"removeState", "id":"%s", "desc":"MagicHome %s Mode", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "mode", x)).encode())
                        s.sendall(('{"type":"removeState", "id":"%s", "desc":"MagicHome %s White", "defaultValue":"0"}\n' % ("TPPlugin.MagicHome.device." + x + "white", x)).encode())
        try:
            if oldStates != DeviceStates and DeviceStates != []:
                for i in DeviceStates:
                    if i not in oldStates:
                        Power = i[list(i)[0]]["Power"]
                        if Power:
                            Power = "On"
                        elif not Power:
                            Power = "Off"
                        s.sendall(('{"type":"stateUpdate", "id":"%s", "value":"%s"}\n' % ("TPPlugin.MagicHome.device." + list(i)[0] + "power", Power)).encode())
                        s.sendall(('{"type":"stateUpdate", "id":"%s", "value":"%s"}\n' % ("TPPlugin.MagicHome.device." + list(i)[0] + "rgb", DecimalToHex(i[list(i)[0]]["RGB"]))).encode())
                        s.sendall(('{"type":"stateUpdate", "id":"%s", "value":"%s"}\n' % ("TPPlugin.MagicHome.device." + list(i)[0] + "brightness", int((i[list(i)[0]]["Brightness"])/2.54))).encode())
                        ModeString = str(i[list(i)[0]]["Mode"])
                        ModeString = ModeString[7:-1]
                        s.sendall(('{"type":"stateUpdate", "id":"%s", "value":"%s"}\n' % ("TPPlugin.MagicHome.device." + list(i)[0] + "mode", ModeString)).encode())
                        WhitePower = i[list(i)[0]]["Is_White"]
                        if WhitePower:
                            WhitePower = "On"
                        elif not WhitePower:
                            WhitePower = "Off"
                        s.sendall(('{"type":"stateUpdate", "id":"%s", "value":"%s"}\n' % ("TPPlugin.MagicHome.device." + list(i)[0] + "white", WhitePower)).encode())
                oldStates = DeviceStates
        except:
            sys.exit()
    else:
        timer.cancel()


updateStates()

while Running:
    '''
    This Keeps this running and wait until it receive a data
    '''
    try:
        buffer = bytearray()
        while True:
            data = s.recv(1)
            if data != b'\n':
                buffer.extend(data)
            else:
                break
    except ConnectionResetError:
        WriteServerData(f"Shutdown TPYeeLightPlugin...")
        Running = False
        sys.exit()

    firstLine = buffer[:buffer.find(b'\n')]
    print(firstLine)
    WriteServerData(f"Received: {firstLine}")
    d = firstLine
    d = json.loads(d)
    if d['type'] == "closePlugin":
        WriteServerData(f"Shutdown TPMagicHomePlugin...")
        Running = False
        sys.exit()
    if d['type'] == 'settings':
        settings[0]['State Update Delay'] = d['values'][0]['State Update Delay']
        settings[1]["Discover Devices Delay"] = d['values'][1]['Discover Devices Delay']
        settings[2]["Enable Disconnected Devices"] = d['values'][2]['Enable Disconnected Devices']
        if settings[3]["Permanent Devices UI"] != d['values'][3]["Permanent Devices UI"] and d['values'][3]["Permanent Devices UI"] == "On":
            threading.Thread(target=StartUI).start()
        settings[3]["Permanent Devices UI"] = d['values'][3]["Permanent Devices UI"]
        settings[4]["Enable Log"] = d['values'][4]['Enable Log']
        settings[5]["Enable Auto Update"] = d['values'][5]['Enable Auto Update']

    if d['type'] != 'closePlugin' and Running and d['type'] != 'listChange' and d['type'] != "settings" and d['type'] != "broadcast":
        try:
            if d['data'][0]['value'] != "" and d['data'][1]['value'] != "":
                try:
                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.OnOFFTigger' and d['data'][0]['value'] == "ON":
                        WriteServerData(f"Running Action Turn On {d['data'][0]['value']} Light")
                        Light(d['data'][1]['value']).on = True
                    elif d['actionId'] == 'TPPlugin.MagicHome.Actions.OnOFFTigger' and d['data'][0]['value'] == "OFF":
                        WriteServerData(f"Running Action Turn Off {d['data'][0]['value']} Light")
                        Light(d['data'][1]['value']).on = False

                    if d['actionId'] == "TPPlugin.MagicHome.Actions.Bright" and d['data'][1]['id'] == "TPPlugin.MagicHome.Actions.DataBright":
                        WriteServerData(f"Running Action Bright Level {d['data'][0]['value']} On {d['data'][1]['value']}")
                        Light(d['data'][0]['value']).brightness = int((int(d['data'][1]['value']))*2.55001)

                    if d['actionId'] == "TPPlugin.MagicHome.Actions.RGB" and d['type'] == "action":
                        test = d['data'][1]['value'].lstrip('#')
                        RGB = list(int(test[i:i + 2], 16) for i in (0, 2, 4))
                        WriteServerData(f"Running Converting Hex: {d['data'][1]['value']} to RGB:{RGB}")
                        print(f"RGB = {RGB}")
                        Light(d['data'][0]['value']).rgb = (RGB[0], RGB[1], RGB[2])

                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.Toggle' and d['data'][1]['id'] == 'TPPlugin.MagicHome.Actions.UnusedData':
                        WriteServerData(f"Running Action Toggle {d['data'][0]['value']} Light")
                        power = Light(d['data'][0]['value']).on
                        if power:
                            Light(d['data'][0]['value']).on = False
                        elif not power:
                            Light(d['data'][0]['value']).on = True

                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.Brightness_Down' and d['data'][1]['id'] == "TPPlugin.MagicHome.Actions.DataBrightDown":
                        WriteServerData(f"Running Action Brightness Down {d['data'][0]['value']} Light")
                        BrightDown = int(Light(d['data'][0]['value']).brightness / 2.54)
                        if BrightDown - int(d['data'][1]['value']) <= 1:
                            BrightDown = 2
                            BrightDown += int(d['data'][1]['value'])
                        Light(d['data'][0]['value']).brightness = int((int(BrightDown)-int(d['data'][1]['value']))*2.55001)

                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.Brightness_Up' and d['data'][1]['id'] == "TPPlugin.MagicHome.Actions.DataBrightUp":
                        WriteServerData(f"Running Action Brightness Up {d['data'][0]['value']} Light")
                        BrightUp = Light(d['data'][0]['value']).brightness / 2.54
                        if BrightUp + int(d['data'][1]['value']) >= 100:
                            BrightUp = 100
                            BrightUp -= int(d['data'][1]['value'])
                        Light(d['data'][0]['value']).brightness = int((int(BrightUp) + int(d['data'][1]['value'])) * 2.55001)

                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.WhiteColdOrWarm' and d['data'][1]['id'] == "TPPlugin.MagicHome.Actions.DataWhiteWarm":
                        WriteServerData(f"Running Action White Change {d['data'][0]['value']} Light")
                        Light(d['data'][0]['value']).w = int(d['data'][1]['value'])
                        Light(d['data'][0]['value']).cw = int(d['data'][2]['value'])

                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.WhiteOnOffTigger' and d['data'][0]['value'] == "ON":
                        WriteServerData(f"Running Action White Turn On {d['data'][1]['value']} Light")
                        Light(d['data'][1]['value']).is_white = True
                    elif d['actionId'] == 'TPPlugin.MagicHome.Actions.WhiteOnOffTigger' and d['data'][0]['value'] == "OFF":
                        WriteServerData(f"Running Action White Turn Off {d['data'][1]['value']} Light")
                        Light(d['data'][1]['value']).is_white = False

                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.WhiteToggle' and d['data'][1]['id'] == 'TPPlugin.MagicHome.Actions.WhiteUnusedData':
                        WriteServerData(f"Running Action White Toggle {d['data'][0]['value']} Light")
                        White = Light(d['data'][0]['value']).is_white
                        if White:
                            Light(d['data'][0]['value']).is_white = False
                        elif not White:
                            Light(d['data'][0]['value']).is_white = True

                    if d['actionId'] == 'TPPlugin.MagicHome.Actions.Mode' and d['data'][1]['id'] == "TPPlugin.MagicHome.Actions.DataMode":
                        WriteServerData(f"Running Action Changing Mode {d['data'][0]['value']} Light")
                        if d['data'][1]['value'] == "RAINBOW_CROSSFADE":
                            Light(d['data'][0]['value']).mode = magichue.RAINBOW_CROSSFADE
                        elif d['data'][1]['value'] == "RED_GRADUALLY":
                            Light(d['data'][0]['value']).mode = magichue.RED_GRADUALLY
                        elif d['data'][1]['value'] == "GREEN_GRADUALLY":
                            Light(d['data'][0]['value']).mode = magichue.GREEN_GRADUALLY
                        elif d['data'][1]['value'] == "BLUE_GRADUALLY":
                            Light(d['data'][0]['value']).mode = magichue.BLUE_GRADUALLY
                        elif d['data'][1]['value'] == "YELLOW_GRADUALLY":
                            Light(d['data'][0]['value']).mode = magichue.YELLOW_GRADUALLY
                        elif d['data'][1]['value'] == "BLUE_GREEN_GRADUALLY":
                            Light(d['data'][0]['value']).mode = magichue.BLUE_GREEN_GRADUALLY
                        elif d['data'][1]['value'] == "PURPLE_GRADUALLY":
                            Light(d['data'][0]['value']).mode = magichue.PURPLE_GRADUALLY
                        elif d['data'][1]['value'] == "WHITE_GRADUALLY":
                            Light(d['data'][0]['value']).mode = magichue.WHITE_GRADUALLY
                        elif d['data'][1]['value'] == "RED_GREEN_CROSSFADE":
                            Light(d['data'][0]['value']).mode = magichue.RED_GREEN_CROSSFADE
                        elif d['data'][1]['value'] == "RED_BLUE_CROSSFADE":
                            Light(d['data'][0]['value']).mode = magichue.RED_BLUE_CROSSFADE
                        elif d['data'][1]['value'] == "GREEN_BLUE_CROSSFADE":
                            Light(d['data'][0]['value']).mode = magichue.GREEN_BLUE_CROSSFADE
                        elif d['data'][1]['value'] == "RAINBOW_STROBE":
                            Light(d['data'][0]['value']).mode = magichue.RAINBOW_STROBE
                        elif d['data'][1]['value'] == "GREEN_STROBE":
                            Light(d['data'][0]['value']).mode = magichue.GREEN_STROBE
                        elif d['data'][1]['value'] == "BLUE_STROBE":
                            Light(d['data'][0]['value']).mode = magichue.BLUE_STROBE
                        elif d['data'][1]['value'] == "YELLOW_STROBE":
                            Light(d['data'][0]['value']).mode = magichue.YELLOW_STROBE
                        elif d['data'][1]['value'] == "BLUE_GREEN_STROBE":
                            Light(d['data'][0]['value']).mode = magichue.BLUE_GREEN_STROBE
                        elif d['data'][1]['value'] == "PURPLE_STROBE":
                            Light(d['data'][0]['value']).mode = magichue.PURPLE_STROBE
                        elif d['data'][1]['value'] == "WHITE_STROBE":
                            Light(d['data'][0]['value']).mode = magichue.WHITE_STROBE
                        elif d['data'][1]['value'] == "RAINBOW_FLASH":
                            Light(d['data'][0]['value']).mode = magichue.RAINBOW_FLASH
                        elif d['data'][1]['value'] == "NORMAL":
                            Light(d['data'][0]['value']).mode = magichue.NORMAL
                except:
                    WriteServerData("User Passed Connection Rate Limit")
        except KeyError:
            WriteServerData('User did not input values')
