from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

driver = webdriver.Chrome(options=options)
driver.get("https://drlogy.com/rajkot/doctor")

def get_doctor_details():
    doctor_data = []
    wait = WebDriverWait(driver, 10)
    
    # Wait for doctors to load and get all doctor elements
    doctor_elements = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-doc-details"))
    )
    
    print(f"Found {len(doctor_elements)} doctors")
    
    for doctor in doctor_elements:
        try:
            # Extract information using the correct class names
            name = doctor.find_element(By.CLASS_NAME, "pc-dr-nmmm").text
            specialties = doctor.find_elements(By.CLASS_NAME, "hp-p3")
            
            doctor_info = {
                "name": name.strip(),
                "qualification": specialties[0].text.strip(),
                "specialty": specialties[1].text.strip(),
                "experience": specialties[2].text.strip()
            }
            
            # Try to get clinic info
            try:
                clinic = doctor.find_element(By.CLASS_NAME, "hse-8").text
                doctor_info["clinic"] = clinic.strip()
            except:
                doctor_info["clinic"] = "Not specified"
            
            # Try to get location
            try:
                location = specialties[4].text
                doctor_info["location"] = location.strip()
            except:
                doctor_info["location"] = "Not specified"
            
            # Try to get fee
            try:
                fee = doctor.find_element(By.CLASS_NAME, "hp-576").text
                doctor_info["fee"] = fee.strip()
            except:
                doctor_info["fee"] = "Not specified"
                
            doctor_data.append(doctor_info)
            print(f"Successfully extracted data for doctor: {name}")
            
        except Exception as e:
            print(f"Error extracting doctor data: {str(e)}")
    
    return doctor_data

# Scroll down to load all doctors
def scroll_to_load_all():
    SCROLL_PAUSE_TIME = 3
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print("Scrolling to load more doctors...")

try:
    # Initial wait for page load
    time.sleep(5)
    
    # Scroll to load all doctors
    scroll_to_load_all()
    
    # Get doctor details
    doctors = get_doctor_details()
    
    # Save to JSON
    if doctors:
        with open('data/doctors.json', 'w', encoding='utf-8') as f:
            json.dump(doctors, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved details of {len(doctors)} doctors to data/doctors.json")
    else:
        print("No doctor data was collected")

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    driver.quit()