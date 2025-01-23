import platform
import sys
import subprocess
# Function to check if running in Google Colab
def is_colab():
    return "google.colab" in sys.modules
subprocess.run(["pip", "install", "selenium"], check=True)
subprocess.run(["apt-get", "update"], check=True)
subprocess.run(["apt-get", "install", "-y", "chromium-browser"], check=True)
subprocess.run(["apt-get", "install", "-y", "chromium"], check=True)
subprocess.run(["apt-get", "install", "-y", "chromium-driver"], check=True)
subprocess.run(["pip", "install", "webdriver-manager", "Pillow", "reportlab"], check=True)
subprocess.run(["pip", "install", "python-telegram-bot"], check=True)
from google.colab import output, files
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from IPython.display import Image, display
from telegram import Bot
from telegram.constants import ParseMode
import re
import sys
import json
import time
import base64
import platform
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from concurrent.futures import ThreadPoolExecutor, as_completed
def is_colab():
    return "google.colab" in sys.modules

if is_colab():
    output.clear()

def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--verbose")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    return driver

# Function to get URLs and indices from the main page
def get_url_and_index(driver):
    results = []
    index = 1
    while True:
        try:
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.ID, 'DataTables_Table_0'))
            )
            time.sleep(0.1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table', id='DataTables_Table_0')
            links = table.find_all('a', class_='text-teal-700')

            for link in links:
                href = link.get('href')
                if 'fundamentals' in href:
                    href = href.replace('fundamentals', 'stocks')
                    full_link = f"https://chartink.com{href}"
                    print(str(index) + "  " + full_link)
                    index += 1
                    results.append(full_link)

            next_button = driver.find_element(By.ID, 'DataTables_Table_0_next')
            if 'disabled' in next_button.get_attribute('class'):
                break
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            driver.execute_script("arguments[0].click();", next_button)
        except Exception as e:
            print("No more pages or an error occurred:", e)

    return results

async def send_pdf_with_markdown(chat_id = 2003227678, pdf_path = " ", MARKDOWN_TEXT = " "):
    BOT_TOKEN = "7576394776:AAEtmTKSP1eikoB5ZSw5l1BTvCuS1H-LElk"
    CHAT_ID = chat_id
    bot = Bot(token=BOT_TOKEN)
    
    # Send the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        await bot.send_document(
            chat_id=chat_id,
            document=pdf_file,
            caption=MARKDOWN_TEXT,
            parse_mode=ParseMode.MARKDOWN
        )

def get_image_from_link(driver, url, timeframe, s_range, form_data, retries=3):
    """
    Fetch an image from the given link after dynamically updating form inputs.

    :param driver: Selenium WebDriver instance
    :param url: URL to fetch
    :param timeframe: Timeframe value for selection
    :param s_range: Range value for selection
    :param form_data: Dictionary containing form inputs and their desired values
    :param retries: Number of retries for fetching the image
    :return: Tuple of company name and image data in base64, or (None, None) if failed
    """
    driver.get(url)

    try:        
        form_data_json = json.dumps(form_data)

        form_js_template = """
        const formData = {form_data};

        function fillForm(formId, data) {{
            const form = document.getElementById(formId);
            if (!form) {{
                console.error("Form not found");
                return;
            }}

            Object.keys(data).forEach(key => {{
                const field = form.querySelector(`[name="${{key}}"]`);
                const fieldData = data[key];

                if (field) {{
                    if (fieldData.type === "checkbox") {{
                        field.checked = fieldData.value;
                    }} else if (fieldData.type === "text") {{
                        field.value = fieldData.value;
                    }} else if (fieldData.type === "select") {{
                        field.value = fieldData.value;
                    }}
                }}
            }});
        }}
        fillForm("newone3", formData);
        """
        form_js = form_js_template.format(form_data=form_data_json)

        driver.execute_script(form_js)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ti"))
        )
        select_element = driver.find_element(By.ID, "ti")
        select_range_element = driver.find_element(By.ID, "d")

        # Extract the company name
        company_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[@style='margin: 0px;margin-left: 5px;font-size:20px']"))
        ).text
        
        # Update the timeframe dropdown
        timeframe_mapping = {
            "1 day": "1", "2 days": "2", "3 days": "3", "5 days": "5", "10 days": "10",
            "1 month": "22", "2 months": "44", "3 months": "66", "4 months": "91",
            "6 months": "121", "9 months": "198", "1 year": "252", "2 years": "504",
            "3 years": "756", "5 years": "1008", "8 years": "1764", "All Data": "5000"
        }
        select = Select(select_element)
        select.select_by_value(timeframe_mapping.get(timeframe, "5000"))

        # Update the range dropdown
        range_mapping = {
            "Daily": "d", "Weekly": "w", "Monthly": "m", "1 Minute": "1_minute",
            "2 Minute": "2_minute", "3 Minute": "3_minute", "5 Minute": "5_minute",
            "10 Minute": "10_minute", "15 Minute": "15_minute", "20 Minute": "20_minute",
            "25 Minute": "25_minute", "30 Minute": "30_minute", "45 Minute": "45_minute",
            "75 Minute": "75_minute", "125 Minute": "125_minute", "1 Hour": "60_minute",
            "2 Hour": "120_minute", "3 Hour": "180_minute", "4 Hour": "240_minute"
        }
        select_Range = Select(select_range_element)
        select_Range.select_by_value(range_mapping.get(s_range, "d"))


        # Click the 'Update' button
        update_button = driver.find_element(By.ID, "innerb")
        update_button.click()

        # Switch to the iframe containing the chart
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ChartImage"))
        )
        driver.switch_to.frame(iframe)

        # Retry mechanism to find and retrieve the chart image
        for attempt in range(retries):
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Extract the innerHTML
                body_html = driver.execute_script("return document.body.innerHTML;")
                if not body_html:
                    raise ValueError("innerHTML is empty or not found")
                soup = BeautifulSoup(body_html, "html.parser")
                img_tag = soup.find("img", {"id": "cross"})
                if img_tag:
                    img_data_base64 = img_tag["src"].split(",")[1]
                    return company_name, img_data_base64

            except Exception as e:
                if attempt > 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(5)

        print("Failed to find image after multiple attempts. Check the HTML structure or regex.")
        return None, None

    except Exception as e:
        print("Error:", e)
        return None, None


# Function to process each URL and generate PDF
def process_link(url, Period, Range, form_data):
    try:
        driver = web_driver()
        print(f"Processing URL: {url}")
        company_name, image_data = get_image_from_link(driver, url, Period, Range, form_data)
        driver.quit()
        if company_name and image_data:
            img_data = base64.b64decode(image_data)
            image = PILImage.open(BytesIO(img_data))
            return company_name, image
    except Exception as e:
        print(f"Error processing {url}: {e}")
    return None, None


# Main function
async def main(Screener_url, Period, Range, form_data):
    
    driver = web_driver()
    driver.get(Screener_url)
    results = get_url_and_index(driver)
    if is_colab():
      from google.colab import output, files
      output.clear()
    print("Total No of URLs is " + str(len(results)))
    driver.quit()

    base_path = "/content"
    if not is_colab():
        os.makedirs(base_path, exist_ok=True)
    print("Create Canvas")
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_pdf = f"/content/screener_images_{current_datetime}.pdf"
    c = canvas.Canvas(output_pdf, pagesize=A4)
    a4_width, a4_height = A4

    # Increase the number of threads based on the number of URLs
    num_threads = min(len(results), 10)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        print("Creating New Processing To Sub-Process....")
        futures = [executor.submit(process_link, url, Period, Range, form_data) for url in results]
        print("message: New Sub-Process Work successful")
        for future in as_completed(futures, timeout=300):
          try:
            company_name, image = future.result()
            if is_colab():
              from google.colab import output, files
              output.clear()
            if company_name and image:
                print(company_name)
                temp_image_path = f"/content/temp_image_{company_name}.png"
                image.save(temp_image_path)
                display(image)
                image_ratio = image.width / image.height
                a4_ratio = a4_width / a4_height
                if image_ratio > a4_ratio:
                    scaled_width = a4_width
                    scaled_height = a4_width / image_ratio
                else:
                    scaled_height = a4_height
                    scaled_width = a4_height * image_ratio

                page_height = scaled_height + 40
                c.setPageSize((a4_width, page_height))
                c.setFont("Helvetica", 12)
                c.drawCentredString(a4_width / 2, page_height - 30, company_name)
                x_offset = (a4_width - scaled_width) / 2
                y_offset = (page_height - scaled_height - 40) / 2
                c.drawImage(temp_image_path, x_offset, y_offset, width=scaled_width, height=scaled_height)
                c.showPage()
          except TimeoutError:
            print("A thread took too long and was skipped.")

    c.save()
    if is_colab():
        from google.colab import files, output
        output.clear()
        # Markdown message
        markdown_message = f"""
        **Date**: {current_datetime}
        """
        await send_pdf_with_markdown(2003227678, output_pdf, markdown_message)
        return output_pdf
          
    else:
        print(f"PDF saved at {output_pdf}")
