from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import platform
import os
import subprocess
import pyautogui
import time
import json
import xml.etree.ElementTree as ET

hostName = "0.0.0.0"
serverPort = 8080

other_pc = []
display_switch_path = "C:/Users/thoma/Documents/Real Documents/Useful programs/DisplaySwitch.exe"
monitor_info_path = "C:/Users/thoma/Documents/Real Documents/Useful programs/MonitorInfoView.exe"

def hardware_screen_config():
    return get_hardware_config()

class WebServer(BaseHTTPRequestHandler):

    def constructAndSendResponse(self, outJson):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(str(json.dumps(outJson)), "utf-8"))

    def do_GET(self):
        current_screen_config = hardware_screen_config()
        
        done = False
        oldC = current_screen_config
        newC = current_screen_config
        outdict = {}
        print(self.path)

        if self.path == "/set-ex" or self.path == "/set-ex/":
            print("\tFunction not permitted")
            #current_screen_config = "extended"
            #print(f"Set config to '{current_screen_config}'")

        elif self.path == "/set-solo" or self.path == "/set-solo/":
            print("\tFunction not permitted")
            #current_screen_config = "solo"
            #print(f"Set config to '{current_screen_config}'")

        elif self.path == "/get-config" or self.path == "/get-config/":
            outdict = {
                "config": current_screen_config
            }
            done = True

        elif self.path == "/get-sync" or self.path == "/get-sync/":
            pass
        elif self.path == "/do-sync" or self.path == "/do-sync/":
            pass

        elif self.path[0:15] == "/switch-screen-":
            if self.path == "/switch-screen-slave" or self.path == "/switch-screen-slave/":
                print("Switch screen called")

                if current_screen_config == "extended":
                    print("\textended -> solo")
                    newC = "solo"
                    switch_to_solo()
                    done = True
                elif current_screen_config == "solo":
                    print("\tsolo -> extended")
                    newC = "extended"
                    switch_to_extended()
                    done = True

            elif self.path == "/switch-screen-host" or self.path == "/switch-screen-host/":
                print("Switch screen called")
                global other_pc
                res = query_other_pc(other_pc, "switch-screen-slave")


                if res["done"] == True:
                    if current_screen_config == "extended":
                        print("\textended -> solo")
                        newC = "solo"

                        switch_to_solo()
                        done = True
                    elif current_screen_config == "solo":
                        print("\tsolo -> extended")
                        newC = "extended"
                        switch_to_extended()
                        done = True

            outdict = outdict | {
                "done": done,
                "oldConfig": oldC,
                "newConfig": newC,
            }
        if done:
            self.constructAndSendResponse(outdict)
        else:
            self.constructAndSendResponse({"done":False})
        

def get_monitor_count():
    final_path = os.path.expanduser("~/AUTOGENMONITORINFO.xml")
    subprocess.call(['powershell', '-Command', f'{monitor_info_path} /sxml "{final_path}"'])
    tree = ET.parse(final_path)
    os.remove(final_path)
    root = tree.getroot()
    mon_count = len(root.findall("item"))
    print(f"MonCount: {mon_count}")
    return mon_count


def getConfig() -> str:
    #Replace with windows display manager logic

    #accessing the key to open the registry directories under
    
    return current_screen_config()

def switch_display_input():
    pyautogui.hotkey('ctrl','shift','f12')

def switch_to_extended():
    print(platform.system())
    if platform.system() == "Windows":
        subprocess.Popen(['powershell', '-Command', f'{display_switch_path} /extend'])
        
    elif platform.system() == "Linux":
        print("Linux - NOT SUPPORTED")
        #subprocess.call(['sh', './linux-2-monitor.sh'])  


def switch_to_solo():
    print(platform.system())
    if platform.system() == "Windows":
        #time.sleep(1)
        switch_display_input()
        
        time.sleep(8)
        
        subprocess.Popen(['powershell', '-Command', f'{display_switch_path} /external'])
        

def switch_to_solo_old():
    print(platform.system())
    if platform.system() == "Windows":
        print("Windows")#
        time.sleep(1)
        switch_display_input()
        
        time.sleep(8)
        
        subprocess.Popen(['powershell', '-Command', 'displayswitch.exe /clone'])
        time.sleep(0.5)
        pyautogui.press(['tab','tab','tab', 'down', 'space', 'esc'], interval=0.1)
        
        global current_screen_config
        current_screen_config = "solo"

        
    elif platform.system() == "Linux":
        print("Linux - NOT SUPPORTED")
        #subprocess.call(['sh', './linux-1-monitor.sh']) 

def switch_to_extended_old():
    print(platform.system())
    if platform.system() == "Windows":
        subprocess.Popen(['powershell', '-Command', f'{display_switch_path} /clone'])
        time.sleep(0.5)
        pyautogui.press(['tab','tab','tab', 'up', 'space', 'esc'], interval=0.1)
        global current_screen_config
        current_screen_config = "extended"
    elif platform.system() == "Linux":
        print("\tNOT SUPPORTED")
        #subprocess.call(['sh', './linux-2-monitor.sh'])  

def get_hardware_config():
    mon_count = get_monitor_count()
    if mon_count == 1:
        return "solo"
    elif mon_count == 2:
        return "extended"

def query_other_pc(other_pc, query):
    for addr in other_pc:
        try:
            queryString = f"{addr}{query}"
            print(queryString)
            r = requests.get(queryString, timeout=2)
            resJson = json.loads(r.content)
            return resJson
        except:
            print("address failed")


if __name__ == "__main__":
    if platform.system() == "Windows":
        other_pc.append("http://192.168.0.108:8080/")
        other_pc.append("http://192.168.0.107:8080/")
        print(f"Windows: Setting other_pc as '{other_pc}'")
    elif platform.system() == "Linux":
        other_pc = "http://192.168.0.103:8080/"
        print(f"Linux: Setting other_pc as '{other_pc}'")
    

    #print(query_other_pc(other_pc, "get-config"))
    
    webServer = HTTPServer((hostName, serverPort), WebServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

