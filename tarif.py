import os
import csv
import time
import requests
from typing import Any, Dict, List, Tuple

BASE_URL = "https://phinnisi.pelindo.co.id:9021/api/master-tarif/mst-trf-tug"
# Tambahan: endpoint Pandu (Guide)
GUIDE_URL = "https://phinnisi.pelindo.co.id:9021/api/master-tarif/mst-trf-guide"
# Tambah: endpoint Kepil
KEPIL_URL = "https://phinnisi.pelindo.co.id:9021/api/master-tarif/mst-trf-kepil"
# Tambah: endpoint Mooring (Tambat)
MOORING_URL = "https://phinnisi.pelindo.co.id:9021/api/master-tarif/mst-trf-mooring"

# Default token taken from the provided request. Can be overridden by env TARIF_ACCESS_TOKEN.
DEFAULT_ACCESS_TOKEN = (
    "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMTh0K0ZycFNMU0ZhNVMxdnVOcU5CcE5YS0h6UktsVVVpVkpDcmNSRWN0N0hFS3d3WlVrOWwrbkFhZ3gxVEZ4ajRPckVPNzBveFhieFVCZW5VQzRZSDV6bVVBKzhsUGtoaDdjZVZJaUxISlMxWDVKRjhQSDNMWXNYY3NrcHFWSmRNVE5lZ1hqVTJEY1gvZTZoekhrZHJZRE1tWHJKazJJV1MwbWhGRHdMdWpSdWlwWW93V0JyNFlwMEtFaTFZdU5RZU96blNOQjJ5Z3o2dU1McU93YmhTdmE3cTJCdU9JVmpVVTVJNDhWV2hTaFZLUlZPZmhrQlpsVy9FR0JhUlBBYkxpVVJkUWxJOG42T2Z1eTFXeHNaNGNaR2NkQUpDc3hpZkhzVVVVOHJkQ0FrbHlXRHlZYktZRU9OVzZBaTRQejRnbWtJSEYydTFUQVhpbjc4N283YVpGVS9YKzEwOWNzQVloWDhqaHB3VUI0YzVTVXVkWEJQOXlQU0p1S2pOK0Y1L1dDUVFMYlRGdGVFRjJ0cnlGMWF3cnZPaHNnYzFFK1J0RlowRDl4V1JGYzFrUTZQVktyR3VmMnRPUVUzSEVNdlN3MzJwSDZvUXU3NUVQNXpXaC9ONVVIZkxJTWNuVW5qQnArVkM5c2NQM1RnRk14V3FpMUN3elRialJmNlBsWnR6VTJXRGQ3K1pwTDRWc1JndTlHTXJpM0l4ais3MUFtREViSm1LOUZPYmJ0MzVVNXJEYUt1KzBQMVFxVlNIYURQSnVvL05hQUdYcDlvSzJwV3haWThUZWFLNzhQSFBKYSs3L0RFNnRwTzg5eDlQT1FGSS9WbUJ6d3VtM1dQTEdBeEtyQmxDYmdYYXJEN3loNFpuRkRNVGJ6ODdKVGh6bisyYVpsenkyaU9jWGdPTHcwRitwbHpudkdIRzhudGpVcG51a3NFSy90bytxZk0wTkhnZThiZmtEa2REb2MwT3oyN3lqMFBwMXdvYU1IeGxBcC80UngyaWVmbCtERWdXRS9hK090WElGMXJOWW1rQ0dERFZQSm9ZVDZrSTJsNGthZkdtVlczY0JhNkthM1ZFcVZ1dXVIV3ZjbFloMlA5cWJUbWVwMVVOeXdDM1JyNHZXZzNUbG1aT1Y5ZUt1R3BhYkJ1ZlNicGJuQmQ2RXlxamlSVmJZV05wOW93WXl2dEswaFkzMFpOdXB6K2NBZ1MvMTF3MWV0dHZyS3lXYllmM3d3S2FuM0tuTzk5bHNTbzgzTy9CcUpSMnY4V1lZc2k4MmEzbndUbm9rdFJWSEh3QUVYQkR0d04vZWhndGpmTzhqai9RWWlXck1PS2c3VGhZU3hUY0hlNTN4VCs4RzdBVTVxczVIOFp5dGw3dkpSNHIrZUVhTXZFWGJUVncyWks3ZTZRN05OVmZlSlZhZjgzUVEwSXVSVis3ZVVlZURFZVVGT2hYbkU5YjBhZXF6enNnMGFnN0lZZ21aYXJOMEduTUFwTU5BRDNyVDhiU1NXRjNDc0wyelFnY2xVdENnY1RvbGh1M1g0WDhDd3RkNEdJTmtob0Z2R1hnRnlQanRna0Z4ZXF2elZDdGQrTWQwWmxLUzZtRFRZc0p3aWJzSHM3NHFqOFA5Z29qTWN2cm9mWnkycnpQUmhSS3J6eWZPVEUvam9CSTdGWkpyRngwVjVtMGs0RUsvdWZCVmNtQWlPaFNxZ2VORVhUTlZvYitrU2FVeUY5RHczT3ZxNTk2dUc1Nnk3K0RqMUZTVHljcHd6VWxwT2JBdUg2SmU0dmhmbjhkU0tMVjFTWndiaHFWR2lLRFJkNC9IaTBVQUR6aDBCN2txWGpwS0VUY3A3S1NqNm5jbzZSalZJQkJ1MmNLeVJpT2hpcHdSNXhKd2g3MitFVWhiUW1OT2lweUFiWmZrRG5YOHpyYWtNNkxQSXY0M0I4bzVQa0k0Z2kyc1NQcVN3U3owNGFNOFZ0VytSRzc1a2FzTDB6ZUxiRjIxdk0rZHBUcjBiUTZmTDVTSTdWUHprR2NyTTF0OWEvTzFFOTh5UlBrK3NHbHJ4NHIwTkNxbVppdkFZMDc0SHVJNERMVElZUC9FbUo4eU9rbktPRnU3YmNKVmdxR25XNmtMUXNOYjVWZHBlWHJjdkZUQk45dVg2em5nTDhpNURMTTZoR1p1bFVIdDliT1pIRkJtQk8waEozMmhlcTB6SGc4c0dQNXZrSDRFamsvU1BKRExmRkhBSVNGRzNBKzM2WWxKSWdUbUNZS0NSaEUxRjhNQ01waTh4cUgzbk5YTFBQWVRzdDl1amNOMWJUVjRqN1pWRzNNblQ0Z2s2cndjcDhOUTlMRm9QRWsvMG1nU2hjZHVsSDZvb29uVGc2YWwrVGc4NUlkdmZheGNlSDhYQTIwbUs5UkdHVzdLNmxGZ3pYSnhGVUdCUHhRU2JHai9FcmRxVU9vWnUvVHRkcnhuRU1ycVRGUU03MFVzRklhbXF3OHN6clN1cEYzeFErY3ZxOEpPKzZYZTk0UnVrcEw1R1FqSTcrZURxTTVxU2poWU5yU2I0dGxNd0ptSlRsSWY5L0tZOU8vMTdpWmJKQjNYSTh6RjZiMU1RZU1RNEorSnREOElKazl5dDYxbzRFT0ZLZFRWUWt3T204YmI4K1JwVjlHelV3R3lPV1RrODR6MXdCVFZzUlR5K01vVDNHR0F4UFRGb0E5ZW81YmVDUkxRdCtWeUVEbVg1ODV3Q3ppMFlpNXVkaVkwdDFRcnJtbkwwbjdOdFNrN2hVb3BnVThMdnBWS1BIVkl5L3hXMDFCT0xNcHE5Y2V3bU1lNHRPTUdLNmJza1N1UWR3RUJCcEZ1SkE0SDVkcWRLMkxZeUhrbkd3T0lOR05vRlJhaXhPVW5tblZqWjdnRkpCaVNhTlVCc1lQL1dnMjFGUEttTEtidWhOMnk3MEVYS3pqditNSGV4SHVaY2NhUmxwRmVxOTZ5a1BzMWpqRGYzaVJVMDJ3NmwrTHVXemkzSVI5N2FUajB2bUF6MmxGNkc5UG5qaE9BamNUYjZQTGV2UHczdEZNUCtoMUFLaGY1WHlJK1hCTlRFRDd1RmdXNTBIcEFrZ3lzK0ZJdnlnYlpFZC95Q3FZeVFmRlI0WCt4RDRPTCtsWGdiQnRjMG9UaGpoMWVvaTY2aXd1dTFIeSsvWGkxNm93emwzUm5XSmtYM0c2ZXI5SWw0OU9CTm4vODZuR1grNGk0ZHlqb2g0dkJzNVFuVmg3NWRpNDhreTF1ak5iemF3RkltKzF4TFRqaWxqQUhCMmFGd1NKSVA3M1pUQ0lSTXZQczllbVpZL3ZNMjJuelZLc2NjM3JXRENGbVA4UT09.Lwn6dbxuGVLSLSky29PmCWmK7jLFgKCzJnpx8HeCQxA"
)

def _build_headers() -> Dict[str, str]:
    token = os.getenv("TARIF_ACCESS_TOKEN", DEFAULT_ACCESS_TOKEN).strip()
    sub_branch_b64 = os.getenv("SUB_BRANCH_B64", "MTc=").strip()
    return {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh) Python Requests Scraper",
        "access-token": token,
        "sub-branch": sub_branch_b64,
        "origin": "https://phinnisi.pelindo.co.id",
        "referer": "https://phinnisi.pelindo.co.id/",
        "connection": "keep-alive",
    }

def _extract_records(payload: Any) -> List[Dict[str, Any]]:
    # Try common shapes: list, {data:[...]}, {data:{dataRec:[...]}}
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        d = payload.get("data")
        if isinstance(d, list):
            return [x for x in d if isinstance(x, dict)]
        if isinstance(d, dict):
            if isinstance(d.get("dataRec"), list):
                return [x for x in d.get("dataRec") if isinstance(x, dict)]
            if isinstance(d.get("rows"), list):
                return [x for x in d.get("rows") if isinstance(x, dict)]
        if isinstance(payload.get("rows"), list):
            return [x for x in payload.get("rows") if isinstance(x, dict)]
        if isinstance(payload.get("dataRec"), list):
            return [x for x in payload.get("dataRec") if isinstance(x, dict)]
    return []

def _extract_pagination(payload: Any) -> Tuple[int, int]:
    """
    Return (page, total_pages) if available, else (0, 0).
    Looks for common keys: page/totalPage or page/total_page.
    """
    if not isinstance(payload, dict):
        return 0, 0
    d = payload.get("data")
    src = d if isinstance(d, dict) else payload
    page = src.get("page") or src.get("current_page") or 0
    total_pages = src.get("totalPage") or src.get("total_page") or 0
    try:
        return int(page), int(total_pages)
    except Exception:
        return 0, 0

# Generic fetcher agar bisa dipakai untuk Tug dan Pandu
def _fetch_tarif(base_url: str, record: int = 500, data: str = "", max_pages: int = 1000, delay: float = 0.2) -> List[Dict[str, Any]]:
    headers = _build_headers()
    all_rows: List[Dict[str, Any]] = []
    page = 1
    while page <= max_pages:
        params = {"page": page, "record": record, "data": data}
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=60)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException as e:
            print(f"❌ Request failed on page {page}: {e}")
            break

        rows = _extract_records(payload)
        if not rows:
            print(f"ℹ️ No records on page {page}, stopping.")
            break

        all_rows.extend(rows)
        cur_page, total_pages = _extract_pagination(payload)
        print(f"✅ Fetched page {page} with {len(rows)} records from {base_url.split('/')[-1]}. " +
              (f"(pagination {cur_page}/{total_pages})" if total_pages else ""))

        if total_pages and cur_page >= total_pages:
            break
        if len(rows) < record:
            break

        page += 1
        time.sleep(delay)
    print(f"✅ Total records fetched from {base_url.split('/')[-1]}: {len(all_rows)}")
    return all_rows

# Ubah fungsi Tug agar memakai generic fetcher
def fetch_tarif_tug(record: int = 500, data: str = "", max_pages: int = 1000, delay: float = 0.2) -> List[Dict[str, Any]]:
    return _fetch_tarif(BASE_URL, record=record, data=data, max_pages=max_pages, delay=delay)

# Tambah fungsi Pandu (Guide)
def fetch_tarif_guide(record: int = 500, data: str = "", max_pages: int = 1000, delay: float = 0.2) -> List[Dict[str, Any]]:
    return _fetch_tarif(GUIDE_URL, record=record, data=data, max_pages=max_pages, delay=delay)

# Tambah: fungsi Kepil
def fetch_tarif_kepil(record: int = 500, data: str = "", max_pages: int = 1000, delay: float = 0.2) -> List[Dict[str, Any]]:
    return _fetch_tarif(KEPIL_URL, record=record, data=data, max_pages=max_pages, delay=delay)

# Tambah: fungsi Mooring (Tambat)
def fetch_tarif_mooring(record: int = 500, data: str = "", max_pages: int = 1000, delay: float = 0.2) -> List[Dict[str, Any]]:
    return _fetch_tarif(MOORING_URL, record=record, data=data, max_pages=max_pages, delay=delay)

def save_to_csv(rows: List[Dict[str, Any]], filename: str = "tarif_tug.csv") -> None:
    if not rows:
        print("ℹ️ No data to save.")
        return
    # Build dynamic headers (union of keys), sorted for stability
    headers: List[str] = sorted({k for r in rows for k in r.keys()})
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in headers})
        print(f"✅ Saved {len(rows)} rows to {filename}")
    except Exception as e:
        print(f"❌ Failed to save CSV: {e}")

if __name__ == "__main__":
    # Tug (Tunda)
    record = int(os.getenv("TARIF_RECORD", "500"))
    data = os.getenv("TARIF_QUERY", "")
    out_file = os.getenv("TARIF_OUT", "tarif_tug.csv")
    rows = fetch_tarif_tug(record=record, data=data)
    save_to_csv(rows, filename=out_file)

    # Pandu (Guide)
    pandu_record = int(os.getenv("TARIF_PANDU_RECORD", "500"))
    pandu_data = os.getenv("TARIF_PANDU_QUERY", "")
    pandu_out = os.getenv("TARIF_PANDU_OUT", "tarifpandu.csv")
    rows_pandu = fetch_tarif_guide(record=pandu_record, data=pandu_data)
    save_to_csv(rows_pandu, filename=pandu_out)

    # Kepil
    kepil_record = int(os.getenv("TARIF_KEPIL_RECORD", "500"))
    kepil_data = os.getenv("TARIF_KEPIL_QUERY", "")
    kepil_out = os.getenv("TARIF_KEPIL_OUT", "tarifkepil.csv")
    rows_kepil = fetch_tarif_kepil(record=kepil_record, data=kepil_data)
    save_to_csv(rows_kepil, filename=kepil_out)

    # Tambat (Mooring)
    tambat_record = int(os.getenv("TARIF_TAMBAT_RECORD", "500"))
    tambat_data = os.getenv("TARIF_TAMBAT_QUERY", "")
    tambat_out = os.getenv("TARIF_TAMBAT_OUT", "tariftambat.csv")
    rows_tambat = fetch_tarif_mooring(record=tambat_record, data=tambat_data)
    save_to_csv(rows_tambat, filename=tambat_out)
