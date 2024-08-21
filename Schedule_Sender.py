from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import os
from datetime import timedelta, date
import smtplib
from email.message import EmailMessage
import re

sender_email = os.environ.get("SENDER_EMAIL")
sender_password = os.environ.get("SENDER_PASSWORD")

while (True):
    # email setup
    msg = EmailMessage()
    msg['Subject'] = 'Shift Reminder'
    msg['From'] = "farmboyShiftReminder@gmail.com"
    msg['To'] = "EMAIL"

    tomorrow = date.today() + timedelta(days=1) # get current day

    # Enter email
    driver = webdriver.Firefox()
    driver.get("https://myfarmboy.ca/login/")
    email = driver.find_element(By.XPATH, "/html/body/div/div/div/div/form/div/div[1]/input")
    email.clear()
    email.send_keys("EMAIL")

    # Enter password
    password = driver.find_element(By.XPATH, "/html/body/div/div/div/div/form/div/div[2]/input")
    password.clear()
    password.send_keys("PASSWORD")
    password.send_keys(Keys.RETURN)

    driver.implicitly_wait(10) # wait up to 10 seconds for page to load 

    latestShift = driver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div[1]/div/div/p")
    latestShiftDay = re.findall(r'\d+', latestShift.text) # get all the numerical values 
    if latestShiftDay[0] == tomorrow: # check if I have a shift tomorrow
    # send email
        msg.set_content(latestShift.text)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("farmboyShiftReminder@gmail.com", "uittsrygrdlhouny")
        server.send_message(msg)
        server.quit()
    else:
        print("No Shift Tomorrow")

    driver.find_element(By.XPATH, "/html/body/div/div/div/nav/div/div/div[1]/div[3]/div/a[2]").click() # click on schedule
    time.sleep(10) # wait a bit
    old_shifts = re.findall(r'(\d{1,2}:\d{2} [AP]M) to (\d{1,2}:\d{2} [AP]M)', driver.page_source) # get the times
    shifts = re.findall(r'(\d{1,2}:\d{2} [AP]M) to (\d{1,2}:\d{2} [AP]M)', driver.page_source) # get them again
    try:
        for x in range(len(shifts)): # loop through them
            if shifts[x] != old_shifts[x]: # see if anything was changed during that time
                print("Shift at " + str(old_shifts[x]) + " has been changed to " + str(shifts[x]))

                # if there were changes send an email with what was changed
                msg.set_content("Shift at " + str(old_shifts[x]) + " has been changed to " + str(shifts[x]))
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()
            else:
                print("No shift change")
    except IndexError:  
        print("IndexError (ignore)")

    driver.close()
    time.sleep(43200) # check again after 12 hours (or however long you want)