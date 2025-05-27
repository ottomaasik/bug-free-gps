import requests
from bs4 import BeautifulSoup
import pandas as pd


def merepinnal(x=3, y=16, save=False):

    # URL of the page with hourly observation data
    url = "https://www.ilmateenistus.ee/ilm/ilmavaatlused/vaatlusandmed/tunniandmed/"

    # Set headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Send request
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  # Ensure proper encoding

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all tables (each station is in its own table)
    tables = soup.find_all("table")

    # Extract all tables
    all_dfs = []
    for table in tables:
        # Extract station name from caption or nearby h2 tag
        station_name = table.find_previous("h2").text.strip()

        # Read table into pandas DataFrame
        df = pd.read_html(str(table), decimal=",", thousands=".")[0]
        df["Station"] = station_name
        all_dfs.append(df)

    # Combine all station data
    final_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Sealevel pressure ({final_df.iat[y,0]}): {final_df.iat[y,x]} hPa")

    if save:

        # Save to CSV
        final_df.to_csv("ilmateenistus_hourly_data.csv", index=False, encoding="utf-8-sig")
        print("Data saved to ilmatenistus_hourly_data.csv")

    return final_df.iat[y,x]
