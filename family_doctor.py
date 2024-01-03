import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime


def save_to_csv(data):
    # Create the 'data' folder if it doesn't exist
    data_folder = './data'
    os.makedirs(data_folder, exist_ok=True)

    # Generate a timestamp for the CSV file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the CSV file path
    csv_file_path = os.path.join(data_folder, f"Oakville_{timestamp}.csv")

    # Write data to the CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Name', 'Address', 'Phone', 'Physician'])
        # Write data rows
        writer.writerows(data)

    print(f"Data saved to {csv_file_path}")


def scrape_oakville_physicians():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Uncomment this line if you don't want the browser to be visible

    # Use webdriver_manager to automatically download and install ChromeDriver
    ChromeDriverManager().install()

    try:
        with webdriver.Chrome(options=chrome_options) as driver:
            url = "https://www.halton.ca/For-Residents/Public-Health/Halton-Physicians-Accepting-New-Patients"
            driver.get(url)

            print("Waiting for the Oakville tab to be clickable...")
            # Change to wait for the presence of h2 with text 'Oakville'
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//h2[text()="Oakville"]')))

            print("Extracting data from the list items...")
            data = []
            items = driver.find_elements(By.XPATH, '//h2[text()="Oakville"]/following-sibling::ul/li')
            for item in items:
                name_element = item.find_element(By.XPATH, './/strong')
                name = name_element.get_attribute('innerText').strip() if name_element else ""
                print(f"Name: {name}")

                address_element = item.find_element(By.XPATH, './/ul/li[contains(text(), "Address")]/a')
                address = address_element.get_attribute('innerText').replace('(GoogleMaps link)',
                                                                             '').strip() if address_element else ""
                print(f"Address: {address}")

                phone_element = item.find_element(By.XPATH, './/ul/li[contains(text(), "Phone")]/a')
                phone = phone_element.get_attribute('innerText').strip() if phone_element else ""
                print(f"Phone: {phone}")

                # Extract physician data
                physician_list = item.find_elements(By.XPATH, './/ul/li[contains(text(), "Physician")]/ul/li/strong')
                if not physician_list:
                    # Check if there's only one physician directly under the "Physician" list
                    physician_list = item.find_elements(By.XPATH, './/ul/li[contains(text(), "Physician")]/ul//strong')

                physicians = ', '.join([physician.get_attribute('innerText').strip() for physician in physician_list])

                print(f"Physicians: {physicians}")

                data.append([name, address, phone, physicians])

            # Save the data to a CSV file
            save_to_csv(data)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    scrape_oakville_physicians()
