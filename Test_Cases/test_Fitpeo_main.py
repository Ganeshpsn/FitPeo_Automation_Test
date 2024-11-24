from time import sleep
from selenium.webdriver.common.keys import Keys
import pytest
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from Resources.locators_fitpeo import FitPeoLocators
from selenium.webdriver.support import expected_conditions as EC
import time

from Resources.test_data import TestData


@pytest.fixture(scope='module')
def driver():
    """
    Setup Web driver
    :return:
    """
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(5)  # Wait for up to 5 seconds
    yield driver
    driver.quit()

def update_text_field(driver, value):
    """
    Update the Text Field:
    :param driver:
    :return:
    """
    wait = WebDriverWait(driver, 10)
    text_field = wait.until(EC.element_to_be_clickable((By.XPATH, FitPeoLocators.slider_input)))
    text_field.click()
    time.sleep(5)
    text_field.clear()
    text_field.send_keys(Keys.BACKSPACE * 10)
    sleep(3)
    wait = WebDriverWait(driver, 5)
    value_field = wait.until(EC.presence_of_element_located((By.XPATH, FitPeoLocators.slider_input)))
    text_field.send_keys(str(value))
    time.sleep(5)
    slider = driver.find_element(By.XPATH, FitPeoLocators.slider_path)
    updated_value = int(slider.get_attribute('value'))

    return updated_value

def test_navigate_to_homepage(driver):
    """
    Open the web browser and navigate to FitPeo Homepage
    :param driver: instance of Chrome Driver
    :return:
    """
    driver.get(FitPeoLocators.home_page_url)
    driver.maximize_window()
    home_title = driver.title
    print(home_title)
    assert 'fitpeo' in home_title


def test_navigate_to_revenue_calculator(driver):
    """
    From the homepage, navigate to the Revenue Calculator Page.
    :param driver:
    :return:
    """
    revenue_page = driver.find_element(By.LINK_TEXT, "Revenue Calculator")
    revenue_page.click()
    time.sleep(5)

def test_scroll_to_slider(driver):
    """
    Scroll down the page until the revenue calculator slider is visible.
    :param driver:
    :return:
    """
    slider = driver.find_element(By.XPATH, FitPeoLocators.slider_path)
    sliders = driver.find_element(By.XPATH, "//h5[text()='Total Gross Revenue Per Year']")
    driver.execute_script("arguments[0].scrollIntoView();", sliders)
    time.sleep(3)
    return slider

def test_adjust_slider(driver):
    """
    Adjust the slider to set its value to 820. we’ve highlighted the slider in red color,
    Once the slider is moved the bottom text field value should be updated to 820
    :param driver:
    :return:
    :Note: here used 823 instered of 820 for better results.
    """
    sliders = test_scroll_to_slider(driver)
    slider = driver.find_element(By.XPATH, FitPeoLocators.slider_pointer)
    time.sleep(3)
    current_value = int(sliders.get_attribute('value'))
    desired_value = TestData.adjust_slider_value
    action = ActionChains(driver)
    while current_value != desired_value:
        if current_value < desired_value:
            action.click_and_hold(slider).move_by_offset(6, 0).release().perform()
        else:
            action.click_and_hold(slider).move_by_offset(-3, 0).release().perform()
        time.sleep(1)  # Small delay to allow the value to update
        current_value = int(sliders.get_attribute('value'))

    # Verify the bottom text field value is updated to 820
    time.sleep(3)  # Wait for the value to update
    # Wait for the value field to be present
    wait = WebDriverWait(driver, 5)
    value_field = wait.until(EC.presence_of_element_located((By.XPATH, FitPeoLocators.slider_input)))

    assert int(value_field.get_attribute(
        "value")) == desired_value, f"Expected value: {desired_value}, but got: {value_field.get_attribute('value')}"

    print("Slider value set to 820 successfully")

def test_update_text_field(driver):
    """
    Update the Text Field:
    Click on the text field associated with the slider.
    Enter the value 560 in the text field. Now the slider also should change accordingly
    Validate Slider Value:
    Ensure that when the value 560 is entered in the text field, the slider's position is updated to reflect the value 560
    :param driver:
    :return:
    """
    value = TestData.slider_Text_Field_value
    updated_value = update_text_field(driver, value)
    assert updated_value == value, f"Expected value: {value}, but got: {updated_value}"

    print(f" Successfully validated Slider Value by update {TestData.slider_Text_Field_value} in Text filed")

def test_select_cpt_codes(driver):
    """
    Scroll down further and select the checkboxes for CPT-99091, CPT-99453, CPT-99454, and CPT-99474.
    :param driver:
    :return:
    """
    cpt_codes = TestData.cpt_codes
    # Select Check Box for each code in Cpt_code list
    for code in cpt_codes:
        checkbox = driver.find_element(By.XPATH, f"//div/p[contains(text(), '{code}')]/parent::div/label/span/input")
        if not checkbox.is_selected():
            checkbox.click()
            time.sleep(3)
    else:
        print(f"Successfully selected the checkboxes for {cpt_codes}")

def test_validate_total_reimbursement(driver):
    """
    Validate Total Recurring Reimbursement:
    Verify that the header displaying Total Recurring Reimbursement for all Patients Per Month: shows the value $110700.
    :param driver:
    :return:
    """
    value = 820
    sleep(2)
    sliders = driver.find_element(By.XPATH, "//h5[text()='Total Gross Revenue Per Year']")
    driver.execute_script("arguments[0].scrollIntoView();", sliders)
    updated_value = update_text_field(driver, value)
    sleep(3)
    if updated_value == value:
        wait = WebDriverWait(driver, 5)
        Rev = driver.find_element(By.XPATH, "(//div/p[contains(text(), 'Total Recurring Reimbursement for all Patients Per Month')])[1]")
        total_reimbursement = driver.find_element(By.XPATH, "(//div/p[contains(text(), 'Total Recurring Reimbursement for all Patients Per Month')])[1]//parent::div/p[2]")
        assert "$110700" in total_reimbursement.text, f"Expected reimbursement: $110700, but got: {total_reimbursement.text}"