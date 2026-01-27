from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.cardekho.com/newcars")
time.sleep(5)

all_cars = []
car_names = set()

price_tabs = driver.find_elements(By.CSS_SELECTOR, "ul.gsc-ta-clickWrap li")
price_tabs = [t for t in price_tabs if ("Lakh" in t.text or "Crore" in t.text)]

for i in range(len(price_tabs)):
    price_tabs = driver.find_elements(By.CSS_SELECTOR, "ul.gsc-ta-clickWrap li")
    price_tabs = [t for t in price_tabs if ("Lakh" in t.text or "Crore" in t.text)]
    tab = price_tabs[i]
    segment_name = tab.text.strip()
    print(f"\n🔹 Scraping segment: {segment_name}")

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tab)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(3)

        try:
            view_all_div = driver.find_element(By.CSS_SELECTOR, "div.BottomLinkViewAll:not(.hide)")
            view_all_link = view_all_div.find_element(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", view_all_link)
            driver.execute_script("arguments[0].click();", view_all_link)
            time.sleep(5)
        except Exception as e:
            print(f"No visible 'View All Cars' link for {segment_name}: {e}")
            continue

        divs = driver.find_elements(By.CSS_SELECTOR, ".gsc_col-sm-7.gsc_col-xs-8.gsc_col-md-8.listView.holder")

        for div in divs:
            try:
                h3 = div.find_element(By.TAG_NAME, "h3").text.strip()
                if h3 in car_names:
                    continue
                car_names.add(h3)

                price = div.find_element(By.CSS_SELECTOR, ".price span").text.strip()
                specs = div.find_elements(By.CSS_SELECTOR, ".dotlist span")

                car_specs = {"Segment": segment_name, "Name": h3, "Price": price}
                for s in specs:
                    label = s.get_attribute("title")
                    value = s.text.strip()
                    if label:
                        car_specs[label] = value
                    else:
                        car_specs["Seater"] = value

                all_cars.append(car_specs)
            except Exception as e:
                print(f"Error reading car: {e}")

    except Exception as e:
        print(f"Skipping segment {segment_name}: {e}")

    driver.get("https://www.cardekho.com/newcars")
    time.sleep(5)

df = pd.DataFrame(all_cars)
df.to_csv("data_files/all_segment_cars.csv", index=False, encoding='utf-8-sig')
print("\nData saved to data_files/all_segment_cars.csv")

input("Press Enter to close...")
driver.quit()
