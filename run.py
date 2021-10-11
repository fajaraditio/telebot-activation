from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from telethon import TelegramClient
from shutil import copytree
import asyncio
import time
import csv


async def telegramInit(phoneNumber, appId, appHash, sessionFolder):
    print(phoneNumber)

    client = TelegramClient(sessionFolder, appId, appHash)
    
    await client.start(phoneNumber)
    await client.sign_in(phoneNumber)
    code = input('enter code: ')
    await client.sign_in(phoneNumber, code)

    client.disconnect()


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

        with open('telebot.csv', 'w', encoding='UTF8', newline='') as CSVFile:
            CSVWriter = csv.writer(CSVFile)
            CSVWriter.writerow(['phoneNumber', 'appId', 'appHash'])
            CSVWriter.writerow([phoneNumber, appId, appHash])

        runnerMaster = "runner"
        runnerStored = "stored/" + phoneNumber

        copytree(runnerMaster, runnerStored)

        sessionFolder = runnerStored + '/session/'

        telegramInit(phoneNumber, appId, appHash, sessionFolder)

        driver.close()

# DRIVE SAFE

loop = asyncio.get_event_loop()
loop.run_until_complete(telegramInit("+6283102594694", 8378843,
             "661c0553ba2d6426960dcf011ea23afc", "stored/+6283102594694/session"))
