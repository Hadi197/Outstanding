import requests
import csv
import brotli
import json
import os
import pandas as pd

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

def save_to_csv(data, filename="spb.csv"):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)

        df = pd.DataFrame(data)

        # Normalisasi: jika hanya ada 'nomor_pkk', buat kolom 'no_pkk'
        if "no_pkk" not in df.columns and "nomor_pkk" in df.columns:
            df["no_pkk"] = df["nomor_pkk"]

        # Pastikan kolom target ada
        target_cols = ["no_pkk", "nomor_spb", "waktu_tolak"]
        for col in target_cols:
            if col not in df.columns:
                df[col] = None

        # Simpan hanya kolom yang diminta
        df = df[target_cols]
        df.to_csv(file_path, index=False)

        print(f"[i] Data saved to {file_path} (columns: {', '.join(target_cols)})")
    except Exception as e:
        print(f"[!] Error saving to CSV: {e}")

def main():
    """
    Fetch data from the API and save it to a CSV file.
    """
    base_url = "https://phinnisi.pelindo.co.id:9018/api/monitoring/ina-spb"
    headers = {
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
        "sub-branch": "OTk5,NzI=,MTAx,NjE=,ODE=,MjU=,NzU=,ODM=,NzQ=,NzM=,Mjk=,Mjc=,NTc=,MTY=,NjA=",
        "id-unit": "",
        "id-zone": ""
    }
    params = {
        "data": "",
        "record": 100000,
        "page": 1,
        "start_date": "2025-09-08",
        "end_date": "2025-10-08",
        "is_success": ""
    }

    # Fetch data from the API
    response = fetch_data(base_url, headers, params)

    # Parsing yang lebih toleran terhadap variasi struktur respons
    records = None
    if response:
        data_field = response.get("data", response)
        if isinstance(data_field, dict) and "dataRec" in data_field:
            records = data_field["dataRec"]
        elif isinstance(data_field, list):
            records = data_field
        elif isinstance(response, dict) and "dataRec" in response:
            records = response["dataRec"]
        elif isinstance(data_field, dict):
            for k in ("records", "rows", "items", "list"):
                if k in data_field and isinstance(data_field[k], list):
                    records = data_field[k]
                    break

    if records:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(base_dir, "spb.csv")
        save_to_csv(records, output_file)
    else:
        print("⚠️ No data found in the API response.")

if __name__ == "__main__":
    main()
