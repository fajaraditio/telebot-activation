from __future__ import print_function, unicode_literals
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, UserStatusOffline, UserStatusRecently, UserStatusLastMonth, \
    UserStatusLastWeek
from telethon import TelegramClient, sync, connection
from PyInquirer import prompt, print_json
from shutil import copytree
from datetime import datetime, timedelta
import asyncio
import time
import csv
import json
import re
import os


async def telegramInit(phoneNumber, appId, appHash, runnerFolder):
    print("Send Code:" + phoneNumber)

    client = TelegramClient(runnerFolder + '/session/' + phoneNumber, appId, appHash)

    await client.connect()
    codeSent = await client.send_code_request(phoneNumber)
    # await client.disconnect()

    return codeSent


async def telegramLogin(phoneNumber, appId, appHash, runnerFolder, code, phoneCodeHash):
    print("Login: " + phoneNumber)
    client = TelegramClient(runnerFolder + '/session/' + phoneNumber, appId, appHash)

    await client.connect()
    await client.sign_in(phone=phoneNumber, code=code, password=None, bot_token=None, phone_code_hash=phoneCodeHash)
    # await client.disconnect()


def telegramAddGroup(phoneNumber, appId, appHash, runnerFolder):
    client = TelegramClient(runnerFolder + '/session/' + phoneNumber, appId, appHash)
    client.connect()

    if not client.is_user_authorized():
        print('Login fail, need to run init_session')
        exit()

    print('getting data ' + phoneNumber)
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    query = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))

    chats.extend(query.chats)

    for chat in chats:
        try:
            if chat.megagroup is not None and chat.access_hash is not None:
                groups.append(chat)
        except:
            continue

    results = []
    choices = []
    i = 0
    for group in groups:

        try:
            choices.append(str(i) + '. ' + str(group.title) + ' #- ' + str(group.id))

            tmp = {
                'group_id': str(group.id),
                'access_hash': str(group.access_hash),
                'title': str(group.title),
            }
            results.append(tmp)

            if group.megagroup == True:
                telegramGetUserData(client, phoneNumber, group, runnerFolder)
        except Exception as e:
            choices.append(["No choice"])
            print(e)
            print('error save group')
            
        i += 1

    with open(runnerFolder + '/data/group/' + phoneNumber + '.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    
    groupTargetPrompt = {
        'type': 'list',
        'name': 'group_target',
        'message': 'Choose Target',
        'choices': choices,
        'filter': lambda choice : choice.split('#-')[1]
    }
    
    groupSourcePrompt = {
        'type': 'list',
        'name': 'group_source',
        'message': 'Choose Source',
        'choices': choices,
        'filter': lambda choice : (choice.split('#-')[1]).replace(' ', '')
 
    }

    groupPrompt = [groupTargetPrompt, groupSourcePrompt]

    answer = prompt(groupPrompt)

    updateConfigByAnsweredPrompt(answer, runnerFolder)

def telegramGetUserData(client, phoneNumber, group, runnerFolder):
    group_id = str(group.id)
    print(group_id)

    all_participants = client.get_participants(group, aggressive=True)
    results = []
    today = datetime.now()
    last_week = today + timedelta(days=-7)
    last_month = today + timedelta(days=-30)
    path_file = runnerFolder + '/data/user/' + phoneNumber + "_" + group_id + '.json'

    for user in all_participants:
        # print(user)
        # print(type(user.status))
        try:
            if isinstance(user.status, UserStatusRecently):
                date_online_str = 'online'
            else:
                if isinstance(user.status, UserStatusLastMonth):
                    date_online = last_month
                if isinstance(user.status, UserStatusLastWeek):
                    date_online = last_week
                if isinstance(user.status, UserStatusOffline):
                    date_online = user.status.was_online

                date_online_str = date_online.strftime("%Y%m%d")
            tmp = {
                'user_id': str(user.id),
                'access_hash': str(user.access_hash),
                'username': str(user.username),
                "date_online": date_online_str
            }
            results.append(tmp)
        except:
            print("Error get user")
    with open(path_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

def updateConfigByAnsweredPrompt(answer, runnerFolder):
    JSONFile = runnerFolder + "/config.json"
    with open(JSONFile, "r+") as JSONFile:
        data = json.load(JSONFile)
        data['group_target'] = re.sub("[^0-9]", "", answer['group_target'])
        data['group_source'] = re.sub("[^0-9]", "", answer['group_source'])

        JSONFile.seek(0)

        json.dump(data, JSONFile, indent=4)
        JSONFile.truncate()


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
            CSVWriter.writerow({"phoneNumber": phoneNumber,
                               "appId": appId, "appHash": appHash})

        runnerMaster = "runner"
        runnerStored = "stored/" + phoneNumber

        if (os.path.exists("./" + runnerStored) == False):
            copytree(runnerMaster, runnerStored)

        loop = asyncio.get_event_loop()
        telegramInitiate = loop.run_until_complete(telegramInit(
            phoneNumber, appId, appHash, runnerStored))

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
            phoneNumber, appId, appHash, runnerStored, telegramCode, telegramInitiate.phone_code_hash))

        JSONFile = runnerStored + "/config.json"
        with open(JSONFile, "r+") as JSONFile:
            data = json.load(JSONFile)
            data['account']['phone'] = phoneNumber
            data['account']['api_id'] = appId
            data['account']['api_hash'] = appHash

            JSONFile.seek(0)

            json.dump(data, JSONFile, indent=4)
            JSONFile.truncate()

        telegramAddGroup(phoneNumber, appId, appHash, runnerStored)

        driver.quit()

# DRIVE SAFE


drivingBrowser()
