import os
import yagmail

from time import sleep, strptime
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()
URL = "https://visa.vfsglobal.com/ind/en/deu/login"
VFS_USERNAME = os.environ['VFS_USERNAME']
VFS_PASSWORD = os.environ['VFS_PASSWORD']

SENDER_EMAIL = os.environ['SENDER_EMAIL']
APP_PASSWORD = os.environ['APP_PASSWORD']
RECEIVER_EMAIL = os.environ['RECEIVER_EMAIL']


def login():
    wait = WebDriverWait(driver, 20)

    wait.until(EC.title_contains('Login'))

    # reject all cookies
    wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()

    # fill up username & pwd in the text fields
    email_elem = driver.find_element_by_id('mat-input-0')
    email_elem.send_keys(VFS_USERNAME)

    pwd_elem = driver.find_element_by_id('mat-input-1')
    pwd_elem.send_keys(VFS_PASSWORD)

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'mat-button-wrapper')))

    # wait for sometime before clicking the sign in button
    sleep(2)

    sign_in_button = driver.find_element_by_class_name('mat-button-wrapper')
    sign_in_button.click()


def go_to_homepage():
    # it's not possible to refresh the page. So, click on the top left VFS Global image to go to homepage
    home_elem = driver.find_element_by_xpath('/html/body/app-root/header/div[1]/div/a/img')
    home_elem.click()
    sleep(3)


def click_until_last_category():
    wait = WebDriverWait(driver, 20)
    # new booking
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.d-none > span:nth-child(1)'))).click()

    # choose New Delhi
    sleep(2)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-select-value-1"]'))).click()
    driver.find_elements_by_class_name('mat-option-text')[12].click()

    # schengen visa
    sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-select-value-3"]'))).click()
    driver.find_elements_by_class_name('mat-option-text')[-1].click()

    sleep(3)
    return


def click_last_category(pos):
    wait = WebDriverWait(driver, 20)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-select-value-5"]'))).click()
    driver.find_elements_by_class_name('mat-option-text')[pos].click()
    sleep(2)
    return get_appointment_info()


def preprocess_appointment_date(appointment_date):
    ad = appointment_date
    month = ad[:3]
    day = ad.split()[1].replace(',', '').zfill(2)
    year = ad[-4:]
    return f'{month} {day}, {year}'


def earlier_than_deadline(appointment, deadline):
    """check whether the appointment date is earlier than the preferred deadline date.
    Both dates should be in the format 'Jan 31, 2022'"""

    deadline_date = strptime(deadline, '%b %d, %Y')
    appointment_date = strptime(preprocess_appointment_date(appointment), '%b %d, %Y')

    return ((appointment_date.tm_year <= deadline_date.tm_year) and
            (appointment_date.tm_mon <= deadline_date.tm_mon) and
            (appointment_date.tm_mday <= deadline_date.tm_mday))


def cycle_last_category():
    """ keep changing the last category alternately to force reload the status.
    This way, it's fast and doesn't need to go through all the options from the start again """

    COUNTER = 0
    DEADLINE = 'Oct 20, 2022'
    last_appointment_text = None
    while True:
        text = click_last_category(11)
        appointment_date = text.split(':')[-1].strip()
        if ((not text.startswith('No appointment')) and
            (earlier_than_deadline(appointment_date, DEADLINE)) and
            (text != last_appointment_text)):
            last_appointment_text = text
            print(text)
            send_email(text)
            print('sleeping for 2 minutes')
            sleep(120)
        else:
            _ = click_last_category(10)  # or anything other than our required category
            COUNTER += 1
            if not COUNTER%100:
                print('restarting to clear cookies...')
                break
    sleep(1)


def get_appointment_info():
    # grab appointment info from the alert box
    alert_box = driver.find_element_by_css_selector('.alert')
    text = alert_box.text

    return text


def send_email(text):
    subject = 'DE VISA 🇩🇪 Appointment vacancy alert'
    content = [f'Appointment for VISA: {text}']

    with yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD) as yag:
        yag.send(RECEIVER_EMAIL, subject, content)


def get_profile():
    # return profile with cache disabled
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    return profile


if __name__ == "__main__":
    # keep checking for appointments forever (unless stopped explicitly from cmdline)
    while True:
        try:
            profile = get_profile()
            driver = webdriver.Firefox(profile)
            driver.get(URL)

            login()
            sleep(5)

            # select first two categories and cycle the last one
            click_until_last_category()
            cycle_last_category()

        except Exception as e:
            print(f'error encountered: {e}')
        finally:        
            driver.delete_all_cookies()
            sleep(2)
            driver.quit()

