from time import sleep
from snipeit import Assets, Users
import sys
import subprocess
import os
import json
import re
import requests
import pandas as pd
import configparser
import shutil



if not os.path.exists('conf.ini'):
    shutil.copy('conf.ini.sample', 'conf.ini')



config = configparser.ConfigParser()
config.read('conf.ini')


server = config.get('DEFAULT', 'server')
token = config.get('DEFAULT', 'token')
urlsheetx = config.get('DEFAULT', 'urlsheetx')
urlsheet = urlsheetx.replace('/edit#gid=', '/export?format=csv&gid=')


A = Assets()
U = Users()


## Sheet location in google drive , share drive > all_user > alluser

def getHostname():
    #ubuntu get hostname from /etc/hostname
    with open('/etc/hostname', 'r') as file:
        hostname = file.read()
        #strip trailing whitespace, and remove trailing whitespace
        hostname = hostname.strip()

        #if hostame has <hostname>.animapoint remove .animapoint
        if '.animapoint' in hostname:
            hostname = hostname.replace('.animapoint', '')


        
        return hostname

def assetID():
    #get id of asset by hostname
    s = A.getID(server, token, getHostname())
    #convert to string
    s = str(s)
    return s



def getGpu():
    #ubuntu get gpu from lspci, #get GPU model and memory using bash, gpu=$(lspci | grep VGA | awk -F ":" '{print $3}')
    gpu = subprocess.check_output(['lspci | grep VGA | awk -F ":" \'{print $3}\''], shell=True)
    #format output gpu remove b' and ', and remove trailing whitespace
    gpu = gpu.decode('utf-8').replace('b\'', '').replace('\',', '').strip()
    #     # gpu = gpu.decode('utf-8').replace('b\'', '').replace('\'', '')

    # gpu = subprocess.check_output(['lspci', '-vnn', '-d', '10de:']).decode('utf-8')
    return gpu

    #grep only gpu name from getGpu output



def getRamType():
    ramtype = subprocess.check_output(['dmidecode | grep DDR | awk \'{print $NF}\''], shell=True)
    #format output ramtype remove b' and ', and remove trailing whitespace
    ramtype = ramtype.decode('utf-8').replace('b\'', '').replace('\',', '').strip()
    #only get first word from ramtype
    ramtype = ramtype.split()[0].strip()


    return ramtype



def getRam():
    #get ram memory total from : cat /proc/meminfo | grep MemTotal | awk '{print $2}'
    ram = subprocess.check_output(['cat /proc/meminfo | grep MemTotal | awk \'{print $2}\''], shell=True)
    #format output ram remove b' and ', and remove trailing whitespace
    ram = ram.decode('utf-8').replace('b\'', '').replace('\',', '').strip()
    #     # ram = ram.decode('utf-8').replace('b\'', '').replace('\'', '')
    #convert to gb, 2 decimal places
    ram = round(int(ram) / 1024 / 1024, 2)


    return ram



def getCpu():
    #ubuntu get cpu from lscpu, #get CPU model using bash, cpu=$(lscpu | grep "Model name" | awk -F ":" '{print $2}')
    cpu = subprocess.check_output(['lscpu | grep "Model name" | awk -F ":" \'{print $2}\''], shell=True)
    #format output cpu remove b' and ', and remove trailing whitespace, also clean any trailing whitespace in middle
    cpu = cpu.decode('utf-8').replace('b\'', '').replace('\',', '').strip()

    

    return cpu






def getMac():
    #get 1 mac address that connected 
    mac = subprocess.check_output(['ip link | grep ether | awk \'{print $2}\''], shell=True)
    #format output mac remove b' and ', and remove trailing whitespace
    mac = mac.decode('utf-8').replace('b\'', '').replace('\',', '').strip()
    #     # mac = mac.decode('utf-8').replace('b\'', '').replace('\'', '')
    return mac
    
def getLocalIp():
    #get 1 local ip address of hostname
    localip = subprocess.check_output(['hostname -I | awk \'{print $1}\''], shell=True)
    #format output localip remove b' and ', and remove trailing whitespace
    localip = localip.decode('utf-8').replace('b\'', '').replace('\',', '').strip()
    #     # localip = localip.decode('utf-8').replace('b\'', '').replace('\'', '')
    return localip

def updateIPasset():
    #update ip address of asset
    #get local ip address
    localip = getLocalIp()
    #convert localip to string
    localip = str(localip)
    # print(localip)
    payloadip = '{"_snipeit_ip_address_8": "localip"}'
    #ESCAPE VARIABLE LOCALIP TO PAYLOAD
    payloadip = payloadip.replace('localip', localip)

    # update ip address of asset
    A.updateDevice(server, token, assetID(), payloadip)
    # print (r)

def updateCpuasset():
    #update cpu of asset
    #get cpu
    cpu = getCpu()
    #convert cpu to string
    cpu = str(cpu)
    # print(cpu)
    payloadcpu = '{"_snipeit_cpu_2": "cxpu"}'
    #ESCAPE VARIABLE CPU TO PAYLOAD
    payloadcpu = payloadcpu.replace('cxpu', cpu)
    # print(payloadcpu)

    # update cpu of asset
    # c = A.updateDevice(server, token, assetID(), payloadcpu)
    A.updateDevice(server, token, assetID(), payloadcpu)
    # print (c)

def updateRamTypeasset():
    #update ram type of asset
    #get ram type
    ramtype = getRamType()
    #convert ram type to string
    ramtype = str(ramtype)
    # print(ramtype)
    payloadramtype = '{"_snipeit_ram_type_5": "ramtype"}'
    #ESCAPE VARIABLE RAM TYPE TO PAYLOAD
    payloadramtype = payloadramtype.replace('ramtype', ramtype)
    # print(payloadramtype)

    # update ram type of asset
    A.updateDevice(server, token, assetID(), payloadramtype)
    # print (r)

def updateRamasset():
    #update ram of asset
    #get ram
    ram = getRam()
    #convert ram to string
    ram = int(ram)
    #add ram to payload using f string
    payloadram = f'{{"_snipeit_ram_3": {ram}}}'


    # payloadram = f'{"_snipeit_ram_3": "{{ram}}"}'
    
    # print(payloadram)

    # update ram of asset
    A.updateDevice(server, token, assetID(), payloadram)
    # r = A.updateDevice(server, token, assetID(), payloadram)
    # print (r)

def updateGpuasset():
    #update gpu of asset
    #get gpu
    gpu = getGpu()
    #convert gpu to string
    gpu = str(gpu)

    #create if else if gpu == NVIDIA Corporation Device 2206 (rev a1) then gpu = NVIDIA RTX 3080 10 GB
    if gpu == 'NVIDIA Corporation Device 2206 (rev a1)': 
        gpu = 'NVIDIA RTX 3080 10 GB'
    elif gpu == 'NVIDIA Corporation GM206 [GeForce GTX 960] (rev a1)':
        gpu = 'NVIDIA GTX 960 4 GB'
    elif gpu == 'NVIDIA Corporation GM107 [GeForce GTX 750 Ti] (rev a2)':
        gpu = 'NVIDIA GTX 750 Ti 2 GB'
    elif gpu == 'NVIDIA Corporation GP106 [GeForce GTX 1060 3GB] (rev a1)':
        gpu = 'NVIDIA GTX 1060 3 GB'
    elif gpu == 'NVIDIA Corporation GP106 [GeForce GTX 1060 6GB] (rev a1)':
        gpu = 'NVIDIA GTX 1060 6 GB'
    elif gpu == 'NVIDIA Corporation GK106 [GeForce GTX 660] (rev a1)':
        gpu = 'NVIDIA GTX 660 2 GB'
    elif gpu == 'NVIDIA Corporation Device 1f0a (rev a1)':
        gpu = 'NVIDIA GTX 1650 4 GB'
    elif gpu == 'NVIDIA Corporation Device 1f08 (rev a1)':
        gpu = 'NVIDIA GTX 2060 6 GB'


    # print(gpu)
    payloadgpu = f'{{"_snipeit_gpu_4": "{gpu}"}}'
    #ESCAPE VARIABLE GPU TO PAYLOAD
    
    # print(payloadgpu)

    # update gpu of asset
    A.updateDevice(server, token, assetID(), payloadgpu)
    # print (r)


def getMainDisk():
    outputParted = subprocess.check_output(['parted', '-lm'])
    outputParted = outputParted.decode('utf-8')
    # print(outputParted)
    # print(outputParted)

    disk = []
    for i, line in enumerate(outputParted.splitlines()):
        if 'BYT' in line:
            
            diskName = outputParted.splitlines()[i+1].split(':')[6]
            diskSize = outputParted.splitlines()[i+1].split(':')[1]
            lineContainboot = outputParted.splitlines()[i+2]
            # print(lineContainboot)
            if 'boot' in lineContainboot:
                
                disk.append(diskName)
                disk.append(diskSize)
                
                r = disk[0] + ' ' + disk[1]
                return r
            else:
                pass
        else:
            pass

    # print(disk)

def getSecondaryDisk():
    outputParted = subprocess.check_output(['parted', '-lm'])
    outputParted = outputParted.decode('utf-8')
    # print(outputParted)
    # print(outputParted)

    disk = []
    for i, line in enumerate(outputParted.splitlines()):
        if 'BYT' in line:
            # print(line)
            # print(i)
            # print(outputParted.splitlines()[i+1])
            # print(outputParted.splitlines()[i+1].split(':')[0])
            diskName = outputParted.splitlines()[i+1].split(':')[6]
            diskSize = outputParted.splitlines()[i+1].split(':')[1]
            lineContainboot = outputParted.splitlines()[i+2]
            # print(lineContainboot)
            if 'boot' in lineContainboot:
                # print(lineContainboot)
                # print(lineContainboot.split(':')[0])
                pass
            else:
                disk.append(diskName)
                disk.append(diskSize)
                # print(disk)
                # print('xx')
                r = disk[0] + ' ' + disk[1]
                return r
        else:
            pass

    # print(disk)



            
    


    
def updateMainDiskasset():
    #update main disk of asset
    #get main disk
    maindisk = getMainDisk()
    #convert main disk to string
    maindisk = str(maindisk)
    # print(maindisk)
    payloadmaindisk = f'{{"_snipeit_main_storage_6": "{maindisk}"}}'
    
    # print(payloadmaindisk)

    # update main disk of asset
    A.updateDevice(server, token, assetID(), payloadmaindisk)
    # print (r)

def updateSecondaryDiskasset():
    #update secondary disk of asset
    #get secondary disk
    secondarydisk = getSecondaryDisk()
    #convert secondary disk to string
    secondarydisk = str(secondarydisk)
    # print(secondarydisk)
    payloadsecondarydisk = f'{{"_snipeit_secondary_storage_7": "{secondarydisk}"}}'
    
    # print(payloadsecondarydisk)

    # update secondary disk of asset
    A.updateDevice(server, token, assetID(), payloadsecondarydisk)
    # print (r)

def getUser():
    #get user login this computer using command who
    outputWho = subprocess.check_output(['who'])
    outputWho = outputWho.decode('utf-8')
    # print(outputWho)
    # print(outputWho.split(' ')[0])
    user = outputWho.split(' ')[0]

    # # exclude root and anima users
    # if user == 'root' or user == 'anima':
    #     return ''
    # else:
    #     return user

    return user
    


def checkoutAssetToUser():
    #checkout asset to user
    #get user login this computer using command who
    user = getUser()

    # exclude root and anima users
    if user == 'root' or user == 'anima':
        return

    user_id = U.getID(server, token, user)

    # user_id = U.getID(server, token, getUser())
    # print(user_id)

    def checkout():
        #start checkout asset to user
        payload_checkin = {
                    "status_id": 2
                }
        checkin = A.checkIn(server, token, assetID(), payload_checkin)
        #checkout

        #run 2nd time incase 1st time user_id is not found
        user_id = U.getID(server, token, user)

        payload_checkout = {
                    "checkout_to_type": "user",
                    "assigned_user": user_id,
                    "status_id": 2
                }
        headers = {
                    "accept": "application/json",
                    "Authorization": "Bearer " + token,
                    "content-type": "application/json"
                } 

        urlcheckout = server + '/api/v1/hardware/' + str(assetID()) + '/checkout'
        checkout = requests.post(urlcheckout, json=payload_checkout, headers=headers)
        checkout = checkout.json()
        statusCheckout = checkout['status']
        # print(statusCheckout)

        if statusCheckout == 'success':
            print(f'Checkout asset to user {getUser()} success')
        else:
            print(f'Checkout asset to user {getUser()} failed')
            print(statusCheckout)
            return
            
    def createuser():
        #parse sheet alluser
        #get all user from sheet
        # read CSV file into a pandas dataframe
        df = pd.read_csv(urlsheet)

        # select rows where the username column matches the user name returned by getUser()
        df = df.loc[df['username'] == getUser()]

        # check if the dataframe is empty
        #CSV FILE is sheet in google drive, urlsheetx is url of sheet, 
        if df.shape[0] == 0:
            print(f"Error: user {getUser()} not found in CSV file")
            return

        # extract the firstname and lastname values from the dataframe
        firstname = df['firstname'].values[0]
        lastname = df['lastname'].values[0]
        usernamex = df['username'].values[0]


        # print(user)
        # print(usernamex)
        # print(firstname)
        # print(lastname)
        if usernamex == getUser():
            #create user on inventory
            payloadCreateuser = f'{{"username":"{usernamex}","first_name":"{firstname}","last_name":"{lastname}","password":"sCX3&Y30uzBl4*!","password_confirmation":"sCX3&Y30uzBl4*!"}}'
            urlcreateuser = U.create(server, token, payloadCreateuser)
            print ("Creating "+usernamex)

        else:
            pass


        #start create user
        


    if user_id == 'notfound':
        print('not found user to checkout')
        createuser()
        checkout()
        #need to create user on inventory
    else:
        checkout()






print (f'Get Info {getHostname()} ...')
print(f'Current user : {getUser()}')
# print(getGpu())
# print(getRamType())
# print(getRam())    
# print(getCpu())
# print('##########')
# print(getAllDisk())
# print(getMainDisk())
# # print('######2nd####')
# print(getSecondaryDisk())

# print(getMac())
# print(getLocalIp())


#####################
# update asset data #
#####################

if assetID() == 'notfound':
    #need to create asset on inventory
    print('not found asset to update')
else:
    #start update asset
    checkoutAssetToUser()
    updateIPasset()
    updateCpuasset()
    updateRamTypeasset()
    updateRamasset()
    updateGpuasset()
    updateMainDiskasset()
    updateSecondaryDiskasset()
    print("Asset details spec updated ...")
    





