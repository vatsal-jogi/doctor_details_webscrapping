from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
options.add_argument('--disable-notifications')
# Uncomment the following line to run Chrome in headless mode
# options.add_argument('--headless')

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)

def extract_doctor_urls():
    """
    Extracts all doctor profile URLs from the main doctors page.

    Returns:
        list: A list of doctor profile URLs.
    """
    doctor_urls = []
    main_url = "https://drlogy.com/rajkot/doctor"
    try:
        driver.get(main_url)
        wait = WebDriverWait(driver, 20)

        # Scroll to load all doctors
        scroll_to_load_all()

        # Wait for doctors to load
        doctor_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/rajkot/doctor/')]"))
        )

        print(f"Found {len(doctor_elements)} doctor profiles.")

        for doctor in doctor_elements:
            href = doctor.get_attribute('href')
            if href and href not in doctor_urls:
                doctor_urls.append(href)
                print(f"Added doctor URL: {href}")

    except TimeoutException:
        print("Timed out waiting for doctor profiles to load.")
    except Exception as e:
        print(f"An error occurred while extracting doctor URLs: {e}")

    return doctor_urls

def extract_memberships(driver, wait):
    """
    Extracts memberships from a doctor's profile page.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        wait (WebDriverWait): The WebDriverWait instance.

    Returns:
        list: A list of memberships.
    """
    memberships = []
    try:
        # Attempt 1: Memberships listed in an unordered list (<ul><li>)
        memberships_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Membership')]/following-sibling::ul/li"
        )
        memberships = [member.text.strip() for member in memberships_elements if member.text.strip()]
        if memberships:
            print(f"Found {len(memberships)} memberships using Attempt 1.")
            return memberships
    except Exception as e:
        print(f"Attempt 1 failed to locate memberships: {e}")

    try:
        # Attempt 2: Memberships listed in paragraphs (<p>)
        memberships_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Membership')]/following-sibling::p"
        )
        memberships = [member.text.strip() for member in memberships_elements if member.text.strip()]
        if memberships:
            print(f"Found {len(memberships)} memberships using Attempt 2.")
            return memberships
    except Exception as e:
        print(f"Attempt 2 failed to locate memberships: {e}")

    try:
        # Attempt 3: Memberships listed within divs with a specific class
        memberships_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Membership')]/following-sibling::div[contains(@class, 'membership-item')]/span"
        )
        memberships = [member.text.strip() for member in memberships_elements if member.text.strip()]
        if memberships:
            print(f"Found {len(memberships)} memberships using Attempt 3.")
            return memberships
    except Exception as e:
        print(f"Attempt 3 failed to locate memberships: {e}")

    # If none of the attempts found memberships
    print("No memberships found using any attempts.")
    return memberships

def extract_services(driver, services_url):
    """
    Extracts services from a doctor's services page.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        services_url (str): The URL of the doctor's services page.

    Returns:
        list: A list of services provided by the doctor.
    """
    services = []
    try:
        driver.get(services_url)
        print(f"Navigated to Services page: {services_url}")
        wait = WebDriverWait(driver, 20)

        # Wait for the 'Services' header to be present
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Services')]"))
        )
        time.sleep(2)  # Additional wait to ensure the page has fully loaded

        # Precisely target the first <ul> following the 'Services' <h2>
        services_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Services')]/following-sibling::ul[1]/li"
        )

        services = [service.text.strip() for service in services_elements if service.text.strip()]

        # Debugging statements
        print(f"Found {len(services)} services on {services_url}:")
        for idx, service in enumerate(services, start=1):
            print(f"{idx}. {service}")

    except TimeoutException:
        print(f"Timed out waiting for services to load on {services_url}.")
    except Exception as e:
        print(f"Error extracting services from {services_url}: {e}")

    return services

def extract_doctor_details(doctor_url):
    """
    Extracts detailed information from a doctor's profile page.

    Args:
        doctor_url (str): The URL of the doctor's profile page.

    Returns:
        dict: A dictionary containing the doctor's details.
    """
    doctor_info = {}
    try:
        driver.get(doctor_url)
        wait = WebDriverWait(driver, 20)

        # Wait for the doctor's name to be present
        name_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dr.')]"))
        )
        doctor_info['name'] = name_element.text.strip()
        print(f"Extracting details for {doctor_info['name']}.")

        # Extract Specialization
        specialties_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Specialization')]/following-sibling::ul/li"
        )
        doctor_info['specialization'] = [specialty.text.strip() for specialty in specialties_elements if specialty.text.strip()]
        print(f"Extracted {len(doctor_info['specialization'])} specializations.")

        # Extract Languages Spoken
        languages_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Languages spoken')]/following-sibling::ul/li"
        )
        doctor_info['languages_spoken'] = [language.text.strip() for language in languages_elements if language.text.strip()]
        print(f"Extracted {len(doctor_info['languages_spoken'])} languages spoken.")

        # Extract Education
        education_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Education')]/following-sibling::ul/li"
        )
        doctor_info['education'] = [edu.text.strip() for edu in education_elements if edu.text.strip()]
        print(f"Extracted {len(doctor_info['education'])} education details.")

        # Extract Registrations
        registrations_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Registrations')]/following-sibling::ul/li"
        )
        doctor_info['registrations'] = [reg.text.strip() for reg in registrations_elements if reg.text.strip()]
        print(f"Extracted {len(doctor_info['registrations'])} registrations.")

        # Extract Experience
        experience_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Experience')]/following-sibling::ul/li"
        )
        doctor_info['experience'] = [exp.text.strip() for exp in experience_elements if exp.text.strip()]
        print(f"Extracted {len(doctor_info['experience'])} experiences.")

        # Extract Memberships
        doctor_info['memberships'] = extract_memberships(driver, wait)
        print(f"Extracted {len(doctor_info['memberships'])} memberships.")

        # Extract Clinic Fees
        fees_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Clinic Fees')]/following-sibling::div"
        )
        doctor_info['clinic_fees'] = [fee.text.strip() for fee in fees_elements if fee.text.strip()]
        print(f"Extracted {len(doctor_info['clinic_fees'])} clinic fees.")

        # Extract Timing
        timing_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Timing')]/following-sibling::div"
        )
        doctor_info['timing'] = [time_elem.text.strip() for time_elem in timing_elements if time_elem.text.strip()]
        print(f"Extracted {len(doctor_info['timing'])} timings.")

        # Extract Services from the Services Page
        services_url = doctor_url.rstrip('/') + "/services"
        doctor_info['services'] = extract_services(services_url)
        print(f"Extracted {len(doctor_info['services'])} services.")

        print(f"Successfully extracted data for {doctor_info['name']}.")

    except TimeoutException:
        print(f"Timed out waiting for elements on {doctor_url}.")
    except NoSuchElementException:
        print(f"Necessary elements not found on {doctor_url}.")
    except Exception as e:
        print(f"Error extracting details from {doctor_url}: {e}")

    return doctor_info

def scroll_to_load_all():
    """
    Scrolls down the page to load all doctor profiles.
    """
    SCROLL_PAUSE_TIME = 3
    driver.execute_script("window.scrollTo(0, 0);")  # Scroll to top before starting
    time.sleep(2)
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print("Scrolling to load more doctors...")

def main():
    """
    Main function to extract details of all doctors and save them to a JSON file.
    """
    try:
        # Extract all doctor profile URLs
        doctor_urls = extract_doctor_urls()

        all_doctors_data = []

        for idx, url in enumerate(doctor_urls, start=1):
            print(f"Processing doctor {idx}/{len(doctor_urls)}: {url}")
            data = extract_doctor_details(url)
            if data:
                all_doctors_data.append(data)
            # Optional: Add delay to prevent overwhelming the server
            time.sleep(2)

        # Save to JSON
        if all_doctors_data:
            # Define the output JSON file path
            data_file = 'data/doctors_data.json'
            if os.path.isfile(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                # Create a dictionary for easy update based on doctor's name
                existing_data_dict = {doctor['name']: doctor for doctor in existing_data}

                # Update existing data with new data
                for doctor in all_doctors_data:
                    if doctor['name'] in existing_data_dict:
                        existing_data_dict[doctor['name']].update(doctor)
                    else:
                        existing_data_dict[doctor['name']] = doctor

                # Convert back to list
                combined_data = list(existing_data_dict.values())

                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(combined_data, f, indent=4, ensure_ascii=False)
                print(f"Successfully updated details of {len(combined_data)} doctors in {data_file}.")
            else:
                # If the file does not exist, create it
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(all_doctors_data, f, indent=4, ensure_ascii=False)
                print(f"Successfully saved details of {len(all_doctors_data)} doctors to {data_file}.")
        else:
            print("No doctor data was collected.")

    except Exception as e:
        print(f"An error occurred in the main execution: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()