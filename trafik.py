import requests
import csv
from datetime import datetime

def fetch_traffic_data():
    """1) Scrap data dari API dan kembalikan payload JSON mentah."""
    url = "https://phinnisi.pelindo.co.id:9014/api/reporting/traffic/list"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
        "access-token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMS8xNHN2ZVdlUWxQeEtmSTRiZWczTnZvaDY4QUZmYlZQUmpQRHpLaVpFWUx1SEhkMXRScHpubm83cldCaVNPNUtlN2FhTXpQRG9NTTlURUpDK1F3WlNscUFWVjlycngwRlQreXVza0I0UUxVdTc3R0grNlpYaGhjTy9aYkt3L05CL2h5eGFQTmxQOWY1c0xKcnBrMC9GSUFGM0J5cmlmSlhKT2pJcnQ1UjFrbVZLdHNWRXV1VWFKYTA5YklRQ0hsWHFNSlJkYmE5Q0d2aTdkSnRzZW50aEUxUlNGR3R2UkRKU3kyOTFvRGVtdCtkOE42K1ZHR1F1YU9NQ2dSK1c1RmdSZ0VqYzRQd0pOU2tDQk5oRFhPMTkwclZIU2thdGtOZ3hLZU13N0REem13bFdwVDlYU2t1QldHOThIdStSbCtFblZzcFJtbVFOdG05WnM3eUlOTWw4UFJ5UTk1dVRyRmRQeWdLRjdjSVRaakpCN0dpYjdPSzFKejBhTWRiSTFhR0hMSDdycktxRVRYckF1elJuYnFkZDJJTEdRWWtIZjE5bmFiVkpJT0VtRTMrNTloeGMyNHl0UXhqRmQ5R0MzaFV1T0xJczdoTHBmVUM0WFVvZjArVGxEK1dBMW9QTXg0WkdmeXFXWUNtRFBlZFVLaG1JbHl2ekxhb0NzZENyMVRZclhTSUNrRnQxWThDRS9PeFlzQXhCdGdCcUdOSTllQ3d1QVROdmZWSEtwd3IrMmFYNHcrMHMyRWJCU0Z5SHU3TGhPVTJ6d2FBNnMxa0FnVlFORGQ4dTNubHhEcS91a1JFVVMzVWhia3ZmOXZnMGY1TFBiOXorS1JuRWllUkhad1JEYjRSYjBiVUJEeTJGTDBEd1BSZmhRS0wweDl2MXJTQ1JJQVFJM3ZxVW1kYzcvSUdRbXNUbmRZNUUxbm1wVmhwRXRJVjhYZEcwenduRzQ0emhuZGswK2FybVRSTkdkdVF4SGFjYUJOWVE5K0kwMEdjZ0xTQ25NVlVYeGVwaDMzbVhLRkVvUmUvUUwybjNTQzFYUVpUUXJiR3RoT2RnYy9qcjJJQWNwdmoxVTNVQTR4RmxiajRqWmZISDA0WDJwajZqUnhLdFp0RGVtdlNadVRzKzVTWHVTTWYxZ3dOZloyYUoxcVBtSzhTdzBkWERZc3FLYXc0NFY3a0t0OXQ0RFlRQU1meE5vY3lUbHI5ZVZVMUdnUXBKd2RQU2RrT1RjVkFJUmdhblgxTk4rZCtHb3Y1RGNqYVYxU3EzWW9XL25JalN4VXptRUlKWWR3bXZVZmNGWVRWNzFZV1BIaElTUTVMUUNpbytmTjdxTDB6cDNYVENqQVhCMFZGR1NFOEdCY1VvdlhpbS9LTmJBS0JTT1RCckRBVVk5SEcwVFJrSUd2WlQzdXJkdnh1WE10c1o0S3kyNDlBSUl5dTBPblJZM0cyaDFUTWVkQkhqUGZUKzFMdmdiUXIvZTVUSytxdXBPSU96eFd6dkp2OG13NDBlcVREMnFzWGhrT3cwUTVDNTFhN2p0MXhiZEFIMGYwbU9iWHN3MndERU84YmhGQURibW5KREMwNzdOTFRPRTZjdjF3dmxBZ0pCZWZ2YVZORUFmMUZtL1dQMzB1UkluT29yeGU1aXpGcGI2OEFpV1JVYjlkWE9UYzgzaVBVeGxuODNFSTd1cUtzOGdZQnc0VVF3dHJLdzNiUGwzQXVyN01KZkJic3pHWmRYWnRHV3Zta3VWTVJOVEMrcGU2N1lMckRNL1YvUFg3c2R2Y3JOVGZXSEdYWFBLdFRvZVJKRmNBYXJMdEl5NnBZdkRKcWZONkhIQUttaFM2TmtGTDF5em8wVzZ2bjR0cGZwaUk4TjRrUzRaNUFmOGMvVkRPOWRYMmJwcmxGRUdqNldlcXRMOW02WWhEbVErRXZsM3NjWkhVTVo2d1J5MHYrYk43TFA5QjZtTE5RZ1ZVZ04vbUVLRGFVMDRKcml2a0o4RmQxNGExSVhGSG9ZRG9lUUl3RGgvb3JwZUptSmQvTnczSk5OY0xUYmxtakllYU5RUjVuWTRRNlFUOG1hMFk3b0EzUTRaclpLMDYvTXRDWVIrdXRMZVpib2xvNUVYOGVVeUJrdGRSa2RiMDA1V05HbFAzZDRiSktkSjUxdmkwSTVZVWJQejIwTTBOM2dCRnk0Y1phd0hwckFsWUo3bXNyQ2xEdUphVk52MFZ6V0FpRDVMb2NhSUZ0WGNzT25QdWRvK3h3bHVYTnhxdE1CeVdUWWNBbFFzdmxjOGFrdVFqblBXbkI3RjdWR3R6L3FybCtucWRnVURpUE9qTTlnKzJmcjNqL1ZsS01zUjQ1QU9TMlJLUEczU0dobXZUSUVEOG4wTnFpUE94UUVaK2d6bng3d0VSWXptZnJyVjV3eXBIbHcyU29iZytKM0NBdGFad1VnS1JkVjg2ZFpsZHBxVjRyNUVTcUM4SFZCSnhpNHVpNGFZSkI0Sml0dTA3SGNRWFE1aENFcXdmTG8yTTZ3aEdXbXFUb1ZTcG4va0NHcjFLM1lqdjBPOGJVWUdPclF2TithTGRFdTgwTmo5bkx1dFlYakd5Y3paLzZyYjg2OHdaZjB2ZDM3WkVDTG0vT2F5YktucVRRM1Zrd1hLNGM2QnVLOXM0OFFzOHpZL1ZMbE9RcFBGTUpBaDkxaUFaUmNscFBaVzZlYldpcC9mQ1pGaGtIVVA2UlNuMlVmYURSdUxjQ0Vpb01DZ2M0N0kyRzROYk8vSDlyWm5BUFRZNTlWc3Iwazc5T2QrUDhLaDVoUm9GSFJESUIyRVZIOVp5U3FzTmZZY3AyUnZyUlc5Nkk4MUVqWHVjY25GZzcyYXhWZlNvZ1Y4bHEyaG5qNnZWcXQ4UEdrYmt3OW85MkNOa2hIUlMydDI0aERoQ2pNVGtGcW95VmYzaWU0eXJBK28yNE5lamxHYlBqcFl3MW9iN1lrMUYrTmg0dE8yVnBOTUdUYndtMTJBb0V0dHFjLzRNOVpHaS9uUlB2WGdNYUJqclFVbmRkOU5oQTNNRzg3VDlZN0NUeDMwSDluYjI2YXFVRjB4OGRWd0k3RjRLV0tEREVYVU42Z2tBbEdhcjhWclp5QU9YajJ6c0RNSGFCUERKdkV5WUtMbXRkWi9WS2gxWEpMQktMVG44REtWQ1VKQ3JxbElyOS9NV2ZvTEdVVHB2UGdWY0FGRUtxNk1JeXZxMFNCc1VGZUFIVFZVZXE5OUVwNU5WK3VYeGZWRU9aZXNtRmpQUldabUhidll4WmNRem5aaW9kbEtZOFFsOGdRajlEemo0M2Myc0hURnQ3aGVmbDBkcHhLY3VHajJwZz09.E5qdN83CY-h8LTWtTHVpaYYewnYNvmNewovXLPMVkEY",
        "content-type": "application/json",
    }
    payload = {
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "branch": "17",
        "record": 100000,
        "page": 1,
        "data": "",
        "organization": ""
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print("✅ Traffic data fetched successfully.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch traffic data: {e}")
        return None


def _parse_month_year(invoice_date: str):
    """Ekstrak nama bulan (Indonesia) dan tahun dari string tanggal 'dd-mm-YYYY HH:MM'."""
    if not invoice_date:
        return "", ""
    try:
        dt = datetime.strptime(invoice_date, "%d-%m-%Y %H:%M")
        bulan = dt.strftime("%B")
        tahun = dt.strftime("%Y")
        return bulan, tahun
    except Exception:
        return "", ""


def build_summary_rows(data):
    """
    2) Bentuk summary minimal sesuai kebutuhan trafiksby.html.
       Hanya sisakan kolom yang dipakai di dashboard agar CSV kecil dan cepat.

    Kolom yang dipertahankan:
    - no_pkk, no_pkk_inaportnet
    - location, shipping_type, package_type, vessel_type
    - grt dan gt (salah satu boleh kosong, trafiksby handle keduanya)
    - bulan, tahun (turunan dari invoice_date)
    - moorage_revenue, pilotage_revenue, towage_revenue
    """
    rows = []
    if not data or not isinstance(data, dict):
        return rows

    recs = (
        data.get("data", {}).get("dataRec", [])
        if isinstance(data.get("data", {}), dict)
        else []
    )

    for r in recs:
        invoice_date = r.get("invoice_date", "")
        bulan, tahun = _parse_month_year(invoice_date)

        # Ambil nilai GRT/GT sebagai string apa adanya; JS akan parse angka
        grt_val = r.get("grt", "")
        gt_val = r.get("gt", "")

        # Filter: hanya baris yang relevan (punya salah satu identitas kunjungan)
        no_pkk = (r.get("no_pkk") or "").strip()
        no_pkk_inaport = (r.get("no_pkk_inaportnet") or "").strip()
        if not (no_pkk or no_pkk_inaport):
            continue

        rows.append({
            "no_pkk": no_pkk,
            "no_pkk_inaportnet": no_pkk_inaport,
            "location": (r.get("location") or "").strip(),
            "shipping_type": (r.get("shipping_type") or "").strip(),
            "package_type": (r.get("package_type") or "").strip(),
            "vessel_type": (r.get("vessel_type") or "").strip(),
            "grt": grt_val,
            "gt": gt_val,
            "bulan": bulan,
            "tahun": tahun,
            # revenue fields as-is (string); dashboard JS will parse currency/number
            "moorage_revenue": r.get("moorage_revenue", ""),
            "pilotage_revenue": r.get("pilotage_revenue", ""),
            "towage_revenue": r.get("towage_revenue", ""),
        })

    return rows

def save_summary_to_csv(rows, filename="trafik.csv"):
    """3) Simpan summary ke CSV dan 4) tidak menyimpan raw data."""
    headers = [
        "no_pkk",
        "no_pkk_inaportnet",
        "location",
        "shipping_type",
        "package_type",
        "vessel_type",
        "grt",
        "gt",
        "bulan",
        "tahun",
        "moorage_revenue",
        "pilotage_revenue",
        "towage_revenue",
    ]
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for r in rows:
                # pastikan hanya header yang ditulis
                w.writerow({k: r.get(k, "") for k in headers})
        print(f"✅ Summary saved to {filename} ({len(rows)} rows).")
    except Exception as e:
        print(f"❌ Failed to save summary CSV: {e}")

if __name__ == "__main__":
    # 1) Scrap data
    data = fetch_traffic_data()
    if not data:
        raise SystemExit(1)

    # 2) Bangun summary minimal untuk dashboard
    summary_rows = build_summary_rows(data)

    # 3) Simpan summary ke trafik.csv
    save_summary_to_csv(summary_rows, filename="trafik.csv")

    # 4) Hapus data scrap (di memori) — tidak disimpan ke file apa pun
    del data

