
##########################################################
#  Script Name: CPU,RAM,HDD-Monitor                      #
#  Author: Slim Jay                                      #
#  Date: July 18 2020                                    #
#  e-mail: Slim@uigtc.com                                #
#  Description: Python + Bash                            #
#  sends a MatterMost alert when CPU, RAM or HD is maxed     #
#                                                        #
#  Usage:                                                #
#      Just Add this .py file to crontab                 #
#      and make it run every 1 min eg. * * * * *         #
#                                                        #
#  Rquirements: Python >3.x                              #
##########################################################

import requests, socket, shutil, os, logging, configparser

logging.basicConfig(filename='monitor.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

config = configparser.ConfigParser()

# Load the config file if it exists, or create it with default values
if os.path.exists('config.ini'):
    config.read('config.ini')
else:
    config['thresholds'] = {
        'cpu': '90',
        'memory': '2000',
        'disk': '5'
    }
    config['notifications'] = {
        'mattermost_url': 'https://your-mattermost-url.com/hooks/your-hook-id'
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Get threshold values from configuration file
cpu_threshold = config.getint('thresholds', 'cpu')
mem_threshold = config.getint('thresholds', 'memory')
disk_threshold = config.getint('thresholds', 'disk')

def send_mattermost_message(message):
    url = config.get('notifications', 'mattermost_url')
    headers = {'Content-Type': 'application/json'}
    data = {'text': message}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            logging.error('Error sending Mattermost message')
    except requests.exceptions.Timeout:
        logging.error('Mattermost connection timed out')
    except requests.exceptions.RequestException as e:
        logging.error(f'Error sending Mattermost message: {e}')

def mattermost_alert():
    global CPU_Load, Server_IP, Hard_Disk
    message = "Server Warning: " + socket.gethostname() + "\n" + \
              "Server IP: " + Server_IP + "\n" + \
              "CPU Load: " + CPU_Load + "%" + "\n" + \
              "Free Memory: " + FreeMem + "/MB" + "\n" + \
              "Remaining Disk Space: " + str(Hard_Disk) + "GB"
    send_mattermost_message(message)
    logging.warning(message)

# Get Droplet IP Address
Server_IP=str(os.popen('curl ifconfig.me').readline())
# Get CPU Load
CPU_Load=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
# Get Available Memory
FreeMem=str(os.popen(''' free -m | awk '/Mem:/ { print $4 }' ''').readline())
# Get Disk Remaining Space
total, used, free = shutil.disk_usage(__file__)
# Math to convert KB to MB
Hard_Disk = free // (2**30)

if float(CPU_Load) >= cpu_threshold:
    mattermost_alert()
if int(FreeMem) <= mem_threshold:
    mattermost_alert()
if Hard_Disk <= disk_threshold:
    mattermost_alert()
else:
    logging.info('All is OK')
