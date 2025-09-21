import requests
import json
import os
import pandas as pd  # Added for CSV export

API_URL = "https://phinnisi.pelindo.co.id:9021/api/executing/monitoring-operational"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
    "access-token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMStuWnUxTkR6MG1sdWNDTTNrdGdTK1QvYi84MisrRWdDdVZjL3ZkSTU4V1lQLzdGUnBNWTV4TGVLYXZNZnFlR040ZWM2cks2QVhBRTRsUE1WN2NCUCtRWCtNNzJhZHVKWjg4a3RiK1g4eTc2OE0zeGdNVVh2MWxqSEtlbmJKQitQcExwVURBRU13dEVsYithV0h5cFN2WFJoeXNSZVVYU2czbGliVTAwdS9sTnlveG5GelBoZitsZWhpU3Nic0ltRlZraU41V28rQmNDMWFMMkhEcW0zTVJzd255eVdsM3hYZUpOOE1hQkRMVys3SWpEeFBoUTdHemFxZlZERURvYVRTYXV1eEs1dk9YQ2p5TmFZZ0tmY3AxaytzVXAxV1FvTFQrbVJjZTY4T3h6cklkaTQ2dVE3WmNaVUc2RHNUMWVDWVBDWW9ZYm1XdmIzWnRtajFnU3JlUytLQ3FMMnFkbVc4QkQwWUFvelFaUHVnN0pMYkFPc3l5TE15UWlZR2wrVE5GQ3dsV3laQVVCTFpobUw5cGJScmk0dkRlNmpnOWZqS0szVDV2dEZnVGlGaWYrZGdSMmhZSndBenE3TVFCUEtNdm5TbnRKam1qQnRKRjJPZkxIMWlIWXFtVHBGRzBIbjlLem1GbjZzelFjK3AxQyt4emFaaHY4c2Vwa0J5RDAvTllqRmpveGRrQWZBS050eWp3ZDQ1Z2ZtN0VjRVJSWE9Sa1dWOUNVdnc4aVoxWDhLanFWd05KeGYrRTBzTlJQZW5nOXFqeU9iUW1rUGJCb1BPQURkQmV6d0JsV3VQbVI4MHg5UEhpNllLU01FQk1xUTRQZEw5N1Q1K09nMjNnN2ZnTXIzNzd0WU1xbEZpQm51clYwM1ZHSU9TS1Jyb01Rb1RtOWxiZzFrc1NzYWUzb0M3bUpsWUVJTDBpbFYySVd6TW8wSnZ3Mi9raFh1dy9ub3RvV2hQUEtDWWZIRjRnZmgrSmlmT0RLNzdiMFo3N2xXVW01bFV5MXNSbVdHSlIzdmtHd3NFZHdQZUc2NEVtVjRlNzF3dFBMUmQ5YU5UbXU2Z0V2alBaQ1dJdEsxRXZ3aVp4dWRVUmhnMlZMOWFXbFdydUJQYjAxWnBTQXhzdmU4YzBQWVdHUEZ6QmhLbWhYRi90QXh4b0M0NnAzbGpGZW5QbTdlcVJoYnhYZWhGb1VOTzA3Y1FnazFwWEYyRE9ualBFaSs2WFVHVHgySVNNZEFqZ09XNWxaVzlQWWw2UmdCN1JDUEptL3J1bWxvaS9lV1pjL2hXOWpoT1dXc2JFUldQUDMxdUJjdmdUdkNVOXR0NEs3T2J1VUVLT3BPSUJGNnowbVpQVE8rdW1JUHBkRGVubU1YdEpHWVRGYW1WUFByODg1U0kvczVGUG55bVFhNXdnZFozKzZsUXVrSFRiK2FYMkxDNHQxWVNGWGpYWGs1ZlJuV2lGUDhxd05kT0xHa3BqOWZEZXZzK2RvenFqODR4enFhTWJKNi9IU1d2dVZoaXBWNzVHOWhPYXpiTUloR0ZURzBKU3ZmbnAxMXFqN2x1aDl1YXJLYlJIV0s0RzBqK21ocHJ1Z1VXWEFrM0tSeTBPc2ZLakl3dUtDM28yWnVxSThVVHRnTnlDeUV2SHBzVUU0RDI2anhOaUdIMFFIdDF1MU5IbkdTeHdvelNvWVBrSzFJYjdHeGMwTVlwV2FWT0RwdXQrZkVZWFIvSzFSclVyODg3eGw4T1JqanA5KzNZTFlicm1wVnlzc2E3eGJSTjhzYUZ4bDhZbEV4TWVnME1FMGYrdE1VSERoVnNOZnBVckxZanI0Tkh3eVRrelNMajNjTlZvclVPNjZSSUNPUXBLRFQrZVZaMWJieERmOVFBd0JwU29mc0hXYisyWDVpS1BKcUhxOER2cngzOFpvNlB6SzA5RE1OK1c2blY3Q2xLQWxVdDZXdVhuaTdhN1NSREhWN2Q0T1BHTngwblFCNWZMdHExZlhvNXJtbTh6S0NTNkFLeDVkajFENHk2SHhHS2F6NFVudEF0bTQ4REdELzFFa3l2MnZMN0tYNmF4UXl0Mnc3eG8wMWpiSElJZGMvWTdYVzVqOGpzSXVoaVBQbnJiVVZIZGhNYzMxMSsvQ0tvL0p4K2pQWXhTSlRUeklZY2wvenBsaTN2ZUZQcERDeS9Hb1pCd2hkSHRVbnZZVnA4c3lsYlJ2bng5cXljcm9HeDVmTjloZy8yT0JKblFIRnRzRnl2Sk1nZzBqZVVCY043c2crQUY2d3JyQVhiZC9xWk1BRXkvd0pNNy8vYzVFanZ5d2x4bUY3YWprTFZFTFk5Y21LZG9SSTFZRXp1eHk1a3o1R2tadi9JYS84ZlpvYzJZN3JTdzl3OGt5NUl6MGVrSzRXV0hZYTFIYThSU1VBMGl5WEtJYWovWi82OFJncGhwZmY5V0JndzF3ZUM0OUtJWDRqWUZRZnJnb2Yrc0g5OFF2VExmZkVJNS9NbmV0R3lOMmlJYkhxT21vcVBHOFhsWHJJZUtwR284alAweDRVdTNsTElwY3I0TjV5MktDbjA5QS85ZXB1ZHlMQUdMQ2xaMmNIWG96MXEwWVl6emRaOXF0Q1ZjZ1ZYNWFKV0F3cWk3VFhVbisyK3lJaE5vSDlwMEFPWlFBNHJCbkM2WmZpelQ2QkdVVFZLTm56dUlabW1MVmJEMWpxVDdjWDVGTFhObDhDcEk0UXMvb0xVdDc5SFArb1hEN29STDlkbnFJbHZFZit5UTNDM0tuY2EvTndlV2dtTjFsbE5oRkxhMTlsUkd6dEREZjZQc1JWd3k3LzZPZm9EUWR6bnVvNC8yR1pvWjdSbWZzY1ZpQWZyeHNHdmVEc3pjOE1Qb3NVL09aRkoxSTVyeTJIWE40SkRkdkxJVlBES29RVnRqZkdnWnVIRXJoK0NqRThaUnVFQytqSytVQXFtbXppZWxYcXo3VWRVWVBTTzdZMFJJU2t6aC95T0t2UWpUbmJhbmlWK3kzbTc2UEhuUDdtRXNxaC81bWxPRWNsNUZNR1VsUGJHNHdlKzQ4ek9SYTY3c243Zy9PNVcwWnVvK2VPVHpKMGdTOTV4ckJVNEZDcVZjSDFQVUowOE1zOU9lOEp4SlhQMk5IWjFkU1AwNnFxdDVsTHd2dm5KNCtYNmxlVm1POFB2UitmZGd2NGFiYTE2eEY4RFVFNlFZT0N5SnorT3YxUVI5aitVN1czSWh5T1N0RXlCczc3Ri8rYW4rbFA1T053bThYdTFlZm94Y01QUmliVzc5M1p4RFBTODFxeW5PS0dWYmU1cXFEUjJOODZvbVFweVUxQjlWNGphblR3Z3ZEQT09.M-LYqMR7--S6Nje1F18AG-PFZ4SQPdzBNnPdVP1a9t4",
    "connection": "keep-alive",
    "host": "phinnisi.pelindo.co.id:9021",
    "origin": "https://phinnisi.pelindo.co.id",
    "referer": "https://phinnisi.pelindo.co.id/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
}

def scrape_data(page=1, record=100):
    params = {
        "page": page,
        "record": record,
        "data": ""
    }
    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"[!] Error during request: {e}")
        return None

def save_to_csv(data, filename="wasop.csv"):
    try:
        # Extract only the required columns
        df = pd.DataFrame(data["data"]["dataRec"])
        # Filter rows based on name_process_code
        filtered_df = df[df["name_process_code"].isin(["Request PPKB", "Realization"])]
        filtered_df = filtered_df[["no_pkk", "no_pkk_inaportnet", "name_process_code", "gt", "loa"]]
        # Coerce 'gt' to numeric and keep only rows where gt > 500
        filtered_df = filtered_df.assign(gt=pd.to_numeric(filtered_df["gt"], errors="coerce"))
        filtered_df = filtered_df[filtered_df["gt"] > 500]
        filtered_df.to_csv(filename, index=False)
        print(f"[i] Filtered data saved to {filename} (GT > 500 only)")
    except Exception as e:
        print(f"[!] Error saving to CSV: {e}")

def scrape_all_data(record=1000):
    """
    Scrape all data in batches of `record` size.
    """
    all_data = []
    page = 1
    while True:
        print(f"[i] Fetching page {page}...")
        data = scrape_data(page=page, record=record)
        if not data or "data" not in data or "dataRec" not in data["data"]:
            print("[!] No more data or error in response.")
            break
        batch = data["data"]["dataRec"]
        all_data.extend(batch)
        print(f"[i] Retrieved {len(batch)} records.")
        if len(batch) < record:  # Last page
            break
        page += 1
    print(f"[i] Total records fetched: {len(all_data)}")
    return all_data

if __name__ == "__main__":
    print("[i] Starting data scraping...")
    all_data = scrape_all_data()
    if all_data:
        save_to_csv({"data": {"dataRec": all_data}})
