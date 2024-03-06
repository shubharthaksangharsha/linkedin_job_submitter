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
import csv 
import re 
from time import sleep
from bs4 import BeautifulSoup, Comment
from ingest import * 
import os 
import json
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument(f"--user-data-dir=/home/shubharthak/snap/chromium/common/chromium/")

# Set up the Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)


llm = ChatGroq(temperature=0,  model_name="mixtral-8x7b-32768", streaming=True, callbacks=[StreamingStdOutCallbackHandler()])    
embed = load_embedding_model()
vectorstore = load_vector_store(stored_path='vectorstore', embeddings=embed)
retriever = vectorstore.as_retriever()
prompt = PromptTemplate.from_template(template=template2)
chain = load_qa_chain(retriever=retriever, llm=llm, prompt=prompt)


# Navigate to the form site
form_site = 'https://www.linkedin.com/in/shubharthaksangharsha/'
driver.get(form_site)
print(driver.title)


def operate(xpath=None, click=False, type=False, instructions=None, verbose=True):
    if instructions:
        if verbose:
            print('Inside Instructions')
        for inst in instructions:
            
            if 'click' in inst[0]:
                if verbose:
                    print('Clicking the element')
                WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,inst[2]))).click()
                if verbose:
                    print('Clicked the element')
            if 'type' in inst[0]:
                if verbose:
                    print('Clicking the element to type')
                type_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,inst[2])))
                type_element.click()
                if verbose:
                    print('Clicked the element')
                type_element.send_keys(inst[1])
                if verbose:
                    print('typed the keys ')
    if click:
        if verbose:
            print('Clicking the element')
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,xpath))).click()
        if verbose:
            print('Clicked the element')
    if type:
        if verbose:
            print('Clicking the element to type')
        type_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,xpath)))
        type_element.click()
        if verbose:
            print('Clicked the element')
            type_element.send_keys(type)
        if verbose:
            print('typed the keys ')

def sign_in_linkedin(username, password):
    sign_button_xpath = '//*[@id="main-content"]/div/form/p/button'
    email_button_xpath = '//*[@id="session_key"]'
    password_button_xpath = '//*[@id="session_password"]'
    submit_button_xpath = '//*[@id="main-content"]/div/div[2]/form/div[2]/button'
    # operate(sign_button_xpath, click=True)
    # operate(email_button_xpath, type=username)
    # operate(password_button_xpath, type=password)
    operate(submit_button_xpath, click=True)


# sign_in_linkedin(os.environ.get('linkedin_username'), os.environ.get('linkedin_password') )

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
    dialog_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test-modal]')))

    # driver.switch_to.window(driver.current_window_handle)
    apply_buttons = dialog_box.find_elements(By.CSS_SELECTOR, 'span.artdeco-button__text')
    for button in apply_buttons:
        if button.text == search:
            return button  # Return the button element
    return None  # Return None if no buttons with the specified text are found

# Function to handle radio buttons
def handle_radio_buttons(answers):
    # Find all radio button groups on the page
    radio_button_groups = driver.find_elements(By.CSS_SELECTOR, 'fieldset[data-test-form-builder-radio-button-form-component="true"]')

    for group in radio_button_groups:
        # Find the legend element which contains the question text
        legend = group.find_element(By.CSS_SELECTOR, 'legend')
        question_text = legend.text

        # Find all radio buttons within the group
        radio_buttons = group.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')

        # Check if the answer is already provided
        if question_text in answers:
            # Select the radio button based on the user's answer
            answer = answers[question_text].lower()
            for radio in radio_buttons:
                if radio.get_attribute('value').lower() == answer:
                    # Attempt to click the radio button with retry logic
                    click_radio_button(radio)
                    break
        else:
            # If the answer is not provided, prompt the user and select the radio button based on their input
            print(f"Question: {question_text}")
            answer = input("Choose 'Yes' or 'No': ").lower()
            for radio in radio_buttons:
                if radio.get_attribute('value').lower() == answer:
                    # Attempt to click the radio button with retry logic
                    click_radio_button(radio)
                    break
            # Store the answer for future use
            answers[question_text] = answer

# Helper function to click a radio button with retry logic
def click_radio_button(radio, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            # Scroll the radio button into view and click it
            driver.execute_script("arguments[0].scrollIntoView(true);", radio)
            radio.click()
            return  # Successfully clicked the radio button
        except StaleElementReferenceException:
            # If the element is stale, refresh the reference and try again
            radio = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, radio.get_attribute('id')))
            )
    # If we've reached the maximum number of attempts, raise the exception
    raise StaleElementReferenceException(f"Failed to click radio button after {max_attempts} attempts.")

def get_llm_response(question):
    response = get_response(query=question, chain=chain)
    response = parse_answer(response)
    if response:
        print(response['answer'])
        return response['answer']
    else:
        print('Cant parse JSON')
    return None
# Function to fill out the form based on user input
def fill_out_form(answers, questions):
    global next_button
    # Find the text fields, select options, and radio buttons on the LinkedIn Easy Apply form
    dialog_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test-modal]')))

    input_fields = dialog_box.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
    select_options = dialog_box.find_elements(By.CSS_SELECTOR, 'select')
    radio_buttons = dialog_box.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')

    #TODO extract questions 

    # Fill out the form with the provided answers
    for i, field in enumerate(input_fields):
        try:
            label = field.find_element(By.XPATH, './preceding-sibling::label[1]')
        except:
            label = field.find_element(By.XPATH, f'//label[@for="{field.get_attribute("id")}"]')

        # Check if the field is already filled
        if field.get_attribute('value') != '':
            print(f"Field '{label.text}' is already filled.")
            continue  # Skip to the next field

        if label.text in answers:
            # If the answer is already provided, use it
            field.send_keys(answers[label.text])
        else:
            # If the answer is not provided, prompt the LLM
            print(label.text)   
            print('Getting the question')
            try:
                question = questions[i]
            except:
                print('Question not found so using label.text')
                question = label.text

            if find_substring_in_text(label.text, 'City'):
                try:
                    scroll_to_element_and_click(element=next_button, driver=driver)
                    print('Skipped City Button')
                except:
                    print(f"City Button not found.")
                    continue
                # return answers
            answer = get_llm_response(question)
            try:
                del(questions[i])
            except:
                pass
            
            # answer = input(f"Enter answer for '{label.text}': ")
            field.send_keys(answer)
            answers[label.text] = answer  # Store the answer for future use
    handle_checkbox()

# Handle select options
    for i, select in enumerate(select_options):
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
            # question = questions[i]
            choice = input(f"Choose an option (1-{len(options)}): ")
            selected_option = options[int(choice) - 1]
            select_element = Select(select)
            select_element.select_by_visible_text(selected_option)
            answers[label.text] = selected_option  # Store the answer for future use
    return answers
def parse_answer(string_with_json):
    

    # Find the JSON string within the larger string
    start_index = string_with_json.find('{')
    end_index = string_with_json.rfind('}') + 1
    json_string = string_with_json[start_index:end_index]

    # Parse the JSON string
    parsed_json = json.loads(json_string)

    print(parsed_json)
    return parsed_json

def get_all_error_messages():
    # Wait for the error messages to be visible
    wait = WebDriverWait(driver, 10)
    error_messages = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.artdeco-inline-feedback__message')))

    # Extract the text from each error message
    error_texts = []
    for error_message in error_messages:
        # Use JavaScript to get the inner HTML of the element
        # inner_html = error_message.find_element(By.CSS_SELECTOR, '.artdeco-inline-feedback__message').text

        inner_html = driver.execute_script("return arguments[0].innerHTML;", error_message)
        print('inner html', inner_html)
        text = inner_html.replace('<!---->', '').replace('\n', '').strip()
        print('error', text)
        error_texts.append(text)
    # Wait for the error messages to be visible
    wait = WebDriverWait(driver, 10)
    input_fields = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.artdeco-text-input--input')))
    questions = []
    for input_field in input_fields:
        # Find the label associated with the input field
        label_element = driver.find_element(By.CSS_SELECTOR, f'label[for="{input_field.get_attribute("id")}"]')
        question_text = label_element.text
        questions.append(question_text)
    both = []
    for error, question in zip(error_texts, questions):
        both.append(question + ' ' + error)
    return both


def check_for_error_messages():
    
    error_messages = driver.find_elements(By.CSS_SELECTOR, '.artdeco-inline-feedback__message')
    return any(error_messages)

# Function to write a question to a CSV file
def write_question_to_csv(question):
    with open('questions.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header if the file is empty
        if file.tell() == 0:
            writer.writerow(['Question'])
        # Write the question to the CSV file
        writer.writerow([question])

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

def find_substring_in_text(text, substring):
    # Convert the text and substring to lowercase for case-insensitive search
    text_lower = text.lower()
    substring_lower = substring.lower()
    
    # Split the text into words
    words = text_lower.split()
    
    # Iterate over the words
    for word in words:
        # Check if the substring is in the word
        if substring_lower in word:
            print(f"Found '{substring}' in the text.")
            return True  # Return True if the substring is found
    else:
        print(f"'{substring}' not found in the text.")
        return False  # Return False if the substring is not found

def handle_checkbox():
    # CSS selector for the checkbox label
    css_selector = "#checkbox-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3830758025-247286133020652785-multipleChoice > div > label"
    xpath='//*[@id="checkbox-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3805551361-6910476300330709486-multipleChoice"]/div/label'
    
    # Wait for the label to be present and get the text
    try:
        label = driver.find_element(By.XPATH, xpath)
    except:
        print("CheckBox Label not found.")
        return
    
    # Get the text of the label
    label_text = label.text
    
    # Find the associated checkbox input by the 'for' attribute of the label
    checkbox_id = label.get_attribute('for')
    checkbox = driver.find_element(By.ID, checkbox_id)
    
    # Prompt the user for input
    user_input = get_llm_response(label.text  + ' (yes/no): ')
    user_input = input(f"{label_text} (yes/no): ").lower()
    
    
    # Check or uncheck the checkbox based on user input
    if user_input == 'yes':
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)

    elif user_input == 'no':
        if checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")


def scroll_to_element_and_click(element, driver):
    try:
        # Scroll to the element
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        # Wait for the element to be clickable
        wait.until(EC.element_to_be_clickable(element))
        # Click the element
        element.click()
    except ElementClickInterceptedException:
        # If the click is intercepted, scroll to the element and try again
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        element.click()

def handle_stale_element2(locator):
    try:
        # Attempt to click the element
        wait.until(EC.element_to_be_clickable(locator)).click()
    except StaleElementReferenceException:
        # If the element is stale, relocate it and try again
        wait.until(EC.presence_of_element_located(locator))
        handle_stale_element2(locator)

# Main loop
try:
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
    # Navigate to the job section
    job_button_locator = (By.XPATH, '/html/body/div[5]/header/div/nav/ul/li[3]/a')
    handle_stale_element2(job_button_locator)
    # job = WebDriverWait(driver, 60).until(
    #     EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/header/div/nav/ul/li[3]/a'))).click()
    print('Clicked Job')
    # Click on the "Show more" button
    show_more_button_locator = (By.LINK_TEXT, 'Show all')
    handle_stale_element2(show_more_button_locator)
    # wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Show all'))).click()
    print('Clicked Show More')
    sleep(2)

    # Wait for the job list elements to be visible
    li_elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'li.job-card-container__apply-method.job-card-container__footer-item.inline-flex.align-items-center')))
    print(f'Found {len(li_elements)} Jobs')

    for li_element in li_elements:
        # Get the coordinates of the element
        x, y = li_element.location['x'], li_element.location['y']
        width, height = li_element.size['width'], li_element.size['height']

        # Click on the element
        driver.execute_script(f"window.scrollTo({x},{y});")
        li_element.click()
        sleep(5)
        
        click_easy_apply('Easy Apply')

        while True:
            dialog_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test-modal]')))
            # Check if the "Review" button is present
            sleep(1)
            print('Checking Review Button Before')
            review_button = check_button('Review')
            if review_button:
                review_button.click()
                print('Clicked Review Button')
                error = check_for_error_messages()
                print('empty field found:',error)
                if error:
                    questions = get_all_error_messages()
                    print('errors', questions)
                    print('empty field occured, so filling the form')
                    fill_out_form(answers={}, questions=questions)
                    scroll_to_element_and_click(element=review_button, driver=driver)
                    print('Clicked review button')
                    continue  # Exit the loop after clicking the button
                else:                
                    print('Clicked Review Button Successfully')
                    break  # Exit the loop after clicking the button
            print('Checking Next Button Before')
            next_button = check_button('Next')
            if next_button:
                print('Trying to click next button ')
                try:
                    scroll_to_element_and_click(driver=driver,element=next_button)
                except:
                    print('Unable to click next button')
                    pass
                print('Clicked Next Button')
                error = check_for_error_messages()
                print('empty field found:',error)
                if error:
                    questions = get_all_error_messages()
                    print('errors2', questions)
                    print('empty field occured, so filling the form')
                    fill_out_form(answers={}, questions=questions)
                    scroll_to_element_and_click(element=next_button, driver=driver)
                    print('filled the button now Clicked next button')
                    
                else:
                    print('Clicked Next Button Successfully')
            else:
                print('Exit button is not present so breaking ')
                break  # If "Next" button is not present, break the loop
        submit_btn = check_button('Submit application')
        if submit_btn:
            print('Trying to click submit button ')
            scroll_to_element_and_click(element=submit_btn, driver=driver)
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