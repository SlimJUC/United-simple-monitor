
##########################################################
#  Script Name: CPU,RAM,HDD-Monitor                      #
#  Author: Slim Jay                                      #
#  Date: July 18 2020                                    #
#  e-mail: Slim@uigtc.com                                #
#  Description: Python + Bash                            #
#  sends an email alert when CPU, RAM or HD is maxed     #
#                                                        #
#  Usage:                                                #
#      Just Add this .py file to crontab                 #
#      and make it run every 1 min eg. * * * * *         #
#                                                        #
#  Rquirements: Python >3.x                              #
##########################################################

import smtplib, ssl,socket, shutil, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


################ Calculating Hardware Usage

# Get Droplet IP Address
Server_IP=str(os.popen('curl ifconfig.me').readline())
# Get CPU Load
CPU_Load=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
# Get Available Memeory
FreeMem=str(os.popen(''' free -m | awk '/Mem:/ { print $4 }' ''').readline()) 
# Get Disk Remaining Space
total, used, free = shutil.disk_usage(__file__) 
# Math to convert KB to MB
Hard_Disk = free // (2**30)


# Sending Alerts Function, Change the vlaues to your own |
# Although a dummy account @uigtc.com would be nice so all can use it

def mail2():
    global CPU_Load, Server_IP, Hard_Disk
    fromaddr = "email@DOMAIN.com" # Change Me!
    toaddr = "email@DOMAIN.com" # Change Me!
    msg = MIMEMultipart() 
    msg['From'] = fromaddr 
    msg['To'] = toaddr 
    msg['Subject'] = "Server Warning " + socket.gethostname() 
    body = "Server IP " + Server_IP + " CPU Load " + CPU_Load + "%" + " Free Memory "+ FreeMem + "/MB " + " Remaining Disk Space: " + str(Hard_Disk) + "GB"
    msg.attach(MIMEText(body, 'plain')) 
    email = smtplib.SMTP('smtp.gmail.com', 587) 
    email.starttls() 
    email.login(fromaddr, "PASSWORD-HERE") # Change Me!
    message = msg.as_string() 
    email.sendmail(fromaddr, toaddr, message) 
    email.quit()



# Executing Alert Function 

if CPU_Load >= str(90.0):
    mail2()
elif Hard_Disk <= 5:
    mail2()
elif FreeMem <= str(2000):
    mail2()
else:
    print("All is Ok")
