import requests
import csv
from datetime import datetime, timedelta

API_URL = "https://phinnisi.pelindo.co.id:9014/api/reporting/daily-pilotage/list"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMStXLzc5dGhtSndHaFp5MkZWaTRnS1c4WHNLQThTS1p1RW9mYVYxR2hRSjVvZ2FCek1BalV3M2QzbUl6RjVTWXJER2ZBZU5LN3lvMGdtUXRYTFpjd1YrWEhzZFlXVnRqTWVJeUVQbHhSbm9IUjlkNkxVVnVZWUcxeFJiT3FLVGY2VXlhS24vcnJLNnJzYlVaVlNxblcwRHZUbnBTL2tCOE5TZ0E0QmlETm8yWHVxeVBuQlZDak1FdHZwUlZCYnR4Q3VDc1RQUmZTaU5KUXo3TFNoYzJnUjlCbjF5LzJpenJlTlVPcm1SRnUvajNLZzZjUzJaWTd6T0R0Vlg0VURJNU5IdFgzdGQ3aWxlVzRENnU0QjBuaTRrS3VmZmhZL3JzZ25jZk5vMjYyREtPWkhPUFZ0T0IzQTlKcm1VYWY2amVlVms5UGs3bzZFVEg0aWQ1eU1RWFpWaksrWWMvbW5NQ1IxOTQyWW1sNTEvZWFqeXpnN0RPUjJyUE9xZ3NSbVUyTFJxRytublF0VWZ1ak1uSlZDVFpBd3UvNURzV3ltdDc0MXFHb2JHUHdncGREVlptMnN1aWt1MFFPUEJsbXFKZ2dlYkJLNlVjVERRNFhJNTF3Q2l1SGRmNUpYRTU1ZU02cWJrUWcrM3JuRTYrU0l3blhITHhOeGlGbCsrQW95b1B2aFNFczRLNGpLU3dpNGdvSFZTWTBrUnlXYSt4MTBNMWdHbmdSWXFNTE5yelMzZk5TcUprd1d0SlpMb0xQRnRrcUNWMk5xaVM1NHRSZDExb2lDd0IzeWhqdkUxbHUxM2hXbDRFTDU3VEhXM0RwZHZxdmloSlJXVm4wV1J5S21WeHp2RDBxaFpEZnd4T0FxQkZpemZtQWNGb1lmcGdiTkVoSnlkYzJYdFVzeVYyQWhJZEw1VWk4WEQveFpGUHJ4RkY2SGRodGJSK2pUa0EzVmxEK1QzeTJ3bFFwVW5CVHhTL0JudlAySnkydWhLRWV3bnZGZVdZWmN0SjB6UnZHU1IxdHBKZXVXU3ErVWU1eGUwOXdvMk5VeDVMVUs0T2Vvc3pvQXpzcnBEY2NldUpLdi8zWXFVOWhHcEthaFAybFBJWHBuKzMzZVYxR0xybGdGeEFHd1F2YjFYM1NQQjJENkdRWXBTbFU3VzJlanpRWXlIOTZDay9MSzR2QjV0cFpWSnVnU0M4SXU5QWUzUGV5YWFRYTZMdjh2M2lEQzFGSjBnR1Vtb3dWbWVMVDczS3RqMTcvVktjR1AvVU16S3VLbXdUNHEvV2VmMExFZEhWNEwvbThwbllOTHIzZUpKcFdueVBTQjZPRkJXdmxOVXE1V2FmOThwUk0rK2dCWGo3QmhxemVwaFB0WE5pTUxxUjlwcVpiUWM5MFdRWEpaVzF1NEhrUnhFUHNDRmJnRGtkTFhaQSswekl4RzVRQTZOTkpzNVl0MmV3eCtyRDA2cW1wK0xEaUYxSEd3cHQ0MnUwcUQza3dBMTE2ZUVJclpXbGNRbHp0Y0k5aUtOaUZiNGNuY25SVFRWQjNhd3poL1U3SUYxSWNHY1VNT0NkRDVRY0hyUlExSlV5UEdEckVpaE5mSFlJVmI2M0oxTExyOURUbTFHamIvL3Q5MTdBWjhpM3FId0J3L0cvYXVnQ2ZoMzVYUm9uY2Yzd3gwK1hMeURvcVRmZWdkNEdkVDIvQ2RlTzlFbFNxWk5DK1pXcUlRdlJaaDlEcEhlYis3OW9EMHZ0WUJkZTM4UTZVRnV3dnVRNVFCaGlUblNodThiWGZVNHA3REFDaWVkSFFYYXFtQStNUmtFcGUxemp6dTNUTEZMMU94QWxNQ2hUSnAxYk94LzlYTk9vNVA3VUh6Q21JY1E2L0pSdUVkRHdOeUFCN1pZZFZsWWRrQ3hLbFV6eHZ3V0hXNnJkeG9EeFNkUHpzZk4xNEZsb0VkUGZoTlBPWFErdVlTVmdOMnJqMEEySUJlUzFJMmNUL2pBR1ZNS0xhc2hRQ0doTVNWNGJKSW5lMFhwMzYxT1h2S1lrWFJGL1dReXVaUHVZc3E4TDdJclU2UEVsN2dMWWszeENpaGt2Y0lYOFhRbmVjbndxaDhhZmZMa2NTUm9TaitvM2dqREZwVGp1V1pNaEo3TE11NFI1c2U1Wm5iUFpoMVdCY0Z4N21pY1NrTi9scVpnN2VCenBab2lmbnI3QmZ4ZVRVY2tVK25KeTJNSXlpU1VLUHZBRFdSV1JKcEZVdzd4SHg3aDRZaWJwbmxqLzVYUC9yZjA1OVV4ME9hTytpNjkwZ0NoSHZIUlBOSTFJa00xQjNRR29WRm1NdXBMWmlMTU5hV3dEV2hmTFhTRGtJLzUyTlE3bDA1VFNjNDdBdUZjbkd0NkUzRmJjUmZsL3l1Um9qMHRPMDBSWURGSkhDZFBxM09sWk8zd0hQZDFuendIWXYvR1kxRlU2NmtobGc0UXRSeGFvQVhiMlkwNHRVb3hYVUtZNmd1S0M2L1YzOUN4QWlJb0FYeTZ5bnpBUUFrQUZDUlRPci9CK3VNbzdkay9BY0hLcWpaMWllYkRXWmFZTFB1ZTVWcFlqNVdyazhkNE9zRndNcmdHdFQxemVoT1g0TjlONXFWdm1ta1p3Z0p1ZlNxMVZSU01UTHlPbVJZZDE0aHk1M3U2SUtJMjlxZFRiR0lRV3BWUnVaWjY3U3prYnBSL014UE1LUUZZUGUxTVVCUDBzT0hvMUQ3YzFIeFo2VmEwUjdXbGZWL3hOclNXNFNSZDZZeER1RGw4eXFROXF2MlVVMm9BWlZHRHNyVVBFRU9XWjA3eTJFUU5VRnBkRTUyNVVjSWpCUjdnV3NKSzV6cUt0WXIwZ3FLcTZnRGZPb2dVN2Vncm9ZUnJabjRwa1NRRUZxMDZaejdXcjB2SGxYWDFlazJNMGJPb2gvcUVpc1lmby9kdWZGZFJMaVdwaVNoNnY2V3RIWElmcGtjUXVMTkJ4TFRPbVlRTEw1Y3ZsQ1RkSll2NUo4SVpCOUpFU1E5WjdOUW9NUGRDMVI2TkdzMUpyRlpwUHkySjU2Zzg4dklJUTlNV0ZUdDVNSElTdE54TjZmVU10dDh4M0dxRENmUG5McFdtQnVXYUtGMnpmZmRSdnRsUmMzRy9sUnpnaGNjdjEyL2xkN3hyeC9XVU5FaldDQUhnUWVxbmdITVhMVXNwdjdld3l4UjFTZElYbHBhMUN2RlFVUGhiU092aURTL2c.V85wJNkbUuMUbdijBefbMJREO5VpnEsTsHav2OUjtP8"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
    "access-token": ACCESS_TOKEN,
    "sub-branch": "OTk5,NzI=,MTAx,NjE=,ODE=,MjU=,NzU=,ODM=,NzQ=,NzM=,Mjk=,Mjc=,MTY=,NTc=,NjA=",
    "origin": "https://phinnisi.pelindo.co.id",
    "referer": "https://phinnisi.pelindo.co.id/",
    "connection": "keep-alive"
}

def scrap_daily_pilotage(start_date, end_date, page=1, record=1000, max_retries=3):
    params = {
        "start": start_date,
        "end": end_date,
        "data": "",
        "page": page,
        "record": record
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=120)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ReadTimeout as e:
            print(f"Timeout on page {page}, attempt {attempt+1}/{max_retries}")
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            print(f"Error on page {page}: {e}")
            if attempt == max_retries - 1:
                raise

def month_range(start_date, end_date):
    """Yield (start, end) date string for each month in the period."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start.replace(day=1)
    while current <= end:
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = (next_month - timedelta(days=1)).day
        period_start = current
        period_end = current.replace(day=last_day)
        if period_end > end:
            period_end = end
        yield period_start.strftime("%Y-%m-%d"), period_end.strftime("%Y-%m-%d")
        current = next_month

if __name__ == "__main__":
    # Contoh penggunaan
    start = "2023-01-01"
    end = "2025-12-31"
    record = 100000
    all_rows = []

    for period_start, period_end in month_range(start, end):
        print(f"Ambil data periode: {period_start} s/d {period_end}")
        page = 1
        while True:
            try:
                data = scrap_daily_pilotage(period_start, period_end, page=page, record=record)
            except Exception as e:
                print(f"Gagal mengambil page {page} periode {period_start} - {period_end}: {e}")
                break
            # Cari data tabular pada struktur nested
            rows = None
            if (
                isinstance(data, dict)
                and "data" in data
                and isinstance(data["data"], dict)
                and "dataRec" in data["data"]
                and isinstance(data["data"]["dataRec"], list)
            ):
                rows = data["data"]["dataRec"]
            else:
                if isinstance(data, dict):
                    for key in ['dataRec', 'data', 'rows', 'result', 'items']:
                        if key in data and isinstance(data[key], list):
                            rows = data[key]
                            break
                    if rows is None:
                        for key in ['data', 'result', 'items']:
                            if key in data and isinstance(data[key], dict):
                                for subkey in ['dataRec', 'rows', 'items']:
                                    if subkey in data[key] and isinstance(data[key][subkey], list):
                                        rows = data[key][subkey]
                                        break
                                if rows is not None:
                                    break
                elif isinstance(data, list):
                    rows = data

            # Filter hanya kp_grt > 500
            if rows is not None and len(rows) > 0:
                filtered_kp = []
                for row in rows:
                    try:
                        grt_val = float(row.get("kp_grt", 0))
                    except Exception:
                        grt_val = 0
                    if grt_val > 500:
                        filtered_kp.append(row)
                print(f"  Page {page}: {len(filtered_kp)} rows (kp_grt > 500)")
                all_rows.extend(filtered_kp)
                if len(rows) < record:
                    break
                page += 1
            else:
                break

    print(f"Jumlah total baris ditemukan: {len(all_rows)}")
    if all_rows:
        # Ambil hanya kolom yang diinginkan
        selected_cols = ["no_pkk_inaportnet", "no_pkk", "zone","status_nota"]
        # Filter hanya status_nota = BELUM VERIFIKASI
        filtered_rows = [row for row in all_rows if row.get("status_nota", "").strip().upper() == "BELUM VERIFIKASI"]
        # Hapus duplikat berdasarkan no_pkk_inaportnet (ambil satu saja)
        seen = set()
        unique_rows = []
        for row in filtered_rows:
            key = row.get("no_pkk_inaportnet", "")
            if key and key not in seen:
                seen.add(key)
                filtered_row = {k: row.get(k, "") for k in selected_cols}
                unique_rows.append(filtered_row)
        with open("lhgk.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=selected_cols)
            writer.writeheader()
            writer.writerows(unique_rows)
        print("Data berhasil disimpan ke lhgk.csv (hanya kolom yang dipilih & unik no_pkk_inaportnet)")
    else:
        print("Tidak ada data tabular untuk disimpan.")