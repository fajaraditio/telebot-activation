from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from telethon import TelegramClient
from shutil import copytree
import asyncio
import time
import csv
import json
import re
import os


async def telegramInit(phoneNumber, appId, appHash, sessionFolder):
    print("Send Code:" + phoneNumber)

    client = TelegramClient(sessionFolder, appId, appHash)

    await client.connect()
    codeSent = await client.send_code_request(phoneNumber)
    # await client.disconnect()

    return codeSent

async def telegramLogin(phoneNumber, appId, appHash, sessionFolder, code, phoneCodeHash):
    print("Login: " + phoneNumber)
    client = TelegramClient(sessionFolder, appId, appHash)

    await client.connect()
    await client.sign_in(phone=phoneNumber, code=code, password=None, bot_token=None, phone_code_hash=phoneCodeHash)
    # await client.disconnect()

def drivingBrowser():
    driver = webdriver.Firefox()
    driver.get("https://web.telegram.org/k/")

    time.sleep(30)

    waitingDriver = WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, 'SearchInput')))

    if (waitingDriver == True):
        btnMenu = driver.find_element_by_css_selector(
            "div.btn-icon.btn-menu-toggle.rp.sidebar-tools-button")
        btnMenu.click()

        btnSetting = driver.find_element_by_css_selector(
            "div.btn-menu-item.tgico-settings.rp")
        btnSetting.click()

        phoneNumberSpan = driver.find_element_by_css_selector(
            "div.sidebar-content div.profile-subtitle")
        phoneNumber = phoneNumberSpan.text.replace(' ', '')

        print(phoneNumber)

        driver.execute_script(
            "window.open('https://my.telegram.org','_blank');")

        driver.switch_to.window(driver.window_handles[1])

        time.sleep(5)

        myPhoneNumber = driver.find_element_by_id("my_login_phone")
        myBtnSubmit = driver.find_element_by_xpath("//button[@type='submit']")

        myPhoneNumber.send_keys(phoneNumber)
        myBtnSubmit.click()

        driver.switch_to.window(driver.window_handles[0])

        backBtn = driver.find_element_by_css_selector(
            "button.btn-icon.tgico-left.sidebar-close-button")
        backBtn.click()

        telegramMsg = driver.find_element_by_xpath(
            "//li[@data-peer-id='777000']")
        telegramMsg.click()

        time.sleep(5)

        telegramChats = driver.find_elements_by_xpath(
            "//div[@class='message']")

        chats = []
        for currentChat in telegramChats:
            chats.append(currentChat.text)

        telegramCode = chats[len(chats) - 1]
        telegramCode = telegramCode.split('\n')[1]

        print(telegramCode)

        driver.switch_to.window(driver.window_handles[1])

        time.sleep(5)

        myPassword = driver.find_element_by_id("my_password")

        myPassword.send_keys(telegramCode)
        myPassword.submit()

        time.sleep(5)

        linkAPIdev = driver.find_element_by_xpath("//a[@href='/apps']")
        linkAPIdev.click()

        time.sleep(5)

        appInput = driver.find_elements_by_xpath(
            "//span[@class='form-control input-xlarge uneditable-input'][@onclick='this.select();']")

        appData = []
        for currentApp in appInput:
            appData.append(currentApp.text)

        if len(appData) == 0:
            appTitleInput = driver.find_element_by_id("app_title")
            appShortnameInput = driver.find_element_by_id("app_shortname")
            platformCheckbox = driver.find_element_by_xpath(
                "//input[@value='other']")
            saveBtn = driver.find_element_by_id("app_save_btn")

            appTitleInput.send_keys("Barbara Muda")
            appShortnameInput.send_keys("barbarmud123")
            platformCheckbox.click()

            time.sleep(2)

            saveBtn.click()

            time.sleep(2)

            appInput = driver.find_elements_by_xpath(
                "//span[@class='form-control input-xlarge uneditable-input'][@onclick='this.select();']")

            appData = []
            for currentApp in appInput:
                appData.append(currentApp.text)

            appId = appData[0]
            appHash = appData[1]
        else:
            appId = appData[0]
            appHash = appData[1]

        with open('telebot.csv', 'a') as CSVFile:
            fieldnames = ['phoneNumber', 'appId', 'appHash']
            CSVWriter = csv.DictWriter(CSVFile, fieldnames=fieldnames)
            CSVWriter.writeheader()
            CSVWriter.writerow({"phoneNumber": phoneNumber, "appId": appId, "appHash": appHash})

        runnerMaster = "runner"
        runnerStored = "stored/" + phoneNumber

        if (os.path.exists("./" + runnerStored) == False):
            copytree(runnerMaster, runnerStored)

        sessionFolder = runnerStored + '/session/' + phoneNumber

        loop = asyncio.get_event_loop()
        telegramInitiate = loop.run_until_complete(telegramInit(
            phoneNumber, appId, appHash, sessionFolder))

        driver.switch_to.window(driver.window_handles[0])

        time.sleep(5)

        telegramChats = driver.find_elements_by_xpath(
            "//div[@class='message']")

        chats = []
        for currentChat in telegramChats:
            chats.append(currentChat.text)

        telegramCode = chats[len(chats) - 1]
        telegramCode = re.sub("[^0-9]", "", telegramCode)[0:5]

        print(telegramCode)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(telegramLogin(
            phoneNumber, appId, appHash, sessionFolder, telegramCode, telegramInitiate.phone_code_hash))

        JSONFile = runnerStored + "/config.json" 
        with open(JSONFile) as JSONFile:
            data = json.load(JSONFile)
            data['account']['phone'] = phoneNumber
            data['account']['api_id'] = appId
            data['account']['api_hash'] = appHash

            JSONFile.seek(0)

            json.dump(data, JSONFile, indent=4)
            JSONFile.truncate()
        # driver.close()

# DRIVE SAFE

drivingBrowser()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(telegramLogin(
#             "+6283123591441", 8811341, "649401c330298b40c4b2ddbc51c17e2f",  "stored/+6283123591441/session/", 82196, "82196abc"))
