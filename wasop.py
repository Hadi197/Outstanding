import requests
import json
import os
import pandas as pd
import asyncio
import aiohttp
import time

API_URL = "https://phinnisi.pelindo.co.id:9018/api/executing/monitoring-operational"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
    "access-token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMStuWnUxTkR6MG1sdWNDTTNrdGdTK1QvYi84MisrRWdDdVZjL3ZkSTU4V1lQLzdGUnBNWTV4TGVLYXZNZnFlR040ZWM2cks2QVhBRTRsUE1WN2NCUCtRWCtNNzJhZHVKWjg4a3RiK1g4eTc2OE0zeGdNVVh2MWxqSEtlbmJKQitQcExwVURBRU13dEVsYithV0h5cFN2WFJoeXNSZVVYU2czbGliVTAwdS9sTnlveG5GelBoZitsZWhpU3Nic0ltRlZraU41V28rQmNDMWFMMkhEcW0zTVJzd255eVdsM3hYZUpOOE1hQkRMVys3SWpEeFBoUTdHemFxZlZERURvYVRTYXV1eEs1dk9YQ2p5TmFZZ0tmY3AxaytzVXAxV1FvTFQrbVJjZTY4T3h6cklkaTQ2dVE3WmNaVUc2RHNUMWVDWVBDWW9ZYm1XdmIzWnRtajFnU3JlUytLQ3FMMnFkbVc4QkQwWUFvelFaUHVnN0pMYkFPc3l5TE15UWlZR2wrVE5GQ3dsV3laQVVCTFpobUw5cGJScmk0dkRlNmpnOWZqS0szVDV2dEZnVGlGaWYrZGdSMmhZSndBenE3TVFCUEtNdm5TbnRKam1qQnRKRjJPZkxIMWlIWXFtVHBGRzBIbjlLem1GbjZzelFjK3AxQyt4emFaaHY4c2Vwa0J5RDAvTllqRmpveGRrQWZBS050eWp3ZDQ1Z2ZtN0VjRVJSWE9Sa1dWOUNVdnc4aVoxWDhLanFWd05KeGYrRTBzTlJQZW5nOXFqeU9iUW1rUGJCb1BPQURkQmV6d0JsV3VQbVI4MHg5UEhpNllLU01FQk1xUTRQZEw5N1Q1K09nMjNnN2ZnTXIzNzd0WU1xbEZpQm51clYwM1ZHSU9TS1Jyb01Rb1RtOWxiZzFrc1NzYWUzb0M3bUpsWUVJTDBpbFYySVd6TW8wSnZ3Mi9raFh1dy9ub3RvV2hQUEtDWWZIRjRnZmgrSmlmT0RLNzdiMFo3N2xXVW01bFV5MXNSbVdHSlIzdmtHd3NFZHdQZUc2NEVtVjRlNzF3dFBMUmQ5YU5UbXU2Z0V2alBaQ1dJdEsxRXZ3aVp4dWRVUmhnMlZMOWFXbFdydUJQYjAxWnBTQXhzdmU4YzBQWVdHUEZ6QmhLbWhYRi90QXh4b0M0NnAzbGpGZW5QbTdlcVJoYnhYZWhGb1VOTzA3Y1FnazFwWEYyRE9ualBFaSs2WFVHVHgySVNNZEFqZ09XNWxaVzlQWWw2UmdCN1JDUEptL3J1bWxvaS9lV1pjL2hXOWpoT1dXc2JFUldQUDMxdUJjdmdUdkNVOXR0NEs3T2J1VUVLT3BPSUJGNnowbVpQVE8rdW1JUHBkRGVubU1YdEpHWVRGYW1WUFByODg1U0kvczVGUG55bVFhNXdnZFozKzZsUXVrSFRiK2FYMkxDNHQxWVNGWGpYWGs1ZlJuV2lGUDhxd05kT0xHa3BqOWZEZXZzK2RvenFqODR4enFhTWJKNi9IU1d2dVZoaXBWNzVHOWhPYXpiTUloR0ZURzBKU3ZmbnAxMXFqN2x1aDl1YXJLYlJIV0s0RzBqK21ocHJ1Z1VXWEFrM0tSeTBPc2ZLakl3dUtDM28yWnVxSThVVHRnTnlDeUV2SHBzVUU0RDI2anhOaUdIMFFIdDF1MU5IbkdTeHdvelNvWVBrSzFJYjdHeGMwTVlwV2FWT0RwdXQrZkVZWFIvSzFSclVyODg3eGw4T1JqanA5KzNZTFlicm1wVnlzc2E3eGJSTjhzYUZ4bDhZbEV4TWVnME1FMGYrdE1VSERoVnNOZnBVckxZanI0Tkh3eVRrelNMajNjTlZvclVPNjZSSUNPUXBLRFQrZVZaMWJieERmOVFBd0JwU29mc0hXYisyWDVpS1BKcUhxOER2cngzOFpvNlB6SzA5RE1OK1c2blY3Q2xLQWxVdDZXdVhuaTdhN1NSREhWN2Q0T1BHTngwblFCNWZMdHExZlhvNXJtbTh6S0NTNkFLeDVkajFENHk2SHhHS2F6NFVudEF0bTQ4REdELzFFa3l2MnZMN0tYNmF4UXl0Mnc3eG8wMWpiSElJZGMvWTdYVzVqOGpzSXVoaVBQbnJiVVZIZGhNYzMxMSsvQ0tvL0p4K2pQWXhTSlRUeklZY2wvenBsaTN2ZUZQcERDeS9Hb1pCd2hkSHRVbnZZVnA4c3lsYlJ2bng5cXljcm9HeDVmTjloZy8yT0JKblFIRnRzRnl2Sk1nZzBqZVVCY043c2crQUY2d3JyQVhiZC9xWk1BRXkvd0pNNy8vYzVFanZ5d2x4bUY3YWprTFZFTFk5Y21LZG9SSTFZRXp1eHk1a3o1R2tadi9JYS84ZlpvYzJZN3JTdzl3OGt5NUl6MGVrSzRXV0hZYTFIYThSU1VBMGl5WEtJYWovWi82OFJncGhwZmY5V0JndzF3ZUM0OUtJWDRqWUZRZnJnb2Yrc0g5OFF2VExmZkVJNS9NbmV0R3lOMmlJYkhxT21vcVBHOFhsWHJJZUtwR284alAweDRVdTNsTElwY3I0TjV5MktDbjA5QS85ZXB1ZHlMQUdMQ2xaMmNIWG96MXEwWVl6emRaOXF0Q1ZjZ1ZYNWFKV0F3cWk3VFhVbisyK3lJaE5vSDlwMEFPWlFBNHJCbkM2WmZpelQ2QkdVVFZLTm56dUlabW1MVmJEMWpxVDdjWDVGTFhObDhDcEk0UXMvb0xVdDc5SFArb1hEN29STDlkbnFJbHZFZit5UTNDM0tuY2EvTndlV2dtTjFsbE5oRkxhMTlsUkd6dEREZjZQc1JWd3k3LzZPZm9EUWR6bnVvNC8yR1pvWjdSbWZzY1ZpQWZyeHNHdmVEc3pjOE1Qb3NVL09aRkoxSTVyeTJIWE40SkRkdkxJVlBES29RVnRqZkdnWnVIRXJoK0NqRThaUnVFQytqSytVQXFtbXppZWxYcXo3VWRVWVBTTzdZMFJJU2t6aC95T0t2UWpUbmJhbmlWK3kzbTc2UEhuUDdtRXNxaC81bWxPRWNsNUZNR1VsUGJHNHdlKzQ4ek9SYTY3c243Zy9PNVcwWnVvK2VPVHpKMGdTOTV4ckJVNEZDcVZjSDFQVUowOE1zOU9lOEp4SlhQMk5IWjFkU1AwNnFxdDVsTHd2dm5KNCtYNmxlVm1POFB2UitmZGd2NGFiYTE2eEY4RFVFNlFZT0N5SnorT3YxUVI5aitVN1czSWh5T1N0RXlCczc3Ri8rYW4rbFA1T053bThYdTFlZm94Y01QUmliVzc5M1p4RFBTODFxeW5PS0dWYmU1cXFEUjJOODZvbVFweVUxQjlWNGphblR3Z3ZEQT09.M-LYqMR7--S6Nje1F18AG-PFZ4SQPdzBNnPdVP1a9t4",
    "access_token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMStuWnUxTkR6MG1sdWNDTTNrdGdTK1QvYi84MisrRWdDdVZjL3ZkSTU4V1lQLzdGUnBNWTV4TGVLYXZNZnFlR040ZWM2cks2QVhBRTRsUE1WN2NCUCtRWCtNNzJhZHVKWjg4a3RiK1g4eTc2OE0zeGdNVVh2MWxqSEtlbmJKQitQcExwVURBRU13dEVsYithV0h5cFN2WFJoeXNSZVVYU2czbGliVTAwdS9zTnlveG5GelBoZitsZWhpU3Nic0ltRlZraU41V28rQmNDMWFMMkhEcW0zTVJzd255eVdsM3hYZUpOOE1hQkRMVys3SWpEeFBoUTdHemFxZlZERURvYVRTYXV1eEs1dk9YQ2p5TmFZZ0tmY3AxaytzVXAxV1FvTFQrbVJjZTY4T3h6cklkaTQ2dVE3WmNaVUc2RHNUMWVDWVBDWW9ZYm1XdmIzWnRtajFnU3JlUytLQ3FMMnFkbVc4QkQwWUFvelFaUHVnN0pMYkFPc3l5TE15UWlZR2wrVE5GQ3dsV3laQVVCTFpobUw5cGJScmk0dkRlNmpnOWZqS0szVDV2dEZnVGlGaWYrZGdSMmhZSndBenE3TVFCUEtNdm5TbnRKam1qQnRKRjJPZkxIMWlIWXFtVHBGRzBIbjlLem1GbjZzelFjK3AxQyt4emFaaHY4c2Vwa0J5RDAvTllqRmpveGRrQWZBS050eWp3ZDQ1Z2ZtN0VjRVJSWE9Sa1dWOUNVdnc4aVoxWDhLanFWd05KeGYrRTBzTlJQZW5nOXFqeU9iUW1rUGJCb1BPQURkQmV6d0JsV3VQbVI4MHg5UEhpNllLU01FQk1xUTRQZEw5N1Q1K09nMjNnN2ZnTXIzNzd0WU1xbEZpQm51clYwM1ZHSU9TS1Jyb01Rb1RtOWxiZzFrc1NzYWUzb0M3bUpsWUVJTDBpbFYySVd6TW8wSnZ3Mi9raFh1dy9ub3RvV2hQUEtDWWZIRjRnZmgrSmlmT0RLNzdiMFo3N2xXVW01bFV5MXNSbVdHSlIzdmtHd3NFZHdQZUc2NEVtVjRlNzF3dFBMUmQ5YU5UbXU2Z0V2alBaQ1dJdEsxRXZ3aVp4dWRVUmhnMlZMOWFXbFdydUJQYjAxWnBTQXhzdmU4YzBQWVdHUEZ6QmhLbWhYRi90QXh4b0M0NnAzbGpGZW5QbTdlcVJoYnhYZWhGb1VOTzA3Y1FnazFwWEYyRE9ualBFaSs2WFVHVHgySVNNZEFqZ09XNWxaVzlQWWw2UmdCN1JDUEptL3J1bWxvaS9lV1pjL2hXOWpoT1dXc2JFUldQUDMxdUJjdmdUdkNVOXR0NEs3T2J1VUVLT3BPSUJGNnowbVpQVE8rdW1JUHBkRGVubU1YdEpHWVRGYW1WUFByODg1U0kvczVGUG55bVFhNXdnZFozKzZsUXVrSFRiK2FYMkxDNHQxWVNGWGpYWGs1ZlJuV2lGUDhxd05kT0xHa3BqOWZEZXZzK2RvenFqODR4enFhTWJKNi9IU1d2dVZoaXBWNzVHOWhPYXpiTUloR0ZURzBKU3ZmbnAxMXFqN2x1aDl1YXJLYlJIV0s0RzBqK21ocHJ1Z1VXWEFrM0tSeTBPc2ZLakl3dUtDM28yWnVxSThVVHRnTnlDeUV2SHBzVUU0RDI2anhOaUdIMFFIdDF1MU5IbkdTeHdvelNvWVBrSzFJYjdHeGMwTVlwV2FWT0RwdXQrZkVZWFIvSzFSclVyODg3eGw4T1JqanA5KzNZTFlicm1wVnlzc2E3eGJSTjhzYUZ4bDhZbEV4TWVnME1FMGYrdE1VSERoVnNOZnBVckxZanI0Tkh3eVRrelNMajNjTlZvclVPNjZSSUNPUXBLRFQrZVZaMWJieERmOVFBd0JwU29mc0hXYisyWDVpS1BKcUhxOER2cngzOFpvNlB6SzA5RE1OK1c2blY3Q2xLQWxVdDZXdVhuaTdhN1NSREhWN2Q0T1BHTngwblFCNWZMdHExZlhvNXJtbTh6S0NTNkFLeDVkajFENHk2SHhHS2F6NFVudEF0bTQ4REdELzFFa3l2MnZMN0tYNmF4UXl0Mnc3eG8wMWpiSElJZGMvWTdYVzVqOGpzSXVoaVBQbnJiVVZIZGhNYzMxMSsvQ0tvL0p4K2pQWXhTSlRUeklZY2wvenBsaTN2ZUZQcERDeS9Hb1pCd2hkSHRVbnZZVnA4c3lsYlJ2bng5cXljcm9HeDVmTjloZy8yT0JKblFIRnRzRnl2Sk1nZzBqZVVCY043c2crQUY2d3JyQVhiZC9xWk1BRXkvd0pNNy8vYzVFanZ5d2x4bUY3YWprTFZFTFk5Y21LZG9SSTFZRXp1eHk1a3o1R2tadi9JYS84ZlpvYzJZN3JTdzl3OGt5NUl6MGVrSzRXV0hZYTFIYThSU1VBMGl5WEtJYWovWi82OFJncGhwZmY5V0JndzF3ZUM0OUtJWDRqWUZRZnJnb2Yrc0g5OFF2VExmZkVJNS9NbmV0R3lOMmlJYkhxT21vcVBHOFhsWHJJZUtwR284alAweDRVdTNsTElwY3I0TjV5MktDbjA5QS85ZXB1ZHlMQUdMQ2xaMmNIWG96MXEwWVl6emRaOXF0Q1ZjZ1ZYNWFKV0F3cWk3VFhVbisyK3lJaE5vSDlwMEFPWlFBNHJCbkM2WmZpelQ2QkdVVFZLTm56dUlabW1MVmJEMWpxVDdjWDVGTFhObDhDcEk0UXMvb0xVdDc5SFArb1hEN29STDlkbnFJbHZFZit5UTNDM0tuY2EvTndlV2dtTjFsbE5oRkxhMTlsUkd6dEREZjZQc1JWd3k3LzZPZm9EUWR6bnVvNC8yR1pvWjdSbWZzY1ZpQWZyeHNHdmVEc3pjOE1Qb3NVL09aRkoxSTVyeTJIWE40SkRkdkxJVlBES29RVnRqZkdnWnVIRXJoK0NqRThaUnVFQytqSytVQXFtbXppZWxYcXo3VWRVWVBTTzdZMFJJU2t6aC95T0t2UWpUbmJhbmlWK3kzbTc2UEhuUDdtRXNxaC81bWxPRWNsNUZNR1VsUGJHNHdlKzQ4ek9SYTY3c243Zy9PNVcwWnVvK2VPVHpKMGdTOTV4ckJVNEZDcVZjSDFQVUowOE1zOU9lOEp4SlhQMk5IWjFkU1AwNnFxdDVsTHd2dm5KNCtYNmxlVm1POFB2UitmZGd2NGFiYTE2eEY4RFVFNlFZT0N5SnorT3YxUVI5aitVN1czSWh5T1N0RXlCczc3Ri8rYW4rbFA1T053bThYdTFlZm94Y01QUmliVzc5M1p4RFBTODFxeW5PS0dWYmU1cXFEUjJOODZvbVFweVUxQjlWNGphblR3Z3ZEQT09.M-LYqMR7--S6Nje1F18AG-PFZ4SQPdzBNnPdVP1a9t4",
    "connection": "keep-alive",
    "host": "phinnisi.pelindo.co.id:9018",
    "origin": "https://phinnisi.pelindo.co.id",
    "referer": "https://phinnisi.pelindo.co.id/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
    "sub-branch": "OTk5,NzU=,NzI=,MTAx,NjE=,ODE=,MjU=,ODM=,NzQ=,NzM=,Mjk=,Mjc=,MTc=,NTc=,MTY=,MTA4,NjA=",
    "id-unit": "",
    "id-zone": "",
}

def scrape_data(page=1, record=100000):
    params = {
        "page": page,
        "record": record,
        "data":""
    }
    try:
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=(10, 60))
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"[!] Error during request: {e}")
        return None

def save_to_csv(data, filename=None):
    if filename is None:
        # Default to current directory (root)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "wasop.csv")
    try:
        # Extract only the required columns
        df = pd.DataFrame(data["data"]["dataRec"])
        # Filter rows based on name_process_code
        filtered_df = df[df["name_process_code"].isin(["Request PPKB", "Realization"])]
        filtered_df = filtered_df[["no_pkk", "no_pkk_inaportnet", "vessel_name", "company_name", "name_process_code", "gt", "loa","name_branch","departure_date"]]
        # Coerce 'gt' to numeric and keep only rows where gt > 500
        filtered_df = filtered_df.assign(gt=pd.to_numeric(filtered_df["gt"], errors="coerce"))
        filtered_df = filtered_df[filtered_df["gt"] > 500]
        filtered_df.to_csv(filename, index=False)
        print(f"[i] Filtered data saved to {filename} (GT > 500 only)")
    except Exception as e:
        print(f"[!] Error saving to CSV: {e}")

async def scrape_data_async(session, page, record, semaphore):
    """Async version untuk concurrent scraping"""
    params = {
        "page": page,
        "record": record,
        "data":""
    }
    
    async with semaphore:
        try:
            print(f"  ⏳ Fetching page {page}...", end='', flush=True)
            async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=120)) as response:
                response.raise_for_status()
                data = await response.json()
                print(f" ✓", flush=True)
                return data, page
        except Exception as e:
            print(f" ✗ ERROR", flush=True)
            print(f"[!] Error during async request for page {page}: {e}")
            return None, page

async def scrape_all_data_async(record=1000):
    """
    Scrape all data menggunakan async concurrent requests untuk speed up
    """
    print("=" * 70)
    print("🚀 WASOP ASYNC SCRAPER - Starting...")
    print("=" * 70)
    
    # Headers untuk aiohttp
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
        "access-token": HEADERS["access-token"],
        "access_token": HEADERS["access_token"],
        "connection": "keep-alive",
        "host": "phinnisi.pelindo.co.id:9018",
        "origin": "https://phinnisi.pelindo.co.id",
        "referer": "https://phinnisi.pelindo.co.id/",
        "user-agent": HEADERS["user-agent"],
        "sub-branch": HEADERS["sub-branch"],
        "id-unit": "",
        "id-zone": "",
    }
    
    # Semaphore untuk limit concurrent requests
    semaphore = asyncio.Semaphore(8)
    all_data = []
    start_time = time.time()
    
    print(f"⚙️  Max concurrent requests: 8")
    print(f"📦 Batch size: 10 pages per batch")
    print(f"⏱️  Timeout: 120 seconds per request")
    print("=" * 70)
    
    async with aiohttp.ClientSession(headers=headers) as session:
        page = 1
        batch_size = 10
        batch_num = 1
        
        while True:
            print(f"\n📊 BATCH #{batch_num} - Processing pages {page} to {page + batch_size - 1}...")
            
            # Create tasks for batch of pages
            tasks = []
            for i in range(batch_size):
                current_page = page + i
                task = scrape_data_async(session, current_page, record, semaphore)
                tasks.append(task)
            
            # Execute batch concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            has_data = False
            batch_records = 0
            for result in results:
                if isinstance(result, Exception):
                    print(f"  ✗ Exception: {result}")
                    continue
                    
                data, p = result
                if not data or "data" not in data or "dataRec" not in data["data"]:
                    continue
                    
                batch = data["data"]["dataRec"]
                if batch:
                    all_data.extend(batch)
                    batch_records += len(batch)
                    has_data = True
                    
                    # Check if this is the last page
                    if len(batch) < record:
                        print(f"\n✅ Batch #{batch_num} completed: {batch_records} records")
                        print(f"🏁 Last page reached at page {p}")
                        elapsed = time.time() - start_time
                        print("=" * 70)
                        print(f"✅ SCRAPING COMPLETED!")
                        print(f"📊 Total records: {len(all_data):,}")
                        print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
                        print(f"⚡ Speed: {len(all_data)/elapsed:.1f} records/sec")
                        print("=" * 70)
                        return all_data
            
            if batch_records > 0:
                elapsed_so_far = time.time() - start_time
                print(f"✅ Batch #{batch_num} completed: {batch_records} records in {elapsed_so_far:.1f}s")
                print(f"📊 Total so far: {len(all_data):,} records")
            
            # If no data in entire batch, we're done
            if not has_data:
                print(f"\n🏁 No more data found")
                break
                
            page += batch_size
            batch_num += 1
    
    elapsed = time.time() - start_time
    print("=" * 70)
    print(f"✅ SCRAPING COMPLETED!")
    print(f"📊 Total records: {len(all_data):,}")
    print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
    print(f"⚡ Speed: {len(all_data)/elapsed:.1f} records/sec")
    print("=" * 70)
    return all_data

def scrape_all_data(record=1000):
    """
    Wrapper to run async scraping
    """
    return asyncio.run(scrape_all_data_async(record))

if __name__ == "__main__":
    print("[i] Starting data scraping...")
    all_data = scrape_all_data()
    if all_data:
        save_to_csv({"data": {"dataRec": all_data}})
