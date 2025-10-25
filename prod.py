import requests
import json
import pandas as pd

# URL API
url = "https://phinnisi.pelindo.co.id:9014/api/reporting/produksi/list"

# Headers berdasarkan request yang diberikan
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
    "access-token": "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMStjRHpxUlZQaDQzL2RRSEZUb2VmUHM4TTdHcE9vSjZUNkpJQkRqelFyTitmd245QTVNOTVKTGdOV3RVUDBOTGQvOGxuNytuWm9ackQvMUdmd1BZdlF6MXgxcHVkeWRvNWkwQ0dZT1ZHWUYwcno0YlE3R2ZjVXEwTGE2OGcyNit0Vmc3dTlSWUtmcUV1YS9iaUwyaG9aVk96LzYvMmI0dG96ZnhJOFlUVnB1VTErMDJqVmcrQzlZL2NJVUh1UXFZQ2dYL3N0ejdZQjVYRmgvNTJOMUJCTGhwMFh2TW1sam9xbHhLanZrZ09rMkprcWtBM2lVZ1ZsNHRZTXlNVFNDUVpPcDFZK1crcEFwREpZbXVLNXpidWh3amFWbmRzdDVMQWZLeHFUZVJvVzBzcXdrWmE1NTJjamsyZHF5U2svZCtveVdudlBHQ0tMWUxHdWcxQXlNbkc0ZTRHaDk5MWY4amRwcGt2c01ZaHJWeUFuT29jbURVb3FzdWhicVBXZ1pHdFEzS0RINjFvRENqOGQ2TnROcGM2VStBOFRhQzVDZW1oNUVsMjRHWm1PcGJWM1dkcjNkR2l2QzcvcE1YZlhVV1hPcWUyaDl5RkVBVU9mS3pvNm1mcnVFRUZ1aHlaKzVGWnNHM1NuQSs0RUkzbWdxVDZIUFhhQkIwSTN1STVhNXJXR1dSQ2VHbjBEZzc2RCs2SHJSa28xZ1gyRURYdE04QmlEZ1lpckVPZVBJazlkNWtlcDE4NDI4R0JMeUlZN0NGZEcyYURjTlZNRGIvWXprZ2Ivb24vL0NCaUIrTElKNndhMWh1ZC82VU8xN2J0VkhWdGVHek5qVjREc0JLbEF0MmVPUmw2L0dpR29Id08rTU84MVd3Tis1MUFRN1ZUN2hFRGhUNDQ5T1JOZkZvb2xQTE9YL0dNRXFPNmJNZXFBWlVrYWFpcVQwWHNoZmFMQjEwZlJGaFBSSkc3bWJKMi9WVE1MZmIwQ2lEb0RVa2FIclZuWlpBcmRWT2RPRkNnYXp3dnAxckpibVNXY0h4VW1lL3ZWUHFHbDFBc0xiRzd5SXh0OWJNaUViaDdMc0tCREk5dXBScSswYXU5R0NRYUNKc2Q5UGpvYlBZSCtiYndLN1BGeXZKRDcvalVSd3dYTDRHc0dRaHdEK2RtUEZyc0p6TkM0ZmZoeFgraFBIVHA4WnFicFRqT1FtMk5yQnFsLzBpK3lHMjNLV1hGbExZclVzTU43dnZNd3JuY0QwOGd1QUt1THh6dm9yUHBuSGx2QUtuQi9CMXFyYk9Lc0szc0VlSmV0NUNhRTdZK0g5d1BNNis4TDB2dTlRWWsvVXZBRTJveUFTWVpCMXhQUFpSZTRVV1dNUitEYllvTnB5aWpvcDMrSlExbTYwMUVkTFExeFdXejRDNjdhODRRd0ttbEpBZGs3UzJWQlFwVEdXT0xvdHBWTDZXLzdvL01DSW1KSlE0OFlncGxEV3ErVmVPTzZqZ1o1Q3dzUWhmVWZzd0pwS045amlpZXFMcjRLUTRSeHdFNWx3bkdyR3V0ZXVNRTlqLzJFV21OYmVTTEhsRER2NmFwUmJ6L1hrRmZ6Y0FBSTZldlI0UkhZTkdRNzVtRXdKNnl0WDBmZ0xEK3V3ZnllQmQ3MWhDN05DVUx2dGxVelh0Wi9Dd0srRnlYdlJqU1UwNGRNZU1nTkVwbzM4TkhKNUlsN1V3RVYxUDVENVZFUGNoMUJRalhhZm1kZlhsOUM5dDdwOWVhZkJFcytqYkllNjJMY0V3T1VpQnptMlhBLzFwNC9Rc3ZYclZXSHJKcTBqdWEvbTBpcFp2UmRSTkpud2tkK3haRUxHSGVkckZqQUliNjUzSUxlTXl3T1Q3WGh6dXMyKzFPOS9KdnZpTGFTUnRGd2JkTkpEbFVPRU50akdqZ0VOSHNkUzhPZmRlMGJncmhXdnFqazZTY2dXTUpraDZ6M1M2L1ExaVY2bTVMYit5dFRhdHZPdW44REFJRkJWODVhaE8xOUMzdUNnamZzd0Nlb2xBaE12T2ltVkduT3JrZElGTWpvakRUL0JUSjdLbjdHeVA2b1UxekNzRVNnMDMrN3h4akIrZjNPSXhLTSs3ZVYyWStDenQ3ZXdRY3pPSCs0RGxJbEpkazdWaUpqTFN5V2JOaWhnQ1VFY1p0elZ1c0EzMHYyOGI4eEhJNFhEbkFkZWQwaUNEZUpyQ3JpMGNvM2hxTG5qWGI1TVFNM0tPVDdNZklwSi92M0p2S3BzUUFXNnY5OFZrZ3FHZjA1bktIMGMxRHpHMTQwelVaOFBKMFpmOE1WU1k3NTI2TEVXVmxxNXhVSE42dERSZVRsUDJQUzd2ait3S3BIUkxteTJTdkx6L1hQall0L0tQUGNKNXFIUjBXOWswbDF3ZGoxNkJyR2gycm5KVTNYMWpRU0h2YlcrS290LzRiV0N5UTdPUm5GYUZ0bm0wMGVLVm1NZ0dzeStqZnpGbkpwYkZDZ3hSemlOdkpxYW43V0ZSVkoyMUFvZkxqZ3Bkc096RzFkL2wrcDZlVWFIdllubzVMTmg0ZGU5eFZ5dEZXeFl6dHNPY1Ridlh5QUFiQnoybGEvMS9LNEpseUpTM05ydlZsd3ZyS1dHenRNTEhZL0pYUTJxaTZObktoYW5aaXN2M0VmdjFmK1NWU0RuSGxvaFhQZjF2cFMvNG4wa0tLUXo4UzFoYzFIam4zS1REa3B5K2dBdTRkMmpGK2hmcXo5VUJtMXJ3N283TFRUN1JjVEFaQnUvQ0FEZTJCdnBxc1FBM2Q0Z1E1WkJOcGt1TVFMQ3RHa3dpM2YzMVQwb0dFVXZEMkI3bUVyVDlJWC84Rm9SdkQ3ZVpYU0VLWFZmd1hIVjJHTXl1RUQxdGhzL2s2QzZpMUZWNEc3UzByN2M5MDFkSVh6ZDZZNll0bjFlTzVocG9aaXpQeGE3YVBBd1BnSXczcDZEUURNSWEzc3VWamw3QU42WlFsWEtNaUc1YUgyWWhvRmFwZHlxU0Q3dzlJMHFtc0xLNWdlQmpRbDBPVTlUV3hnd1Z5YUpuR3ZtYmllZjY2cHlpaGk4aXQzMEg3dDRabTBvZmZxdHlTc0NnNEVkc3VMVVVWWlF6NTZ1SWZ2SHREYUdwdWNFSHptVFgzaEtaOUZNZS8zWFNjOUZjZjNUVGUySG81dEVpNkJpYVNVM2czK3B4ZWxBalNPSVRKaS9QR2FlbW9NV2xhclM.GH50H0wFUiUReWRUQJzZ9aC2bf-BKQhIOQvtFbsvk1g",
    "connection": "keep-alive",
    "content-type": "application/json",
    "host": "phinnisi.pelindo.co.id:9014",
    "id-unit": "",
    "id-zone": "",
    "origin": "https://phinnisi.pelindo.co.id",
    "referer": "https://phinnisi.pelindo.co.id/",
    "sec-ch-ua": '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sub-branch": "MTQy,ODI=,NDc=,NTE=,NTI=,ODg=,ODc=,ODY=,Mzc=,NDA=,NTA=,NDg=,ODQ=,Mzg=,MzE=,NjM=,Mzk=,MTA0,MjA=,Mg==,MTEy,NA==,NQ==,Ng==,OQ==,MTA=,MTE=,MTI=,MTM=,MTQ=,MQ==,MTEx,MTEw,MTA2,MTA1,Mw==,NzU=,NzI=,NTg=,NjY=,MTAx,NjE=,ODE=,MjU=,NTQ=,ODM=,NzQ=,NzM=,NjI=,NTY=,NDk=,NDQ=,Njk=,Njg=,Mjk=,Mjc=,NzE=,MTc=,NTc=,NjU=,MTY=,MTA4,NjA=,NjQ=,MTk=,MTU=,MTg=,MjY=,MjQ=,MzM=,MzQ=,MzY=,NTM=,MTAz,NDU=,OTg=,OTA=,NzY=,Nzc=,OTM=,MjI=,MjM=,Mjg=,MzA=,MzU=,MzI=,NDE=,NDM=,ODA=,ODU=,NTU=,NTk=,MTAy,OTI=",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
}

# Payload untuk POST (kosong, sesuaikan jika perlu)
payload = {}

# Mengirim request POST
response = requests.post(url, headers=headers, json=payload)

# Mengecek status response
if response.status_code == 200:
    data = response.json()
    print("Data berhasil diambil:")
    print(json.dumps(data, indent=4))
    
    # Opsional: Simpan ke file JSON
    with open('prod_data.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Data disimpan ke prod_data.json")
    
    # Simpan data ke CSV
    if data.get("success") and data.get("data"):
        # Asumsikan data["data"] adalah list of dict
        if isinstance(data["data"], list):
            df = pd.DataFrame(data["data"])
            df.to_csv('prod.csv', index=False)
            print("Data disimpan ke prod.csv")
        else:
            print("Data bukan list, tidak bisa simpan ke CSV")
    else:
        print("Tidak ada data untuk disimpan ke CSV")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
