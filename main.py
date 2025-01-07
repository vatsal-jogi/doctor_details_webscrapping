import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
options.add_argument('--disable-notifications')

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)

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

        # Extract Specialization
        specialties_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Specialization')]/following-sibling::ul/li"
        )
        doctor_info['specialization'] = [specialty.text.strip() for specialty in specialties_elements if specialty.text.strip()]

        # Extract Languages Spoken
        languages_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Languages spoken')]/following-sibling::ul/li"
        )
        doctor_info['languages_spoken'] = [language.text.strip() for language in languages_elements if language.text.strip()]

        # Extract Education
        education_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Education')]/following-sibling::ul/li"
        )
        doctor_info['education'] = [edu.text.strip() for edu in education_elements if edu.text.strip()]

        # Extract Registrations
        registrations_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Registrations')]/following-sibling::ul/li"
        )
        doctor_info['registrations'] = [reg.text.strip() for reg in registrations_elements if reg.text.strip()]

        # Extract Experience
        experience_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Experience')]/following-sibling::ul/li"
        )
        doctor_info['experience'] = [exp.text.strip() for exp in experience_elements if exp.text.strip()]

        # Extract Memberships
        memberships_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Memberships')]/following-sibling::ul/li"
        )
        doctor_info['memberships'] = [member.text.strip() for member in memberships_elements if member.text.strip()]

        # Extract Clinic Fees
        fees_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Clinic Fees')]/following-sibling::div"
        )
        doctor_info['clinic_fees'] = [fee.text.strip() for fee in fees_elements if fee.text.strip()]

        # Extract Timing
        timing_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Timing')]/following-sibling::div"
        )
        doctor_info['timing'] = [time_elem.text.strip() for time_elem in timing_elements if time_elem.text.strip()]

        # Extract Services from the same page
        doctor_info['services'] = extract_services(doctor_url)

        print(f"Successfully extracted data for {doctor_info['name']}.")

    except Exception as e:
        print(f"Error extracting details from {doctor_url}: {e}")

    return doctor_info

def extract_services(doctor_url):
    """
    Extracts services from the doctor's profile page.

    Args:
        doctor_url (str): The URL of the doctor's profile page.

    Returns:
        list: A list of services provided by the doctor with details.
    """
    services = []
    try:
        driver.get(doctor_url)
        wait = WebDriverWait(driver, 20)

        # Wait for the 'Services' header to be present
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Services')]"))
        )
        time.sleep(2)  # Additional wait to ensure the page has fully loaded

        # Extract service details
        services_elements = driver.find_elements(
            By.XPATH,
            "//h2[contains(text(), 'Services')]/following-sibling::ul[1]/li"
        )

        for service in services_elements:
            service_name = service.text.strip()
            service_details = {
                'name': service_name,
                'description': "Description not available",  # Placeholder
                'fee': "Fee not available"  # Placeholder
            }
            services.append(service_details)

        print(f"Extracted services: {services}")  # Debugging output

    except Exception as e:
        print(f"Error extracting services from {doctor_url}: {e}")

    return services

def main():
    doctor_url = "https://drlogy.com/rajkot/doctor/dr-neel-gohil"
    doctor_data = extract_doctor_details(doctor_url)

    # Save to JSON
    with open('doctor_details.json', 'w', encoding='utf-8') as f:
        json.dump(doctor_data, f, indent=4, ensure_ascii=False)
    print(f"Doctor details saved to doctor_details.json.")

    driver.quit()

if __name__ == "__main__":
    main()
