import requests
import csv
import brotli
import json

def fetch_data(base_url, headers, params):
    """
    Fetch data from the API.

    :param base_url: The API base URL.
    :param headers: The request headers.
    :param params: The request parameters.
    :return: Parsed JSON data or None if an error occurs.
    """
    try:
        response = requests.get(base_url, headers=headers, params=params)
        print(f"HTTP Status Code: {response.status_code}")
        response.raise_for_status()

        # Handle Brotli compression if Content-Encoding is 'br'
        if response.headers.get("Content-Encoding") == "br":
            try:
                decompressed_content = brotli.decompress(response.content)
            except brotli.error as e:
                print(f"⚠️ Brotli decompression failed: {e}. Falling back to raw content.")
                decompressed_content = response.content
        else:
            decompressed_content = response.content

        # Parse JSON data
        return json.loads(decompressed_content.decode("utf-8"))
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return None

def save_to_csv(data, output_file):
    """
    Save the given data to a CSV file.

    :param data: List of dictionaries to save.
    :param output_file: Path to the output CSV file.
    """
    if not data:
        print("⚠️ No data to save.")
        return

    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Data successfully saved to {output_file}")
    except Exception as e:
        print(f"❌ Failed to save data to CSV: {e}")

def main():
    """
    Fetch data from the API and save it to a CSV file.
    """
    base_url = "https://phinnisi.pelindo.co.id:9021/api/monitoring/ina-spb"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
        "access-token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMS8xNHN2ZVdlUWxQeEtmSTRiZWczTnZvaDY4QUZmYlZQUmpQRHpLaVpFWUx1SEhkMXRScHpubm83cldCaVNPNUtlN2FhTXpQRG9NTTlURUpDK1F3WlNscUFWVjlycngwRlQreXVza0I0UUxVdTc3R0grNlpYaGhjTy9aYkt3L05CL2h5eGFQTmxQOWY1c0xKcnBrMC9GSUFGM0J5cmlmSlhKT2pJcnQ1UjFrbVZLdHNWRXV1VWFKYTA5YklRQ0hsWHFNSlJkYmE5Q0d2aTdkSnRzZW50aEUxUlNGR3R2UkRKU3kyOTFvRGVtdCtkOE42K1ZHR1F1YU9NQ2dSK1c1RmdSZ0VqYzRQd0pOU2tDQk5oRFhPMTkwclZIU2thdGtOZ3hLZU13N0REem13bFdwVDlYU2t1QldHOThIdStSbCtFblZzcFJtbVFOdG05WnM3eUlOTWw4UFJ5UTk1dVRyRmRQeWdLRjdjSVRaakpCN0dpYjdPSzFKejBhTWRiSTFhR0hMSDdycktxRVRYckF1elJuYnFkZDJJTEdRWWtIZjE5bmFiVkpJT0VtRTMrNTloeGMyNHl0UXhqRmQ5R0MzaFV1T0xJczdoTHBmVUM0WFVvZjArVGxEK1dBMW9QTXg0WkdmeXFXWUNtRFBlZFVLaG1JbHl2ekxhb0NzZENyMVRZclhTSUNrRnQxWThDRS9PeFlzQXhCdGdCcUdOSTllQ3d1QVROdmZWSEtwd3IrMmFYNHcrMHMyRWJCU0Z5SHU3TGhPVTJ6d2FBNnMxa0FnVlFORGQ4dTNubHhEcS91a1JFVVMzVWhia3ZmOXZnMGY1TFBiOXorS1JuRWllUkhad1JEYjRSYjBiVUJEeTJGTDBEd1BSZmhRS0wweDl2MXJTQ1JJQVFJM3ZxVW1kYzcvSUdRbXNUbmRZNUUxbm1wVmhwRXRJVjhYZEcwenduRzQ0emhuZGswK2FybVRSTkdkdVF4SGFjYUJOWVE5K0kwMEdjZ0xTQ25NVlVYeGVwaDMzbVhLRkVvUmUvUUwybjNTQzFYUVpUUXJiR3RoT2RnYy9qcjJJQWNwdmoxVTNVQTR4RmxiajRqWmZISDA0WDJwajZqUnhLdFp0RGVtdlNadVRzKzVTWHVTTWYxZ3dOZloyYUoxcVBtSzhTdzBkWERZc3FLYXc0NFY3a0t0OXQ0RFlRQU1meE5vY3lUbHI5ZVZVMUdnUXBKd2RQU2RrT1RjVkFJUmdhblgxTk4rZCtHb3Y1RGNqYVYxU3EzWW9XL25JalN4VXptRUlKWWR3bXZVZmNGWVRWNzFZV1BIaElTUTVMUUNpbytmTjdxTDB6cDNYVENqQVhCMFZGR1NFOEdCY1VvdlhpbS9LTmJBS0JTT1RCckRBVVk5SEcwVFJrSUd2WlQzdXJkdnh1WE10c1o0S3kyNDlBSUl5dTBPblJZM0cyaDFUTWVkQkhqUGZUKzFMdmdiUXIvZTVUSytxdXBPSU96eFd6dkp2OG13NDBlcVREMnFzWGhrT3cwUTVDNTFhN2p0MXhiZEFIMGYwbU9iWHN3MndERU84YmhGQURibW5KREMwNzdOTFRPRTZjdjF3dmxBZ0pCZWZ2YVZORUFmMUZtL1dQMzB1UkluT29yeGU1aXpGcGI2OEFpV1JVYjlkWE9UYzgzaVBVeGxuODNFSTd1cUtzOGdZQnc0VVF3dHJLdzNiUGwzQXVyN01KZkJic3pHWmRYWnRHV3Zta3VWTVJOVEMrcGU2N1lMckRNL1YvUFg3c2R2Y3JOVGZXSEdYWFBLdFRvZVJKRmNBYXJMdEl5NnBZdkRKcWZONkhIQUttaFM2TmtGTDF5em8wVzZ2bjR0cGZwaUk4TjRrUzRaNUFmOGMvVkRPOWRYMmJwcmxGRUdqNldlcXRMOW02WWhEbVErRXZsM3NjWkhVTVo2d1J5MHYrYk43TFA5QjZtTE5RZ1ZVZ04vbUVLRGFVMDRKcml2a0o4RmQxNGExSVhGSG9ZRG9lUUl3RGgvb3JwZUptSmQvTnczSk5OY0xUYmxtakllYU5RUjVuWTRRNlFUOG1hMFk3b0EzUTRaclpLMDYvTXRDWVIrdXRMZVpib2xvNUVYOGVVeUJrdGRSa2RiMDA1V05HbFAzZDRiSktkSjUxdmkwSTVZVWJQejIwTTBOM2dCRnk0Y1phd0hwckFsWUo3bXNyQ2xEdUphVk52MFZ6V0FpRDVMb2NhSUZ0WGNzT25QdWRvK3h3bHVYTnhxdE1CeVdUWWNBbFFzdmxjOGFrdVFqblBXbkI3RjdWR3R6L3FybCtucWRnVURpUE9qTTlnKzJmcjNqL1ZsS01zUjQ1QU9TMlJLUEczU0dobXZUSUVEOG4wTnFpUE94UUVaK2d6bng3d0VSWXptZnJyVjV3eXBIbHcyU29iZytKM0NBdGFad1VnS1JkVjg2ZFpsZHBxVjRyNUVTcUM4SFZCSnhpNHVpNGFZSkI0Sml0dTA3SGNRWFE1aENFcXdmTG8yTTZ3aEdXbXFUb1ZTcG4va0NHcjFLM1lqdjBPOGJVWUdPclF2TithTGRFdTgwTmo5bkx1dFlYakd5Y3paLzZyYjg2OHdaZjB2ZDM3WkVDTG0vT2F5YktucVRRM1Zrd1hLNGM2QnVLOXM0OFFzOHpZL1ZMbE9RcFBGTUpBaDkxaUFaUmNscFBaVzZlYldpcC9mQ1pGaGtIVVA2UlNuMlVmYURSdUxjQ0Vpb01DZ2M0N0kyRzROYk8vSDlyWm5BUFRZNTlWc3Iwazc5T2QrUDhLaDVoUm9GSFJESUIyRVZIOVp5U3FzTmZZY3AyUnZyUlc5Nkk4MUVqWHVjY25GZzcyYXhWZlNvZ1Y4bHEyaG5qNnZWcXQ4UEdrYmt3OW85MkNOa2hIUlMydDI0aERoQ2pNVGtGcW95VmYzaWU0eXJBK28yNE5lamxHYlBqcFl3MW9iN1lrMUYrTmg0dE8yVnBOTUdUYndtMTJBb0V0dHFjLzRNOVpHaS9uUlB2WGdNYUJqclFVbmRkOU5oQTNNRzg3VDlZN0NUeDMwSDluYjI2YXFVRjB4OGRWd0k3RjRLV0tEREVYVU42Z2tBbEdhcjhWclp5QU9YajJ6c0RNSGFCUERKdkV5WUtMbXRkWi9WS2gxWEpMQktMVG44REtWQ1VKQ3JxbElyOS9NV2ZvTEdVVHB2UGdWY0FGRUtxNk1JeXZxMFNCc1VGZUFIVFZVZXE5OUVwNU5WK3VYeGZWRU9aZXNtRmpQUldabUhidll4WmNRem5aaW9kbEtZOFFsOGdRajlEemo0M2Myc0hURnQ3aGVmbDBkcHhLY3VHajJwZz09.E5qdN83CY-h8LTWtTHVpaYYewnYNvmNewovXLPMVkEY"
    }
    params = {
        "data": "",
        "record": 100000,
        "page": 1,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "is_success": ""
    }

    # Fetch data from the API
    response = fetch_data(base_url, headers, params)
    if response and "data" in response and "dataRec" in response["data"]:
        records = response["data"]["dataRec"]
        output_file = "/Users/hadipurwana/Library/CloudStorage/GoogleDrive-purwana.hadi@gmail.com/My Drive/PYTHON/PHINNISI SCRAP/spb.csv"
        save_to_csv(records, output_file)
    else:
        print("⚠️ No data found in the API response.")

if __name__ == "__main__":
    main()
