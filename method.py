from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from IPython.display import Image, display
from google.colab import output
import re
import base64
import time
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from google.colab import files
output.clear()

def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--verbose")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    # options.add_argument("--window-size=1920, 1200")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    return driver

def get_url_and_index(driver):
    results = []  # List to store results (index and URL)
    while True:
        try:
            # Wait for the table to be present
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, 'DataTables_Table_0'))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table', id='DataTables_Table_0')
            links = table.find_all('a', class_='text-teal-700')

            for link in links:
                href = link.get('href')
                if 'fundamentals' in href:
                    href = href.replace('fundamentals', 'stocks')
                    full_link = f"https://chartink.com{href}"
                    results.append(full_link)  # Store the index and URL

            # Try to click the next page button
            next_button = driver.find_element(By.ID, 'DataTables_Table_0_next')
            if 'disabled' in next_button.get_attribute('class'):
                break
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            driver.execute_script("arguments[0].click();", next_button)

        except Exception as e:
            print("No more pages or an error occurred:", e)
            break

    driver.quit()
    return results  # Return the list of results


def get_image_from_link(url, timeframe, s_range, retries=3):
    driver = web_driver()
    driver.get(url)

    try:
        # Capture HTML before switching to iframe
        page_html_before_iframe = driver.execute_script("return document.documentElement.outerHTML;")

        # Wait for the <select> element and select the value for "1 year"
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ti"))
        )
        select_Range_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "d"))
        )

        h3_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h3[@style='margin: 0px;margin-left: 5px;font-size:20px']"))
        )
        
        # Extract the text of the <h3> element
        company_name = h3_element.text
        print(f"Company Name: {company_name}")

        timeframe_mapping = {
        "1 day": "1",
        "2 days": "2",
        "3 days": "3",
        "5 days": "5",
        "10 days": "10",
        "1 month": "22",
        "2 months": "44",
        "3 months": "66",
        "4 months": "91",
        "6 months": "121",
        "9 months": "198",
        "1 year": "252",
        "2 years": "504",
        "3 years": "756",
        "5 years": "1008",
        "8 years": "1764",
        "All Data": "5000"
        }
        select = Select(select_element)
        if timeframe in timeframe_mapping:
            select.select_by_value(timeframe_mapping[timeframe])
        else:
            select.select_by_value(timeframe_mapping["All Data"])

        range_mapping = {
        "Daily": "d",
        "Weekly": "w",
        "Monthly": "m",
        "1 Minute": "1_minute",
        "2 Minute": "2_minute",
        "3 Minute": "3_minute",
        "5 Minute": "5_minute",
        "10 Minute": "10_minute",
        "15 Minute": "15_minute",
        "20 Minute": "20_minute",
        "25 Minute": "25_minute",
        "30 Minute": "30_minute",
        "45 Minute": "45_minute",
        "75 Minute": "75_minute",
        "125 Minute": "125_minute",
        "1 Hour": "60_minute",
        "2 Hour": "120_minute",
        "3 Hour": "180_minute",
        "4 Hour": "240_minute"
        }

        select_Range = Select(select_Range_element)
        if s_range in range_mapping:
            select_Range.select_by_value(range_mapping[s_range])
        else:
            select_Range.select_by_value("d")

        # Click the update button
        update_button = driver.find_element(By.ID, "innerb")
        update_button.click()

        # Wait for the iframe containing the chart to load
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ChartImage"))
        )
        driver.switch_to.frame(iframe)

        for attempt in range(retries):
            try:
                # Capture the HTML inside the iframe
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                body_html = driver.execute_script("return document.body.innerHTML;")

                # Check if body_html is empty or None
                if not body_html:
                    raise ValueError("innerHTML is empty or not found")

                # Regex to extract the base64 image data
                img_match = re.search(r'<img[^>]*id="cross"[^>]*src="data:\s*image/[^;]+;base64,([^"]+)"', body_html)

                if img_match:
                    # Extract the base64 encoded image data
                    img_data_base64 = img_match.group(1)
                    return company_name, img_data_base64  # Returning the base64 blob code as string

            except Exception as e:
                if attempt > 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(5)  # Wait before retrying

        print("Failed to find image after multiple attempts. Check the HTML structure or regex.")
        return None

    except Exception as e:
      if attempt > 1:
        print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
        time.sleep(5)
        print("Error:", e)

    finally:
        driver.quit()
def main(Screener_url, Period, Range):
    driver = web_driver()
    driver.get(Screener_url)
    results = get_url_and_index(driver)
    output_pdf = "/content/screener_images.pdf"
    c = canvas.Canvas(output_pdf, pagesize=A4)
    a4_width, a4_height = A4
    size = len(results)
    print(f"Total number of graphs: {size}")
    for i, url in enumerate(results):
      company_name, img_data_base64 = get_image_from_link(url, Period, Range)
      img_data = base64.b64decode(img_data_base64)
      image = Image.open(BytesIO(img_data))
      temp_image_path = f"/content/temp_image{i}.png"
      image.save(temp_image_path)
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
      c.setFont("Helvetica", 12)  # Set font and size for the heading
      c.drawCentredString(a4_width / 2, page_height - 30, company_name)
      x_offset = (a4_width - scaled_width) / 2
      y_offset = (page_height - scaled_height - 40) / 2  # Adjust y_offset to fit image below the heading
      c.drawImage(temp_image_path, x_offset, y_offset, width=scaled_width, height=scaled_height)
      c.showPage() 
      #   with open("image.png", "wb") as img_file:
      #     img_file.write(img_data)  

      # display(Image(filename="image.png"))
    c.save()
    files.download(output_pdf)
    driver.quit()
