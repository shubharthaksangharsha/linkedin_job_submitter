from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException  # Import the exception
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select

from time import sleep

# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument(f"--user-data-dir=/home/shubharthak/snap/chromium/common/chromium/")


# Set up the Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

# Navigate to the form site
form_site = 'https://www.linkedin.com/in/shubharthaksangharsha/'
driver.get(form_site)
print(driver.title)

# Function to click on the easy apply button
def click_easy_apply(search):
    apply_buttons = driver.find_elements(By.CSS_SELECTOR, 'span.artdeco-button__text')
    for button in apply_buttons:
        if button.text == search:
            # Use ActionChains to click the button
            actions = ActionChains(driver)
            actions.move_to_element(button)
            actions.click(button)
            actions.perform()
            return  # Exit the function after clicking the button

# Function to check if a button with the specified text exists
def check_button(search):
    driver.switch_to.window(driver.current_window_handle)
    print('Switched window')
    apply_buttons = driver.find_elements(By.CSS_SELECTOR, 'span.artdeco-button__text')
    #Create Actions button 
    actions = ActionChains(driver)
    # Iterate through the buttons and check if the text matches
    for button in apply_buttons:
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        if button.text == search:
            actions.move_to_element(button)
            actions.perform()
            print(button.text)
            return button  # Return the button element
    return None  # Return None if no buttons with the specified text are found

# Function to fill out the form based on user input
def fill_out_form(answers):
    # Find the text fields, select options, and radio buttons on the LinkedIn Easy Apply form
    dialog_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test-modal]')))

    input_fields = dialog_box.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
    select_options = dialog_box.find_elements(By.CSS_SELECTOR, 'select')
    radio_buttons = dialog_box.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')

    # Fill out the form with the provided answers
    for field in input_fields:
        label = field.find_element(By.XPATH, './preceding-sibling::label[1]')
        # Check if the field is already filled
        if field.get_attribute('value') != '':
            print(f"Field '{label.text}' is already filled.")
            continue  # Skip to the next field

        if label.text in answers:
            # If the answer is already provided, use it
            field.send_keys(answers[label.text])
        else:
            # If the answer is not provided, prompt the user
            answer = input(f"Enter answer for '{label.text}': ")
            field.send_keys(answer)
            answers[label.text] = answer  # Store the answer for future use

    # Handle radio buttons
    for radio in radio_buttons:
        # Find the label associated with the radio button using the 'aria-labelledby' attribute
        label_id = radio.get_attribute('aria-labelledby')
        if label_id:
            label = driver.find_element(By.ID, label_id)
        else:
            # If 'aria-labelledby' is not present, find the label by its position            
            label = driver.find_element(By.XPATH, f"//label[contains(text(), '{radio.get_attribute('value')}')]")


        if label.text in answers:
            # If the answer is already provided, select the radio button
            if answers[label.text].lower() == 'yes':
                if not radio.is_selected():
                    try:
                        # Attempt to click the radio button
                        radio.click()
                    except (ElementClickInterceptedException, StaleElementReferenceException):
                        # If the click is intercepted or the element is stale, scroll to the element and try again
                        actions = ActionChains(driver)
                        actions.move_to_element(radio).perform()
                        radio.click()
            elif answers[label.text].lower() == 'no':
                if radio.is_selected():
                    try:
                        # Attempt to click the radio button
                        radio.click()
                    except (ElementClickInterceptedException, StaleElementReferenceException):
                        # If the click is intercepted or the element is stale, scroll to the element and try again
                        actions = ActionChains(driver)
                        actions.move_to_element(radio).perform()
                        radio.click()
        else:
            # If the answer is not provided, prompt the user and select the radio button
            answer = input(f"Choose 'Yes' or 'No' for '{label.text}': ")
            if answer.lower() == 'yes':
                if not radio.is_selected():
                    try:
                        # Attempt to click the radio button
                        radio.click()
                    except (ElementClickInterceptedException, StaleElementReferenceException):
                        # If the click is intercepted or the element is stale, scroll to the element and try again
                        actions = ActionChains(driver)
                        actions.move_to_element(radio).perform()
                        radio.click()
            elif answer.lower() == 'no':
                if radio.is_selected():
                    try:
                        # Attempt to click the radio button
                        radio.click()
                    except (ElementClickInterceptedException, StaleElementReferenceException):
                        # If the click is intercepted or the element is stale, scroll to the element and try again
                        actions = ActionChains(driver)
                        actions.move_to_element(radio).perform()
                        radio.click()
            answers[label.text] = answer  # Store the answer for future use
        return answers

# Handle select options
    for select in select_options:
        label = select.find_element(By.XPATH, './preceding-sibling::label[1]')
        if label.text in answers:
            # If the answer is already provided, select the option
            select_element = Select(select)
            select_element.select_by_visible_text(answers[label.text])
        else:
            # If the answer is not provided, prompt the user and select the option
            # Display the options to the user
            options = [option.text for option in select.find_elements(By.TAG_NAME, 'option')]
            print(f"Options for '{label.text}':")
            for idx, option in enumerate(options):
                print(f"{idx + 1}. {option}")

            # Ask the user to choose an option
            choice = input(f"Choose an option (1-{len(options)}): ")
            selected_option = options[int(choice) - 1]
            select_element = Select(select)
            select_element.select_by_visible_text(selected_option)
            answers[label.text] = selected_option  # Store the answer for future use

def check_for_error_messages():
    error_messages = driver.find_elements(By.CSS_SELECTOR, '.artdeco-inline-feedback__message')
    return any(error_messages)

# Function to click the close button
def click_close_button():
    try:
        # Wait for the element to be clickable
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
        close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'artdeco-button__icon')))

        # Now the element is clickable, so you can click on it
        close_button.click()
    except StaleElementReferenceException:
        # The element is stale, so you need to re-find it
        print("Element is stale, trying to click again...")
        click_close_button()  # Recursively call the function to click the button


# Main loop
try:
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
    # Navigate to the job section
    job = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/header/div/nav/ul/li[3]/a')))
    driver.execute_script("arguments[0].scrollIntoView(true);", job)
    job.click()

    print('Clicked Job')
    # Click on the "Show more" button
    show_more = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div/div[3]/div/div/main/div/div[1]/div[1]/div/div/div/section/div[2]/a')))
    driver.execute_script("arguments[0].scrollIntoView(true);", job)
    print('Clicked Show More')
    sleep(2)

    # Wait for the job list elements to be visible
    li_elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'li.job-card-container__apply-method.job-card-container__footer-item.inline-flex.align-items-center')))

    print(f'Found {len(li_elements)} Jobs')

    for li_element in li_elements:
        driver.execute_script("arguments[0].scrollIntoView(true);", li_element)

        # Get the coordinates of the element
        x, y = li_element.location['x'], li_element.location['y']
        width, height = li_element.size['width'], li_element.size['height']

        # Click on the element
        driver.execute_script(f"window.scrollTo({x},{y});")
        try:
            li_element.click()
        except ElementClickInterceptedException:
            actions = ActionChains(driver)
            actions.move_to_element(li_element)
            actions.click()
            actions.perform()
        print('Clicked Job')
        sleep(5)
        
        click_easy_apply('Easy Apply')

        while True:
            if check_for_error_messages():
                print('incomplete field occured while filling the form, so filling the form')
                fill_out_form({})
                continue

            # Check if the "Review" button is present
            sleep(1)
            print('Checking Review Button Before')
            review_button = check_button('Review')
            if review_button:
                print('Trying to click review button ')
                
                try:
                    review_button.click()  # Click the "Review" button
                    print('Clicked review button')
                except:
                    print('Unable to click review button')
                    pass
                error = check_for_error_messages()
                print('empty field found:',error)
                if error:
                    print('empty field occured, so filling the form')
                    fill_out_form(answers={})
                    review_button.click()
                    print('Clicked review button')
                    break
                else:                
                    print('Clicked Review Button Successfully')
                    break  # Exit the loop after clicking the button
            print('Checking Next Button Before')
            next_button = check_button('Next')
            if next_button:
                print('Trying to click next button ')
                next_button.click()  # Click the "Next" button
                print('Clicked Next Button')
                error = check_for_error_messages()
                print('empty field found:',error)
                if error:
                    print('empty field occured, so filling the form')
                    fill_out_form(answers={})
                    next_button.click()
                    print('filled the button now Clicked next button')
                    
                else:
                    print('Clicked Next Button Successfully')
            else:
                print('Exit button is not present so breaking ')
                break  # If "Next" button is not present, break the loop
        submit_btn = check_button('Submit application')
        if submit_btn:
            print('Trying to click submit button ')
            submit_btn.click()  # Click the "Submit" button
            print('Clicked Submit Button')
            sleep(3)
            try:
                click_close_button()
            except: 
                print('Unable to click close button')
                pass
            print('Click the close button too')
            # break

        else:
            print('Submit button is not present so breaking ')
            break  # If "Submit" button is not present, break the loop
        
finally:
    print('Done...')
    pass
    # Close the browser window
    # driver.quit()