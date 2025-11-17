import requests
import pandas as pd
from datetime import datetime, timedelta
import brotli
import json
import os
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

API_URL = "https://phinnisi.pelindo.co.id:9018/api/monitoring/ina-spb"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
    # kirim keduanya sesuai jejak network
    "access-token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMTlkQ0JZMXFMc3ZvTnZxaWd5OUZ5K2M1WlFqcHVrR1UvRkZoa3ZDTVpLdnVzOXJFTFB3QnVHMmpwTEprMWJETWFsZHhIZWxNc0EvNnhJRlFaUmE5MWg2a2NhUmYwQnVYa3pXRWl0czFpZXY1YzV4SjhvNVpVWVFWMzk0c2tKa05oRUgzTlBuT0xJM0RNQW5yU0tyNVF6MDZ1KzFQbW1WQ1BLV3Mya3Q5M1RBRlZ5NzROeXVHcEF6NHpoTWZlYWFXUjJSZFQ3V0NQRjRnVjRrRSttL08yazIwbExkVXlCb3hHc01DNlIrT2lvUm0wVlN0UUpPTXZDV1hseXBRSGlJTWtlVUVUalAwK1pacjQ3UDV3cDNrTmZzZDlHdUU5aGxTM3lSTTF6aVpmOVRDa2Zvclh1cEhVQmpMTEFZeWQwdzVsVG1sRDdvWG9OODB1WkJ5VUNxOEdEV0FlK2hiYXRNZjBmZ28zVXJhV2sxU1RzM3FhcEJNTkE1UnBHSlJ4QzNreEgvT2xacTNGdmdDQjdTOHNOZFJSMzI0QVF0TmQ1OGQ4L0tiUzMzYXhESE9mVnhvdDJqZ1M5dml1WkdvQzJRaEdSSlhKNlArTmhRSjdKbkpmQm5TKzlEbEN1djg4S1RPQkFjcjNoZVowaExmdHdTME02cWZ0RmZaSzAzT0p3WXM0S2c0R1YxVVQzajJhNEFZN1lHV1FLTXpGWmVhYndKbUQrdDdmR1F2UW1aUjR6bXlpRjBkTnNvaW92WFp0Nzk2YnhkZXA1czBMQ1ptd3NlcHczN296RS96Rzd2LzlyNWZpbUdPdjdlNGhzT1RXZG1EUFhhWnZuYkxmOG9mSHl3UXQzME5qM3dpOE9qdzdlNU5CRlFnVVhYNWx3UFBCQjFialRUdmZDQS9RaDhEbUJCSUNxcjdZSnpFalpEVWdTRHo3MG1QTGp5Vm1NQmhNa3EwV3NtalAySEtWeHBtL2FDdktPS0UrWnVRcTRWcHFkM3JXb1oyU1NZZFZmYlJCcmVWNjZnVDRuN1o0RFdBTytWYjErTEJBdkk4V1FPVlpVWjhWdC9jZDY1c3UzdERwTElkNG9jZWV4S1o5Ykh0YytVTGVOM2VlNUhyY0tQNGppRUdSNzI2cTBxMllHODFOT1lDRDIyYkFMMjFoUUNVZ2tHVGtaNm1vN2E0MVExd2MwVkJOK0NuWjl2MXIzeUxZNUt3ckFNQXFua2Y4Q1BkWkFOWERFakxHWkljaVpBd1ZUWWtNNUMyNmdBUWp2eVJLVzNDeFpBNVRqZ2lUNkMzZlJkejg5a1JhYUJkRTkwSTY4ak1zQ0tIclRadGdUeWtEUUd6YjZjcm5OaUsxVTB3WnpGL0xUSmlSWHliQWJ0MkxUaFhTYnZGb3ZHZWR5Q0xDMUFSSklXTTdLNk1heWwyTHZ6SnRTZXloWHRvZUNvMXZ3QTNacHIvdTByQm1vcXBmV3hZU2E5NS9yY0ZSKzlVNTBoWFg3VXFSVTB6OFFmWXFoUUNpNzg5NXZZMXhIb0tlRGRUQzZQeTNLUGdsSTVNYzJleWVwZ2QzNzk0VmpXNmlzNkh4Ui9PNU05M01icFJQMkpxL3pFQklyaG5za1NMcWNpSUFkZ25zTlgxTEtqSGI1TEs4M3BzZ1RHUSs5YlhjdkZUUmdteGdBOE43ZGRDTlphcFd1ektuWEN6WTJpQmdKUFJpS0lmaVd3WmdGQ1N4QktOY1RFL0Q0ZE9rNyticmM3RFp0eHM2NmZSMStHcUs4eUVVTFhzbGZ3UmJMbW5EVU83NzhTRUJINzloa1BKbG9aQ3I5ZlIwN2xsc0RXcERRNE5neStQbUxZTnF0bU85VnJuRkNkN3VNYnVHQ3ZlcVMrOWlvWDlzaG9YdWRyeEdIdStBVVVJTkJaU0lZQXEyR1hiclhkQlZjN2x4bGtxTVVaOWIwdSthYzZuUXdUNmsvaHh4V2pMSVMxS0hVZVJndXNCOERlR2kvdWJQbTdRQ0RCWjJkNHBPSnNtbkhYc0FZSktVSWN0Wnhtd3k5SW0yQmFBUndpQ3F6eitQdEdDZWRHRFBHUU5zUktjR2NZTnc1UjBnU0twdTY1bVdkWld6TERaSy9YaVVkYWJVM0tqdEhwRVNSMjFIbEQvUjl0dGkzWERMcjdGNGtGTXBhNXlvRUdYZGFxNjlUL2d3eEtRSytuNWVXMkhxcUVYRWQvbVBTNlZLdm96dkw2TVlnMnBjWDMyTVd4V2dacGY3dGIyR3I3R3g4WHIyS1lXOGJkd3MvekZHdGdDTk93RmttUEpFMXVybitmcGVCcFJFeTI5ekxNeHdYVzNrOElvSUIwUUxMbUQ0eVZBOGk2UW9KM3V6dnJHMUkzSGV6YXJyR05heWhsM0ErQ1lLNnNRQzhkYjlXOW5aYnRhNy82SlFyL28zbU9xK0dyY1JsVHRkYUFUK3ZYMFZHczJtb3prR1RrRGNEMTFZVDU2Rm9Pa2thZmhiSm9VeDBkMENTUUpoK2xKdWRudWdYeVlNUUZNMkd2cWh1NnVMRTNRTHV3SmVFTDlTbmVMOEkzLzlBYVBBUXhnYjl1T1h0Vi9GSkVrUWJJUllSUVQrNkZtdDRIWWRvNmFsRCtlUXVvR0E2SWZnaXRRNGJyTXdsQmd2YUZUb09GWEU5SlZEYjV0ZFFqVllvTzVsMEpyMWowOGczR3p5bHliZjZGRnptRm9KNG1yTFhLcXk0OEx2aUdxRFNYam1UQ0dHZFc4QzRrMjlVTmpzQUlvZ2ExRnNHL2R4ZkNyT0haOW5Pd09BcEptaVMyVHByb2FRWGhHNWZvTmR3SlRabXd2T3MyOTE3S05vakQ2Tjd3MzJNUlZyLzVYT0JGRUNvS2V5bE5FSDJCbVdjT0l4NTg0OXFqeUk2by9tZlM0RlJyK0M5cWZLWUJxOC83Yk9TUlRYR20zSlhiTGlDUGk0cS9qRFhqWkxua1kwZnR4SXFvTk5PM2ZQVUVjZlFRZE4wTFpKTHRKTmNybzJMeml2RU00b0pBK3RVMitsS2RraEpYdC9hR0x6enArbEcwdEx2WDBoQko4cDVyVGNTaTBHdllKVWJrdXFoNEo3b0tXSkkzMTNCeUpibVdEdDMwTGxSMGNJVS9idkJ6V0UvTlNHSkhkVWZKMUExMWxTUnh1V3U1RXovT3o5L1VEczRldzdWLzk2SW02c3JiVlJPc013bUgwZDBPRjBIN2xtZzA.J6xAZ4VfltUo4-yziXAewbJprwFyMAJD5sZN_Qqc9SM",
    "access_token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMTlkQ0JZMXFMc3ZvTnZxaWd5OUZ5K2M1WlFqcHVrR1UvRkZoa3ZDTVpLdnVzOXJFTFB3QnVHMmpwTEprMWJETWFsZHhIZWxNc0EvNnhJRlFaUmE5MWg2a2NhUmYwQnVYa3pXRWl0czFpZXY1YzV4SjhvNVpVWVFWMzk0c2tKa05oRUgzTlBuT0xJM0RNQW5yU0tyNVF6MDZ1KzFQbW1WQ1BLV3Mya3Q5M1RBRlZ5NzROeXVHcEF6NHpoTWZlYWFXUjJSZFQ3V0NQRjRnVjRrRSttL08yazIwbExkVXlCb3hHc01DNlIrT2lvUm0wVlN0UUpPTXZDV1hseXBRSGlJTWtlVUVUalAwK1pacjQ3UDV3cDNrTmZzZDlHdUU5aGxTM3lSTTF6aVpmOVRDa2Zvclh1cEhVQmpMTEFZeWQwdzVsVG1sRDdvWG9OODB1WkJ5VUNxOEdEV0FlK2hiYXRNZjBmZ28zVXJhV2sxU1RzM3FhcEJNTkE1UnBHSlJ4QzNreEgvT2xacTNGdmdDQjdTOHNOZFJSMzI0QVF0TmQ1OGQ4L0tiUzMzYXhESE9mVnhvdDJqZ1M5dml1WkdvQzJRaEdSSlhKNlArTmhRSjdKbkpmQm5TKzlEbEN1djg4S1RPQkFjcjNoZVowaExmdHdTME02cWZ0RmZaSzAzT0p3WXM0S2c0R1YxVVQzajJhNEFZN1lHV1FLTXpGWmVhYndKbUQrdDdmR1F2UW1aUjR6bXlpRjBkTnNvaW92WFp0Nzk2YnhkZXA1czBMQ1ptd3NlcHczN296RS96Rzd2LzlyNWZpbUdPdjdlNGhzT1RXZG1EUFhhWnZuYkxmOG9mSHl3UXQzME5qM3dpOE9qdzdlNU5CRlFnVVhYNWx3UFBCQjFialRUdmZDQS9RaDhEbUJCSUNxcjdZSnpFalpEVWdTRHo3MG1QTGp5Vm1NQmhNa3EwV3NtalAySEtWeHBtL2FDdktPS0UrWnVRcTRWcHFkM3JXb1oyU1NZZFZmYlJCcmVWNjZnVDRuN1o0RFdBTytWYjErTEJBdkk4V1FPVlpVWjhWdC9jZDY1c3UzdERwTElkNG9jZWV4S1o5Ykh0YytVTGVOM2VlNUhyY0tQNGppRUdSNzI2cTBxMllHODFOT1lDRDIyYkFMMjFoUUNVZ2tHVGtaNm1vN2E0MVExd2MwVkJOK0NuWjl2MXIzeUxZNUt3ckFNQXFua2Y4Q1BkWkFOWERFakxHWkljaVpBd1ZUWWtNNUMyNmdBUWp2eVJLVzNDeFpBNVRqZ2lUNkMzZlJkejg5a1JhYUJkRTkwSTY4ak1zQ0tIclRadGdUeWtEUUd6YjZjcm5OaUsxVTB3WnpGL0xUSmlSWHliQWJ0MkxUaFhTYnZGb3ZHZWR5Q0xDMUFSSklXTTdLNk1heWwyTHZ6SnRTZXloWHRvZUNvMXZ3QTNacHIvdTByQm1vcXBmV3hZU2E5NS9yY0ZSKzlVNTBoWFg3VXFSVTB6OFFmWXFoUUNpNzg5NXZZMXhIb0tlRGRUQzZQeTNLUGdsSTVNYzJleWVwZ2QzNzk0VmpXNmlzNkh4Ui9PNU05M01icFJQMkpxL3pFQklyaG5za1NMcWNpSUFkZ25zTlgxTEtqSGI1TEs4M3BzZ1RHUSs5YlhjdkZUUmdteGdBOE43ZGRDTlphcFd1ektuWEN6WTJpQmdKUFJpS0lmaVd3WmdGQ1N4QktOY1RFL0Q0ZE9rNyticmM3RFp0eHM2NmZSMStHcUs4eUVVTFhzbGZ3UmJMbW5EVU83NzhTRUJINzloa1BKbG9aQ3I5ZlIwN2xsc0RXcERRNE5neStQbUxZTnF0bU85VnJuRkNkN3VNYnVHQ3ZlcVMrOWlvWDlzaG9YdWRyeEdIdStBVVVJTkJaU0lZQXEyR1hiclhkQlZjN2x4bGtxTVVaOWIwdSthYzZuUXdUNmsvaHh4V2pMSVMxS0hVZVJndXNCOERlR2kvdWJQbTdRQ0RCWjJkNHBPSnNtbkhYc0FZSktVSWN0Wnhtd3k5SW0yQmFBUndpQ3F6eitQdEdDZWRHRFBHUU5zUktjR2NZTnc1UjBnU0twdTY1bVdkWld6TERaSy9YaVVkYWJVM0tqdEhwRVNSMjFIbEQvUjl0dGkzWERMcjdGNGtGTXBhNXlvRUdYZGFxNjlUL2d3eEtRSytuNWVXMkhxcUVYRWQvbVBTNlZLdm96dkw2TVlnMnBjWDMyTVd4V2dacGY3dGIyR3I3R3g4WHIyS1lXOGJkd3MvekZHdGdDTk93RmttUEpFMXVybitmcGVCcFJFeTI5ekxNeHdYVzNrOElvSUIwUUxMbUQ0eVZBOGk2UW9KM3V6dnJHMUkzSGV6YXJyR05heWhsM0ErQ1lLNnNRQzhkYjlXOW5aYnRhNy82SlFyL28zbU9xK0dyY1JsVHRkYUFUK3ZYMFZHczJtb3prR1RrRGNEMTFZVDU2Rm9Pa2thZmhiSm9VeDBkMENTUUpoK2xKdWRudWdYeVlNUUZNMkd2cWh1NnVMRTNRTHV3SmVFTDlTbmVMOEkzLzlBYVBBUXhnYjl1T1h0Vi9GSkVrUWJJUllSUVQrNkZtdDRIWWRvNmFsRCtlUXVvR0E2SWZnaXRRNGJyTXdsQmd2YUZUb09GWEU5SlZEYjV0ZFFqVllvTzVsMEpyMWowOGczR3p5bHliZjZGRnptRm9KNG1yTFhLcXk0OEx2aUdxRFNYam1UQ0dHZFc4QzRrMjlVTmpzQUlvZ2ExRnNHL2R4ZkNyT0haOW5Pd09BcEptaVMyVHByb2FRWGhHNWZvTmR3SlRabXd2T3MyOTE3S05vakQ2Tjd3MzJNUlZyLzVYT0JGRUNvS2V5bE5FSDJCbVdjT0l4NTg0OXFqeUk2by9tZlM0RlJyK0M5cWZLWUJxOC83Yk9TUlRYR20zSlhiTGlDUGk0cS9qRFhqWkxua1kwZnR4SXFvTk5PM2ZQVUVjZlFRZE4wTFpKTHRKTmNybzJMeml2RU00b0pBK3RVMitsS2RraEpYdC9hR0x6enArbEcwdEx2WDBoQko4cDVyVGNTaTBHdllKVWJrdXFoNEo3b0tXSkkzMTNCeUpibVdEdDMwTGxSMGNJVS9idkJ6V0UvTlNHSkhkVWZKMUExMWxTUnh1V3U1RXovT3o5L1VEczRldzdWLzk2SW02c3JiVlJPc013bUgwZDBPRjBIN2xtZzA.J6xAZ4VfltUo4-yziXAewbJprwFyMAJD5sZN_Qqc9SM",
    # header tambahan agar mirip request browser
    "origin": "https://phinnisi.pelindo.co.id",
    "referer": "https://phinnisi.pelindo.co.id/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
    "host": "phinnisi.pelindo.co.id:9018",
    "sub-branch": "OTk5,NzU=,NzI=,MTAx,NjE=,ODE=,MjU=,ODM=,NzQ=,NzM=,Mjk=,Mjc=,MTc=,NTc=,MTY=,MTA4,NjA=",
    "id-unit": "",
    "id-zone": ""
}

def get_month_periods(start_year=2025):
    now = datetime.now()
    periods = []
    year = start_year
    while year <= now.year:
        start_month = 1
        end_month = 12 if year < now.year else now.month
        for month in range(start_month, end_month + 1):
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            periods.append((start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        year += 1
    return periods

def scrape_data(page=1, record=100000, periode=""):
    params = {
        "page": page,
        "record": record,
        "data": "",
        "periode": periode
    }
    try:
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=(10, 60))
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"[!] Error during request: {e}")
        return None

def save_to_csv(data, filename=None):
    if filename is None:
        # Default to current directory (root)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "spb.csv")

    try:
        df = pd.DataFrame(data)

        # Pastikan kolom yang dibutuhkan ada, jika tidak, tampilkan kolom yang tersedia
        required_cols = ["nomor_pkk", "nomor_spb", "vessel_name", "gt", "loa", "name_branch", "departure_date", "waktu_tolak"]
        available_cols = [col for col in required_cols if col in df.columns]
        if len(available_cols) < len(required_cols):
            print(f"[!] Kolom berikut tidak ditemukan di data: {set(required_cols) - set(available_cols)}")
        if not available_cols:
            print("[!] Tidak ada kolom yang bisa diekspor.")
            return

        filtered_df = df[available_cols]

        # Filter GT > 500 if column available
        if "gt" in filtered_df.columns:
            filtered_df = filtered_df.assign(gt=pd.to_numeric(filtered_df["gt"], errors="coerce"))
            filtered_df = filtered_df[filtered_df["gt"] > 500]

        # Filter by waktu_tolak year == 2025 when available
        if "waktu_tolak" in filtered_df.columns:
            # Try parsing common datetime formats; fallback to substring match for '2025'
            try:
                wt_parsed = pd.to_datetime(filtered_df["waktu_tolak"], errors="coerce")
                if wt_parsed.notna().any():
                    filtered_df = filtered_df[wt_parsed.dt.year == 2025]
                else:
                    filtered_df = filtered_df[filtered_df["waktu_tolak"].astype(str).str.contains("2025")]
            except Exception:
                filtered_df = filtered_df[filtered_df["waktu_tolak"].astype(str).str.contains("2025")]
        else:
            print('[!] Column "waktu_tolak" not found in data; no waktu_tolak filtering applied.')

        if filtered_df.empty:
            print(f"[!] No rows match the filters (GT>500 and waktu_tolak=2025). No file written.")
            return

        filtered_df.to_csv(filename, index=False)
        print(f"[i] Filtered data saved to {filename} (GT > 500, waktu_tolak=2025, columns: {available_cols})")

    except Exception as e:
        print(f"[!] Error saving to CSV: {e}")

async def scrape_data_async(session, page, record, periode, semaphore):
    """Async version untuk scraping dengan semaphore untuk kontrol concurrency"""
    params = {
        "page": page,
        "record": record,
        "data": "",
        "periode": periode
    }
    
    async with semaphore:
        try:
            async with session.get(API_URL, params=params, timeout=aiohttp.ClientTimeout(total=120)) as response:
                response.raise_for_status()
                data = await response.json()
                return data, periode, page
        except Exception as e:
            print(f"[!] Error during async request for {periode} page {page}: {e}")
            return None, periode, page

async def scrape_period_async(session, start, end, semaphore):
    """Scrape semua halaman untuk satu periode"""
    periode_str = f"{start} s/d {end}"
    print(f"[i] Scraping periode: {periode_str}")
    
    all_batch_data = []
    page = 1
    
    while True:
        data, _, _ = await scrape_data_async(session, page, 1000000, periode_str, semaphore)
        
        if not data or "data" not in data or "dataRec" not in data["data"]:
            break
            
        batch = data["data"]["dataRec"]
        all_batch_data.extend(batch)
        print(f"  {periode_str} - Page {page}: {len(batch)} records")
        
        if len(batch) < 1000:
            break
        page += 1
    
    return all_batch_data

async def scrape_all_data_async():
    """Scrape semua periode secara concurrent dengan async"""
    periods = get_month_periods(start_year=2025)
    print(f"[i] Total {len(periods)} periods to scrape with async concurrency...")
    
    # Semaphore untuk membatasi concurrent requests (max 6 bersamaan)
    semaphore = asyncio.Semaphore(6)
    
    # Custom headers untuk aiohttp
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
        "access-token": HEADERS["access-token"],
        "access_token": HEADERS["access_token"],
        "origin": "https://phinnisi.pelindo.co.id",
        "referer": "https://phinnisi.pelindo.co.id/",
        "user-agent": HEADERS["user-agent"],
        "host": "phinnisi.pelindo.co.id:9018",
        "sub-branch": HEADERS["sub-branch"],
        "id-unit": "",
        "id-zone": ""
    }
    
    start_time = time.time()
    all_data = []
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Create tasks untuk semua periode
        tasks = [scrape_period_async(session, start, end, semaphore) for start, end in periods]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all data
        for result in results:
            if isinstance(result, Exception):
                print(f"[!] Exception in period task: {result}")
                continue
            if result:
                all_data.extend(result)
    
    elapsed = time.time() - start_time
    print(f"[i] Total records fetched: {len(all_data)} in {elapsed:.2f} seconds")
    return all_data

def scrape_all_data():
    """Wrapper function untuk menjalankan async scraping"""
    return asyncio.run(scrape_all_data_async())

def fetch_data(base_url, headers, params):
    """
    Fetch data from the API.
    """
    try:
        # Gunakan timeout dan biarkan Requests auto-decompress (tanpa stream)
        response = requests.get(base_url, headers=headers, params=params, timeout=(10, 60))
        print(f"HTTP Status Code: {response.status_code}")
        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            # fallback ke manual decode
            content = response.content
            if response.headers.get("Content-Encoding") == "br":
                try:
                    content = brotli.decompress(content)
                except Exception as e:
                    print(f"⚠️ Brotli decode gagal: {e}, fallback pakai raw content")
            return json.loads(content.decode("utf-8", errors="ignore"))

    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return None
if __name__ == "__main__":
    all_data = scrape_all_data()
    if all_data:
        save_to_csv(all_data)