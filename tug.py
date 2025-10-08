import os
import sys
import json
import argparse
from typing import Any, Dict, List, Optional, Tuple

import requests
import pandas as pd


API_URL = "https://phinnisi.pelindo.co.id:9018/api/dashboard/tug-utilization/dashboard"

"""
Default settings you can edit below (or override via environment variables):
 - Env vars: TUG_TYPE, TUG_START_DATE, TUG_END_DATE, TUG_RECORD, TUG_PAGE, TUG_MAX_PAGES
"""
DEFAULT_TYPE = "invoice"
DEFAULT_START_DATE = "2025-01-01"
DEFAULT_END_DATE = "2025-12-31"
DEFAULT_RECORD = 100
DEFAULT_PAGE = 1
DEFAULT_MAX_PAGES = None  # set to an integer to limit pages


def _env_int(name: str, default: Optional[int]) -> Optional[int]:
    val = os.getenv(name)
    if val is None or val == "":
        return default
    try:
        return int(val)
    except Exception:
        return default


def resolve_defaults() -> Dict[str, Any]:
    return {
        "type": os.getenv("TUG_TYPE", DEFAULT_TYPE),
        "start_date": os.getenv("TUG_START_DATE", DEFAULT_START_DATE),
        "end_date": os.getenv("TUG_END_DATE", DEFAULT_END_DATE),
        "record": _env_int("TUG_RECORD", DEFAULT_RECORD),
        "page": _env_int("TUG_PAGE", DEFAULT_PAGE),
        "max_pages": _env_int("TUG_MAX_PAGES", DEFAULT_MAX_PAGES),
    }


def resolve_access_token() -> Optional[str]:
    return (
        os.getenv("PHINNISI_ACCESS_TOKEN_TUG")
        or os.getenv("PHINNISI_ACCESS_TOKEN")
        or os.getenv("ACCESS_TOKEN")
        # Fallback: token from provided request dump (can be overridden via env)
        or "eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMThZc2hrZ09sRjNoR1dMeStGZmxLV0FscXl2elp5alB5VEVzcyttUkhoNUx4Vkt5dURaeDZNOWFUTnpnQnYyaURJZWR0KzBpeUpmaUZQcWdDR0liT3hpYVF2b3JkRHNTOEN1enVLMDc0OEFEaWpXY003eDliU2hUYWM3b0d4b2ZKeVFvRHc1d1N4clR6ay9sdm4vSERrbGVhSWNoQjRCUmRRUzlyek44dmxkRklvN0orRXI4VXFsQ1ViemUzQWZrQThaNHpFc0ovVWNIN1Z2dytNWFdLeXdnYllBYTYyU3JOWFVsbjRBK3ZLaGkxaEJxWjJmYlNIN0pWOXhrUVYvR0NxdTJlaDNzZmU4cG8zTHdLWWxhZkpnVjNMU2t6N3c0RkZOT1lxejUxN2dka3NwVVY1OHQ0Q2FZSE9UTGJKZ0JpcGlZdFFETzVjY1I4WmM0TmlVUFUvTVlsME43MjlPb0dmYm4wbVlpZ1RJLzl4MFlDeFo4YkF0dW9NeHlmOWk1YVhFMWhZOFgwbXpBblBGZFd5SytsTS9vWlFjMFYydUg2UVZhUVI4ZWFmc3AybmxDNExCc1EvSEt2ZWZpTldKZ2RzeTFkQndhaWRERDBnQ2krUTNmd2dXY2lXVUtrbXZFcVUvTHB6bTRaemhsM1c4cFpySXh2N2FiSERyVXNRNVBMaTZrRFYxajNuRDlZRjJKWTFuRllOZnZyT2dxUXp3blRJY005c3V5ZmU3MGFjS0xvcEhQN2hCZ1JjQ0hzY2czZkwxU2ZVcFhrSjFzTndSUzJ5bDJsVFlxSnBEbHpPaENtR0hkUDZhVnlmVlVHK0V5b3NvZDMxcldUaWxmRmg1RVVkeUZPb21aRW1GZmpJZ0dBUlJlME9GVFN6WUFTc1ZWbjVWc25LcSsxM0NwMVVmcTFZTHFkKy94K0FRSEJPR0Z0WStubjZ2NEVVVlZ5Tk1pMVl2dU9TcEs3TTlSUzlGR1VFeHhxd3h4TGUvWEtwMGV0Q2ExdExndjRQZnZDWERXajkxQlFrcFBWdWswaU1od01IYkpoOEJyZEJEbWlqcm9HNDM0OUNxUm1NQXdKZGxlR2NaMDJDWVlPMXpiVURxaEN5VmZuTHBaUjNNTDZpTmtUQnhDaFdyWWh6MkwvNGJwa2MzTUF6a01ONFN3c2ZWSkE3S3hhcHJ3bERlQTZIYVJiZ1pjOTFBbC9aVlViSGxrVDJKMjVpNXJzRlJYZW5IU0UxalhTc0FmS1kwK0xDa1p5R0dId3d1L0JKRkxIaTV1S3dhSUlLUXBBVllZbUxVNHJnaUVYVlVCNCtIeEQ0THBIMGxEeExNV3pYbjV4Qjh2blQwei95ZGtCb3ozbnlsdkE2S1ZWcU9ha2JBRVVoazJnUWcxMlN5U2I5cWE2WG9TSU1FTnZudmYrQWNzMno4L2cyYnR2dThmOEZzTnk4TERNdmFPMlhqUTRNckc5TGV6Q01scEZFbE1oUmtqV00zN2c4cDRXUUErRjJqSnY3K3Y4VURFZEdjeGZIYncvd0VkQVBPakJlQzNzdlB1cXo2K1FTZW9BWHlGSkZYVWhhNTg3Q2pxY3F2TGNtTjlWWnptdkhVemxwaUVmZjFxYlo5TWhsNzZUdzBZY2tMamtBa0RXTk1qVndrUWc2WlUySERZWFJwUFhyZ0dtSFFLaGFvSkc3VWRzdEdyeVVmeE1zTVByWmNncTlQUk1nRFVWaWdYc3hOaVFLUi96YUFzVExnTUMvQ1gyVFdPdUpHQ05aK0VWU3Y0YXBqaTB5UlNkdmRnM01UZE1VSjl2MFZPTFBHSkt4VzgydE4rbXIxVC9KcTZwS3hPb3Y1Rm9QMlF5TkxERWxKMXllbzFPWGdZMVArTzJuM1JRaFlRL2NUdWtMMlU2cGt1bHBiNU9nTG9ianNaK1JSSU1sZkM3TDR2NkZjeVZVOHNSTjhQc3o0NTBUSkpDdXN2SDZNcTk3VmFuQWRUOEZpZW9JWHovOHI3a3F5QVlUTTgveHBnZHpBdnIrWmxKaFJialBEZmt2QVBlT0FiOXVRTk9USnE5MGpXK1VHZWt4NG5TZkI1Vk5VSWdEaWdrdXVoVnBrRWh3VTRyMkFjVnpzQ1ZlQlFBRURoV3FDdDg3R2NMRytvai9iV21nMzBLVjlvc256ZThkQ3NoM1dBYkVWVlRsNWxOUVRhdVY3Qkp0Z0RGaXkrTUNlOFhBQmpkZWpYU3RuN2xCSFA5dWlZODJ2L0NJWkxwS1F4aTZKY3ZXQVF5R2VFckFkaWZrb2tzV0FYVUUyZ0UvTEdEQ3VuamhLeWFlSG94V1VGNjFsUHRmRjEyNGdqa1Z2cHFxb2dsNlc1ZUdBZTZ6SnBZRGs4UXJUd2YvdnlJVnkzV3ZTTXdIQVIxb1lPWWFTeSsyZ2h3dTZoeTlKNVlXcEF2QXVNUVVpd21TT29ERmFRRlhMVXdRVnp4enRTbGVrT1Z6THFxcHgvd1BOOWlweXpPcGRBOGw1dmZCU3ZLbUZmSDhjNzMvQmV1czZQaXJzcGtPVFdBVnhIY3craFNQUmFNbjUzMVhtUDR0amdnbGo0d1cycGJGakthV20xUG9JNzI1Uy9jLzYwTVIzMTZJdEdpbkVnTHk4MERKbFc1eG9oNmU2cFpSb0QyTFUvYUhzK3VXUGRNWk9QekFkNEh4UldHNUo0dy91U3QzSFpNMG1HUEFmNGNyVTg1VlYzZjRtWUM2N2Nya0Q3Ukx5YmpXbXBkaFJ0OGZuQnhZT0pja1hnMkRIVE96SGIybTVYYnlPSWcxNWJnbldHa0UvbzZqSUdKSTFOaWZQblhWc290eHdXRThreDNZVlZPWWoyd3V5MnhKVjgvMEZBemJDaUdyZEtUWC9zeWZ5SXJBL1NqeWtrYlR0TEZBRzhaM1dlY1BxVVNRaFJDaGd2eVZNVlNiZGFtUGE1Vm9BUURZR0g1TU50Z0pvVzkrR0VKNDZJYXNHQWNMMFM4NC81TEp3RGZISFRjdmdCYTNSNldKc2lGZm8yRTFoQ0I5WERWK1hZL1RRYS9ZNGlEWjlCcFpxYy8vUzBpMkRINS82ZnFpRm5YMW9odFJhVVJ3ZHdYK1FQcHBmUi9Gd2RsRlNhejJ4MFlGNk1YMm9sSTk1bUQ2MWcrYTBtcGZ5aWFBd1JKbFJERHlvR3ZuMWl2bGZ6eTlJRmYzRWFuako1TTZaUzVzK3BEU0M1amF4MXRCRUZzNEg.NdJsKIXMhIYj8AYtjqaEXeux9ZTPGa5F9p1FJzYEgiA"
    )


def build_headers(access_token: str, sub_branch: Optional[str] = "MTc=") -> Dict[str, str]:
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,ms;q=0.7",
        "access-token": access_token,
        "connection": "keep-alive",
        "host": "phinnisi.pelindo.co.id:9018",
        "origin": "https://phinnisi.pelindo.co.id",
        "referer": "https://phinnisi.pelindo.co.id/",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
        ),
    }
    if sub_branch:
        headers["sub-branch"] = sub_branch
    return headers


def extract_records(payload: Any) -> List[Dict[str, Any]]:
    if payload is None:
        return []
    try:
        # Common shapes used by other endpoints
        if isinstance(payload, dict):
            if isinstance(payload.get("data"), dict):
                if isinstance(payload["data"].get("dataRec"), list):
                    return payload["data"]["dataRec"]
                if isinstance(payload["data"].get("rows"), list):
                    return payload["data"]["rows"]
            if isinstance(payload.get("data"), list):
                return payload["data"]
            if isinstance(payload.get("rows"), list):
                return payload["rows"]
        if isinstance(payload, list):
            return payload
    except Exception:
        pass
    return []


def fetch_page(
    session: requests.Session,
    page: int,
    record: int,
    type_: str,
    start_date: str,
    end_date: str,
    id_unit: Optional[str] = None,
    id_zone: Optional[str] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    params = {
        "page": page,
        "record": record,
        "type": type_,
        "start_date": start_date,
        "end_date": end_date,
    }
    if id_unit:
        params["id-unit"] = id_unit
    if id_zone:
        params["id-zone"] = id_zone

    resp = session.get(API_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    records = extract_records(data)
    return data, records


def fetch_all(
    access_token: str,
    sub_branch: Optional[str],
    type_: str,
    start_date: str,
    end_date: str,
    record: int = 100,
    page_start: int = 1,
    max_pages: Optional[int] = None,
    id_unit: Optional[str] = None,
    id_zone: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    session = requests.Session()
    session.headers.update(build_headers(access_token, sub_branch))

    page = page_start
    all_records: List[Dict[str, Any]] = []
    last_payload: Dict[str, Any] = {}

    while True:
        print(f"[i] Fetching page {page}…")
        payload, records = fetch_page(
            session=session,
            page=page,
            record=record,
            type_=type_,
            start_date=start_date,
            end_date=end_date,
            id_unit=id_unit,
            id_zone=id_zone,
        )
        last_payload = payload
        print(f"[i] Retrieved {len(records)} records")
        if not records:
            break
        all_records.extend(records)
        if len(records) < record:
            break
        if max_pages is not None and (page - page_start + 1) >= max_pages:
            break
        page += 1

    print(f"[i] Total records fetched: {len(all_records)}")
    return all_records, last_payload


def _auto_detect_sort_column(df: pd.DataFrame) -> Optional[str]:
    # Priority keywords likely representing magnitude columns
    priority = [
        "total", "grand_total", "sum", "amount", "value",
        "utilization", "util", "percentage", "percent", "persen",
        "qty", "count", "volume", "teus", "gt", "grt",
        "hours", "duration"
    ]
    cols = list(df.columns)
    lower_cols = [c.lower() for c in cols]
    for key in priority:
        for col, lcol in zip(cols, lower_cols):
            if key in lcol:
                try:
                    pd.to_numeric(df[col], errors="coerce")
                    return col
                except Exception:
                    continue
    # Fallback: first numeric dtype column
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if num_cols:
        return num_cols[0]
    # Last resort: try to coerce any column to numeric and pick the one with most valid nums
    best_col, best_non_nan = None, -1
    for col in cols:
        ser = pd.to_numeric(df[col], errors="coerce")
        cnt = ser.notna().sum()
        if cnt > best_non_nan:
            best_col, best_non_nan = col, cnt
    return best_col


def save_outputs(records: List[Dict[str, Any]], raw: Dict[str, Any], csv_path: str, json_path: str, sort_by: Optional[str] = None) -> None:
    # Save raw JSON payload (last page) for troubleshooting
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        print(f"[i] Raw payload saved to {json_path}")
    except Exception as e:
        print(f"[!] Failed to write raw JSON: {e}")

    # Save flattened records to CSV if available
    if not records:
        print("[!] No records to save to CSV")
        return
    try:
        df = pd.json_normalize(records)
        # Sorting: either by provided column or auto-detected
        chosen_col: Optional[str] = None
        if sort_by:
            if sort_by in df.columns:
                chosen_col = sort_by
            else:
                print(f"[!] --sort-by column '{sort_by}' not found; attempting auto-detect")
        if not chosen_col:
            chosen_col = _auto_detect_sort_column(df)
        if chosen_col:
            try:
                df[chosen_col] = pd.to_numeric(df[chosen_col], errors="coerce")
                df = df.sort_values(by=chosen_col, ascending=False, na_position='last')
                print(f"[i] Sorted CSV by '{chosen_col}' (descending)")
            except Exception as e:
                print(f"[!] Failed to sort by '{chosen_col}': {e}")
        else:
            print("[!] No suitable column found for sorting; writing unsorted CSV")

        df.to_csv(csv_path, index=False)
        print(f"[i] CSV saved to {csv_path} with {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"[!] Failed to write CSV: {e}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    defaults = resolve_defaults()
    p = argparse.ArgumentParser(description="Scrape Tug Utilization dashboard API and export to CSV")
    p.add_argument("--type", default=defaults["type"], help="Type parameter (e.g., invoice)")
    p.add_argument("--start-date", default=defaults["start_date"], help="Start date (YYYY-MM-DD)")
    p.add_argument("--end-date", default=defaults["end_date"], help="End date (YYYY-MM-DD)")
    p.add_argument("--record", type=int, default=defaults["record"], help="Page size to request")
    p.add_argument("--page", type=int, default=defaults["page"], help="Start page number")
    p.add_argument("--max-pages", type=int, default=defaults["max_pages"], help="Max number of pages to fetch (default: all)")
    p.add_argument("--sub-branch", default="MTc=", help="Optional sub-branch header value")
    p.add_argument("--id-unit", default="", help="Optional id-unit parameter")
    p.add_argument("--id-zone", default="", help="Optional id-zone parameter")
    # Get current directory path (root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_csv = os.path.join(script_dir, "tug.csv")
    p.add_argument("--csv", default=default_csv, help="Output CSV path")
    p.add_argument("--sort-by", default="revenue", help="Column name to sort by descending in CSV output (default: revenue)")
    p.add_argument("--json", default="tug_raw.json", help="Output raw JSON path")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    token = resolve_access_token()
    if not token:
        print("[!] Missing access token. Set PHINNISI_ACCESS_TOKEN or edit script.")
        return 2

    try:
        records, raw = fetch_all(
            access_token=token,
            sub_branch=args.sub_branch,
            type_=args.type,
            start_date=args.start_date,
            end_date=args.end_date,
            record=args.record,
            page_start=args.page,
            max_pages=args.max_pages,
            id_unit=(args.id_unit or None),
            id_zone=(args.id_zone or None),
        )
        sort_col = args.sort_by if args.sort_by else None
        save_outputs(records, raw, args.csv, args.json, sort_by=sort_col)
        return 0
    except requests.HTTPError as e:
        print(f"[!] HTTP error: {e}")
        try:
            print(f"    Response: {e.response.text[:500]}…")
        except Exception:
            pass
        return 1
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
