import requests
import csv
from datetime import datetime

def fetch_traffic_data():
    """
    Fetch traffic data from the API.
    """
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

def save_traffic_data_to_csv(data, filename="trafik.csv"):
    """
    Save traffic data to a CSV file with selected columns.
    """
    # Debugging: Print the structure of the data
    print("Debugging: Data received for saving:", data)

    if not data or "data" not in data or "dataRec" not in data["data"] or not isinstance(data["data"]["dataRec"], list) or not data["data"]["dataRec"]:
        print("❌ No valid data to save.")
        return

    # Define the columns to extract
    selected_columns = [
        "no_pkk", "no_pkk_inaportnet", "vessel", "agent", "loa", "grt",
        "location", "lokasi_awal", "shipping_type", "jenis_bendera", "vessel_type",
        "package_type", "flag", "port_of_origin", "destination_port", "next_port",
        "last_port", "moorage_revenue", "pilotage_revenue", "towage_revenue",
        "mooring_boat_revenue", "invoice_date", "bulan", "tahun"
    ]

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(selected_columns)
            # Write rows with selected columns
            for row in data["data"]["dataRec"]:
                # Extract the month and year from invoice_date
                invoice_date = row.get("invoice_date", "")
                bulan = ""
                tahun = ""
                if invoice_date:
                    try:
                        # Handle multiple date formats
                        parsed_date = datetime.strptime(invoice_date, "%d-%m-%Y %H:%M")
                        bulan = parsed_date.strftime("%B")
                        tahun = parsed_date.strftime("%Y")
                    except ValueError:
                        print(f"❌ Invalid date format for invoice_date: {invoice_date}")
                writer.writerow([row.get(col, "") if col not in ["bulan", "tahun"] else (bulan if col == "bulan" else tahun) for col in selected_columns])
        print(f"✅ Traffic data saved to {filename}.")
    except Exception as e:
        print(f"❌ Failed to save traffic data: {e}")

if __name__ == "__main__":
    traffic_data = fetch_traffic_data()
    if (traffic_data):
        print("Fetched data:", traffic_data)  # Debugging line
        save_traffic_data_to_csv(traffic_data)
