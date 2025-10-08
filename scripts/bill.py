#!/usr/bin/env python3
"""
Pelindo Billing Invoice Scraper
Scrapes billing invoice data from Pelindo API
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PelindoBillingScraper:
    def __init__(self):
        self.base_url = "https://phinnisi.pelindo.co.id:9021"
        self.api_endpoint = "/api/billing/invoice/list"
        self.session = requests.Session()
        
        # Headers from the request
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,id;q=0.8,ms;q=0.7',
            'access-token': 'eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMThZS3ZMWmhSL1U0ekpsMEpDS1Exd0NQdVhnRHRxeTYrT1owUFZJZ3dnOWZVcm9kTjRRSWgwaURjMlZvOG9SNm12djBHMU1oWXZTdTRvdTZ1TDF1TG9XMTFnbEcraGxUa2hweThUZjNXeHJQQXFieXRsY21HK2UyTW5qNlNBV0Q2cFNxVmFUMEFTWnlIbGJIc21CbDQzOWVtMEJmYTQrWWxJeGxVczJZQUE1RFhMYno4SXo1SkxuSWJydy9FZjVJQng5QVQ4RWEwVDBsbFYwUXJYOVNGUmZ5NEN3UnRUZnJWWGxRR2VrMk1PQWU3c3M2WmhVcWg0THM5TkJkaTlaQUhYTThnRXJ3OGhLMmhvdncvcFZVZnU5WFBmY0QvNUhMQVFGTkxMVDRnR2Q1NDlMSkVveS9lamZCWFVwUEkzbTlpN0ZWZXVkRWdPZFlLUTUyRkhxV2RCUWVabWQwWVpUckJUN3V6ZFZDTnZBbHRpN3JaaU9XdnBjUG1ZZzRXRU5TQzVtdmJkUytmREV0V0hlK0tuTStYdkM2MHUwQklwZkhHcjJVdkh0YUthaVhzYW5ZdFFyM21PQkY0WUo3Mm1SNFdBNVp3b1ZTR0l3K0xtRlJqMUpDQnQ2aWNuSUVrRm51TlVhelYrRE9VTzlOVmdkem42WGRpbVhETWVaTU0zSjl1VUk1ZzRwSWp4S09uemlMeFJpOG1jYzZpRHdyMUVIazlWK1NhQXR5MjI5bjBKdHRESjUyemExMjIxd2hucTNnSjV6OGdnZFoveHdTdkNEM2R2K0pmOENiTThvWUg2ZXVrN1FrRHlwMDYvZkp4NnN0ZTdkRzJuZDJlVXlqdThpNDIrcUlza21PaUhkVkNTZ2tMYWl1aFkvNEZPWTJ2S3RQcGtzNEUvMVdudmZpY2lmYXgxTWYrQlorc3NjNXMzL0RqRUV2amxOSTh6Z0o0Z043NUF6V1BjcTNRYThoWEl0UmxRNzhaUEttZ2hndER0UURnRXBNL0dqTjRxc1dkMHg2OURwTlhWMVFkOVFVUHRlWXJpTGh6TnhEUUs5YXJQenphdzV4UWozejgyVGRRVlg1akppU2pGVTRLalF0b0N2aGZWNXhCSk5IbjBQQ0hXNFZtUGpJeUpoN3dQSFUvbVIwQ2hSLys0RmhzQXdYZVVvSy95NVQ1MVMyMVoraDFjQ3B2NnRPL2NRdGNVNms1Z0YzczI1Y3NyM1BFQ1VpVmVYbkc3YkdQblFqQ29JTFovdGJ2Zm5yTUdlTGQzamk4ZTFqcjhvbFY4TnNvZTFvdllRR2tQTitUazF5NjZxdTh2N0FRcWNERTdWQnZpVEdiVk9Wd05wbVFQZ0s5U25kZTUyQlpFOGd3MFBDdkdjZDNBU1p4bFBHc0MxYjZoOUg3Q3VtSmVWa1Vub2M3ZjlWc25FZGtSNVhicWU2NzFmNnF4R3haWG9Ha2ZjcUhBamk3L0RQQXN6RmEzUkpXUmRyN1ZjRTVaUUErWkdQZEJOdy9JMDdmSW9lUmZkVzVkTURIUDhkYlplaWFIcnV5S3pXeFBVMHlIeVM5RWcyNDNiZlVZYVVrSVRjOGZ6RVpkNGNHeWxOOHI1RXFIR2cvZ2tFbm43NURqeUp0UUpqRDYyK1dnSEc1bzVEbEsxZlVPRFNiNEdlejNCSXVZTmZ3blJpaGVDMVJqUUs2UVhBUDRHVllKam1xYzRlT0lTdENscVUraVdnQml1a1hOdHhkeWtiLzVENFdCVnp3RC9CVUpPcGtocTNjaVovektySzdhSVVjbFdhRWd6cDRETEIveThZWG5JRXpIeFUwK2c3cHo1dHdyOUFZaVJnaG5SN1ppS3NHU1lhdTVBSmlWSGMvOWVJTWhhNXNvb3lBSkpuNTNGTTJBMGtLcmJqMmZud09vcVI5aWlQSUZ1V2c5RjJ1eVFTR0R4ZW5YbXFERWxXeGFINDV4OG1Wbjd0M1FqRXp3WEx6NldyaldGREYxMzY0NWpEWXhxTU5TMmVyZzcvUmNXbFBselM3RWxFa3VkeDdUMXdhNWRLa3RXR1JyNkNTQmJIOVh4WXltSzdJS1lkbmd1eXNReWE1MDhpVWdGYUlzWVFFeXNMejhKaUxGMEpNZlRScWltM3VlVGVvT250VCtJNkpFYWxSN21CTEpoQk1QdzdZM05YMS91STlteGE5NTQrTFZKMURzblozK3d3UStmdURVL2JMMWxQM2p2V1JxU1U1V3VtTEdBalVucUVHMHArQ3RvZU1Sd2M2QkYvYlR2bTRydVRoMHlGVWFjMlZaMnZESmJqMkh0M0xxNkxjZVV5cERjclhCeGZHY0Z0RWFwZHJJQkswSjd2cFkwQmhDMm14STd0cUgrRFBoZmQwbEl2QlpUN2U5NysyMGQrVGpTOGlEcjNhT1JZRUdGMk9NRThFeFFIdDlsWm9iQXNFRVJSUGJaTm1EME1IUXhmTGdBTDl4WWJtRlpaRnFyY3ViSi9mOVF3SHdrTHFuQzZwamlCYmpzdU9sU3NSYm5rR1ZOWENaVE1tbTczTXFsQVlPaHVDc0htcG9DcDRFajl2aU1JblF2bmJQYXNiT1lsNVg3OXo2UTZWSGNpdG9rOWhGTmlOOE9RUGlsQUU5cThsMWNTbEJzbG5IYlZZNFk3QUJVdFFCV0huUWRYNnV2YUJiSXNvdmhUODlzc1YwdU1jeWFTVFljN2V1Vm8xMEV1bTlSMnUvOEQvc0FzVzYrYWw5TFVHZHplTFhFZVNZbVUxeDJLMitpV29oTHhSRCtURXRYZkIySDVYN2t4VWxHT3FWMjhzcmVsc1BaOGRsTElFbURwOWNHcS9IWEdmYVpQS1RPek1yd0F6c29sbHdhSzVMRmZVTTVmVndycW11UVpzTGJMdUkzN09UYmx6OGZBOU1MdVZBa0QzbGI5S2I3b0o3Z0pIQm1jUTlhdmVjYWI3Q1JPZGR6TmsxRlR0UXRpQUMrM0U0UjFKMmFIVllKUUxubUNmZm43NmY5UFk1a1NONWo0RDdCOU1wSExTYUUvRmlKdis2WTRuaVpWb2hJUTlJRytyM0Z0bE9QMm5tZDYwMHMxMEh5a2UwdUFJZWdOOW8rZlRrTGVnTkt6NWF4NXBkcVY4UlRuS0tYRFFjOFNOaWZyS21CWWJMaXpORHZSNkNRYzJzYWMrYVhXUUs4aXIrbU1iQmo4YXp6OGtxVTJUMTJaanVxWmwrUDNINlJsaCtpaENwZEhOUkFUcDdRSktwUVpiVDNHcjZjcEpmd2VmMWZnYXljVmQ4cmgxRFdjUWpRWFhzZnhaYzh4YkdUVmt3V3d5S0NPcXQxaVR0YnRmNHhrUT09.G5RtPN7K4UhelpwCHaL_HeoDDTzzdDCItq9rJtt0Mmc',
            'access_token': 'eyJhbGciOiJIUzI1NiJ9.VTJGc2RHVmtYMThZS3ZMWmhSL1U0ekpsMEpDS1Exd0NQdVhnRHRxeTYrT1owUFZJZ3dnOWZVcm9kTjRRSWgwaURjMlZvOG9SNm12djBHMU1oWXZTdTRvdTZ1TDF1TG9XMTFnbEcraGxUa2hweThUZjNXeHJQQXFieXRsY21HK2UyTW5qNlNBV0Q2cFNxVmFUMEFTWnlIbGJIc21CbDQzOWVtMEJmYTQrWWxJeGxVczJZQUE1RFhMYno4SXo1SkxuSWJydy9FZjVJQng5QVQ4RWEwVDBsbFYwUXJYOVNGUmZ5NEN3UnRUZnJWWGxRR2VrMk1PQWU3c3M2WmhVcWg0THM5TkJkaTlaQUhYTThnRXJ3OGhLMmhvdncvcFZVZnU5WFBmY0QvNUhMQVFGTkxMVDRnR2Q1NDlMSkVveS9lamZCWFVwUEkzbTlpN0ZWZXVkRWdPZFlLUTUyRkhxV2RCUWVabWQwWVpUckJUN3V6ZFZDTnZBbHRpN3JaaU9XdnBjUG1ZZzRXRU5TQzVtdmJkUytmREV0V0hlK0tuTStYdkM2MHUwQklwZkhHcjJVdkh0YUthaVhzYW5ZdFFyM21PQkY0WUo3Mm1SNFdBNVp3b1ZTR0l3K0xtRlJqMUpDQnQ2aWNuSUVrRm51TlVhelYrRE9VTzlOVmdkem42WGRpbVhETWVaTU0zSjl1VUk1ZzRwSWp4S09uemlMeFJpOG1jYzZpRHdyMUVIazlWK1NhQXR5MjI5bjBKdHRESjUyemExMjIxd2hucTNnSjV6OGdnZFoveHdTdkNEM2R2K0pmOENiTThvWUg2ZXVrN1FrRHlwMDYvZkp4NnN0ZTdkRzJuZDJlVXlqdThpNDIrcUlza21PaUhkVkNTZ2tMYWl1aFkvNEZPWTJ2S3RQcGtzNEUvMVdudmZpY2lmYXgxTWYrQlorc3NjNXMzL0RqRUV2amxOSTh6Z0o0Z043NUF6V1BjcTNRYThoWEl0UmxRNzhaUEttZ2hndER0UURnRXBNL0dqTjRxc1dkMHg2OURwTlhWMVFkOVFVUHRlWXJpTGh6TnhEUUs5YXJQenphdzV4UWozejgyVGRRVlg1akppU2pGVTRLalF0b0N2aGZWNXhCSk5IbjBQQ0hXNFZtUGpJeUpoN3dQSFUvbVIwQ2hSLys0RmhzQXdYZVVvSy95NVQ1MVMyMVoraDFjQ3B2NnRPL2NRdGNVNms1Z0YzczI1Y3NyM1BFQ1VpVmVYbkc3YkdQblFqQ29JTFovdGJ2Zm5yTUdlTGQzamk4ZTFqcjhvbFY4TnNvZTFvdllRR2tQTitUazF5NjZxdTh2N0FRcWNERTdWQnZpVEdiVk9Wd05wbVFQZ0s5U25kZTUyQlpFOGd3MFBDdkdjZDNBU1p4bFBHc0MxYjZoOUg3Q3VtSmVWa1Vub2M3ZjlWc25FZGtSNVhicWU2NzFmNnF4R3haWG9Ha2ZjcUhBamk3L0RQQXN6RmEzUkpXUmRyN1ZjRTVaUUErWkdQZEJOdy9JMDdmSW9lUmZkVzVkTURIUDhkYlplaWFIcnV5S3pXeFBVMHlIeVM5RWcyNDNiZlVZYVVrSVRjOGZ6RVpkNGNHeWxOOHI1RXFIR2cvZ2tFbm43NURqeUp0UUpqRDYyK1dnSEc1bzVEbEsxZlVPRFNiNEdlejNCSXVZTmZ3blJpaGVDMVJqUUs2UVhBUDRHVllKam1xYzRlT0lTdENscVUraVdnQml1a1hOdHhkeWtiLzVENFdCVnp3RC9CVUpPcGtocTNjaVovektySzdhSVVjbFdhRWd6cDRETEIveThZWG5JRXpIeFUwK2c3cHo1dHdyOUFZaVJnaG5SN1ppS3NHU1lhdTVBSmlWSGMvOWVJTWhhNXNvb3lBSkpuNTNGTTJBMGtLcmJqMmZud09vcVI5aWlQSUZ1V2c5RjJ1eVFTR0R4ZW5YbXFERWxXeGFINDV4OG1Wbjd0M1FqRXp3WEx6NldyaldGREYxMzY0NWpEWXhxTU5TMmVyZzcvUmNXbFBselM3RWxFa3VkeDdUMXdhNWRLa3RXR1JyNkNTQmJIOVh4WXltSzdJS1lkbmd1eXNReWE1MDhpVWdGYUlzWVFFeXNMejhKaUxGMEpNZlRScWltM3VlVGVvT250VCtJNkpFYWxSN21CTEpoQk1QdzdZM05YMS91STlteGE5NTQrTFZKMURzblozK3d3UStmdURVL2JMMWxQM2p2V1JxU1U1V3VtTEdBalVucUVHMHArQ3RvZU1Sd2M2QkYvYlR2bTRydVRoMHlGVWFjMlZaMnZESmJqMkh0M0xxNkxjZVV5cERjclhCeGZHY0Z0RWFwZHJJQkswSjd2cFkwQmhDMm14STd0cUgrRFBoZmQwbEl2QlpUN2U5NysyMGQrVGpTOGlEcjNhT1JZRUdGMk9NRThFeFFIdDlsWm9iQXNFRVJSUGJaTm1EME1IUXhmTGdBTDl4WWJtRlpaRnFyY3ViSi9mOVF3SHdrTHFuQzZwamlCYmpzdU9sU3NSYm5rR1ZOWENaVE1tbTczTXFsQVlPaHVDc0htcG9DcDRFajl2aU1JblF2bmJQYXNiT1lsNVg3OXo2UTZWSGNpdG9rOWhGTmlOOE9RUGlsQUU5cThsMWNTbEJzbG5IYlZZNFk3QUJVdFFCV0huUWRYNnV2YUJiSXNvdmhUODlzc1YwdU1jeWFTVFljN2V1Vm8xMEV1bTlSMnUvOEQvc0FzVzYrYWw5TFVHZHplTFhFZVNZbVUxeDJLMitpV29oTHhSRCtURXRYZkIySDVYN2t4VWxHT3FWMjhzcmVsc1BaOGRsTElFbURwOWNHcS9IWEdmYVpQS1RPek1yd0F6c29sbHdhSzVMRmZVTTVmVndycW11UVpzTGJMdUkzN09UYmx6OGZBOU1MdVZBa0QzbGI5S2I3b0o3Z0pIQm1jUTlhdmVjYWI3Q1JPZGR6TmsxRlR0UXRpQUMrM0U0UjFKMmFIVllKUUxubUNmZm43NmY5UFk1a1NONWo0RDdCOU1wSExTYUUvRmlKdis2WTRuaVpWb2hJUTlJRytyM0Z0bE9QMm5tZDYwMHMxMEh5a2UwdUFJZWdOOW8rZlRrTGVnTkt6NWF4NXBkcVY4UlRuS0tYRFFjOFNOaWZyS21CWWJMaXpORHZSNkNRYzJzYWMrYVhXUUs4aXIrbU1iQmo4YXp6OGtxVTJUMTJaanVxWmwrUDNINlJsaCtpaENwZEhOUkFUcDdRSktwUVpiVDNHcjZjcEpmd2VmMWZnYXljVmQ4cmgxRFdjUWpRWFhzZnhaYzh4YkdUVmt3V3d5S0NPcXQxaVR0YnRmNHhrUT09.G5RtPN7K4UhelpwCHaL_HeoDDTzzdDCItq9rJtt0Mmc',
            'connection': 'keep-alive',
            'content-type': 'application/json',
            'host': 'phinnisi.pelindo.co.id:9021',
            'id-unit': '',
            'id-zone': '',
            'origin': 'https://phinnisi.pelindo.co.id',
            'referer': 'https://phinnisi.pelindo.co.id/',
            'sec-ch-ua': '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sub-branch': 'NzI=,MTAx,NjE=,ODE=,MjU=,NzU=,ODM=,NzQ=,NzM=,Mjk=,Mjc=,MTY=,NTc=,NjA=',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0'
        }
        
        # Set headers for the session
        self.session.headers.update(self.headers)
    
    def get_invoice_list(self, payload: Dict = None) -> Optional[Dict]:
        """
        Fetch invoice list from Pelindo API
        
        Args:
            payload: JSON payload for POST request
            
        Returns:
            JSON response data or None if failed
        """
        try:
            url = f"{self.base_url}{self.api_endpoint}"
            
            # Default payload if none provided
            if payload is None:
                payload = {
                    "page": 1,
                    "record": 10000,
                    "data": "",
                    "filterByStatus": "",
                    "filterByType": "",
                    "filterByNota": "",
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31"
                }
            
            logger.info(f"Making request to: {url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Response received: {response.status_code}")
            logger.info(f"Response size: {len(response.content)} bytes")
            
            # Debug: Print response structure
            if isinstance(data, dict):
                logger.info(f"Response structure - Keys: {list(data.keys())}")
                for key, value in data.items():
                    if isinstance(value, list):
                        logger.info(f"  {key}: List with {len(value)} items")
                    elif isinstance(value, dict):
                        logger.info(f"  {key}: Dict with keys {list(value.keys())}")
                    else:
                        logger.info(f"  {key}: {type(value).__name__} = {value}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def get_all_invoices(self, search_params: Dict = None) -> List[Dict]:
        """
        Fetch all invoices with pagination
        
        Args:
            search_params: Search parameters for filtering
            
        Returns:
            List of all invoice records
        """
        all_invoices = []
        page = 1
        record = 10000  # 10,000 records per batch
        
        if search_params is None:
            search_params = {}
        
        # Remove page limit to fetch all data
        # max_pages = None (unlimited)
        
        while True:
            payload = {
                "page": page,
                "record": record,
                "data": search_params.get("data", ""),
                "filterByStatus": search_params.get("filterByStatus", ""),
                "filterByType": search_params.get("filterByType", ""),
                "filterByNota": search_params.get("filterByNota", ""),
                "start_date": search_params.get("start_date", "2025-01-01"),
                "end_date": search_params.get("end_date", "2025-12-31")
            }
            
            logger.info(f"Fetching page {page}...")
            data = self.get_invoice_list(payload)
            
            if not data:
                logger.error(f"Failed to fetch page {page}")
                break
            
            # Extract invoice data based on actual response structure
            if 'data' in data:
                response_data = data['data']
                
                # Check if data contains dataRec (actual invoice records)
                if isinstance(response_data, dict) and 'dataRec' in response_data:
                    invoices = response_data['dataRec']
                elif isinstance(response_data, list):
                    invoices = response_data
                else:
                    invoices = []
                    
                # Get pagination info
                total_pages = 1
                if isinstance(response_data, dict):
                    total_pages = response_data.get('totalPage', 1)
                    total_rows = response_data.get('totalRow', 0)
                    logger.info(f"Total rows available: {total_rows}, Total pages: {total_pages}")
                    
            else:
                invoices = []
                total_pages = 1
            
            if not invoices:
                logger.info("No more invoices found")
                break
            
            all_invoices.extend(invoices)
            logger.info(f"Page {page}/{total_pages}: {len(invoices)} invoices fetched. Total so far: {len(all_invoices)}")
            
            if page >= total_pages:
                logger.info("All pages fetched")
                break
            
            page += 1
            logger.info(f"Moving to next page ({page}/{total_pages})...")
            time.sleep(2)  # Rate limiting - increased to 2 seconds for larger requests
        
        logger.info(f"Total invoices fetched: {len(all_invoices)}")
        return all_invoices
    
    def save_to_csv(self, data: List[Dict], filename: str = None) -> str:
        """
        Save invoice data to CSV file with specific columns and filtering
        
        Args:
            data: List of invoice dictionaries
            filename: Output filename (optional)
            
        Returns:
            Filename of saved file
        """
        if not data:
            logger.warning("No data to save")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pelindo_invoices_{timestamp}.csv"
        
        # Ensure file is saved to data directory
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(script_dir), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Join with data directory path
        if not os.path.dirname(filename):  # If filename doesn't have path
            filename = os.path.join(data_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            
            # Filter only PELAYANAN KAPAL type
            df_filtered = df[df['type'] == 'PELAYANAN KAPAL'].copy()
            
            if len(df_filtered) == 0:
                logger.warning("No PELAYANAN KAPAL records found")
                return ""
            
            # Select only required columns
            required_columns = [
                'no_pkk',
                'no_pkk_inaportnet',
                'vessel_name', 
                'shipping_agent',
                'departure_date',
                'verified_date',
                'verified_by',
                'name_branch',
                'type'
            ]
            
            # Check if all required columns exist
            missing_cols = [col for col in required_columns if col not in df_filtered.columns]
            if missing_cols:
                logger.error(f"Missing columns: {missing_cols}")
                return ""
            
            # Select required columns
            df_result = df_filtered[required_columns].copy()
            
            # Convert date columns to datetime for calculation, handle timezone issues
            df_result['departure_date'] = pd.to_datetime(df_result['departure_date'], errors='coerce').dt.tz_localize(None)
            df_result['verified_date'] = pd.to_datetime(df_result['verified_date'], format='%d-%m-%Y %H:%M', errors='coerce')
            
            # Calculate Lama_Nota (difference in days)
            df_result['Lama_Nota'] = (df_result['verified_date'] - df_result['departure_date']).dt.days
            
            # Calculate Periode (Month-Year from departure_date)
            df_result['Periode'] = df_result['departure_date'].dt.strftime('%m-%Y')
            
            # Reorder columns
            final_columns = [
                'no_pkk',
                'no_pkk_inaportnet',
                'vessel_name',
                'shipping_agent', 
                'departure_date',
                'verified_date',
                'Lama_Nota',
                'verified_by',
                'name_branch',
                'Periode',
                'type'
            ]
            
            df_result = df_result[final_columns]
            
            # Save to CSV
            df_result.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Data saved to: {filename}")
            logger.info(f"Records saved: {len(df_result)}")
            logger.info(f"Columns: {list(df_result.columns)}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return ""
    

    
    def print_summary(self, data: List[Dict]):
        """
        Print summary of scraped data
        
        Args:
            data: List of invoice dictionaries
        """
        if not data:
            logger.info("No data to summarize")
            return
        
        df = pd.DataFrame(data)
        
        print("\n" + "="*60)
        print("PELINDO BILLING INVOICE SCRAPER - SUMMARY")
        print("="*60)
        print(f"Total records: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Scraping date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nColumn names:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
        
        if len(df) > 0:
            print("\nSample data (first 3 rows):")
            print(df.head(3).to_string())
        
        print("="*60)

def scrape_current_year():
    """
    Scrape invoice data for the current year
    
    Returns:
        List of invoice records for current year
    """
    scraper = PelindoBillingScraper()
    current_year = datetime.now().year
    
    search_params = {
        "data": "",
        "filterByStatus": "",
        "filterByType": "",
        "filterByNota": "",
        "start_date": f"{current_year}-01-01",
        "end_date": f"{current_year}-12-31"
    }
    
    print(f"🔍 Scraping Pelindo invoices for year {current_year}")
    print(f"📅 Date range: {search_params['start_date']} to {search_params['end_date']}")
    
    invoices = scraper.get_all_invoices(search_params)
    
    if invoices:
        # Save as bill.csv
        csv_file = scraper.save_to_csv(invoices, "bill.csv")
        
        scraper.print_summary(invoices)
        
        print(f"\n✅ Successfully scraped {len(invoices)} invoices for year {current_year}")
        if csv_file:
            print(f"📄 CSV: {csv_file}")
        
        return invoices
    else:
        print(f"❌ No invoices found for year {current_year}")
        return []

def main():
    """
    Main function to run the scraper
    """
    scraper = PelindoBillingScraper()
    
    # Current year parameters (2025)
    current_year = datetime.now().year
    search_params = {
        "data": "",  # Search term
        "filterByStatus": "",  # Invoice status filter
        "filterByType": "",    # Invoice type filter
        "filterByNota": "",    # Nota filter
        "start_date": f"{current_year}-01-01",  # Start of current year
        "end_date": f"{current_year}-12-31"     # End of current year
    }
    
    print("Starting Pelindo Billing Invoice Scraper...")
    print(f"Target URL: {scraper.base_url}{scraper.api_endpoint}")
    print(f"Scraping data for year: {current_year}")
    print(f"Date range: {search_params['start_date']} to {search_params['end_date']}")
    print(f"📊 Batch size: 10,000 records per page")
    print("⚠️  Note: This will fetch ALL data and may take several minutes...")
    
    # Test single request first
    print("\nTesting connection...")
    test_data = scraper.get_invoice_list()
    
    if test_data:
        print("✅ Connection successful!")
        print(f"Response keys: {list(test_data.keys()) if isinstance(test_data, dict) else 'Not a dict'}")
        
        # Show estimated data size
        if isinstance(test_data, dict) and 'data' in test_data:
            data_info = test_data['data']
            if isinstance(data_info, dict):
                total_pages = data_info.get('totalPage', 'Unknown')
                total_data = data_info.get('totalData', 'Unknown')
                print(f"📈 Estimated total records: {total_data}")
                print(f"📄 Total pages to fetch: {total_pages}")
        
        # Fetch current year invoices
        print("\n🚀 Starting full data scraping...")
        print("This may take several minutes depending on data size...")
        all_invoices = scraper.get_all_invoices(search_params)
        
        if all_invoices:
            # Save with specific filename
            csv_file = scraper.save_to_csv(all_invoices, "bill.csv")
            
            # Print summary
            scraper.print_summary(all_invoices)
            
            print(f"\n✅ Successfully scraped {len(all_invoices)} invoices for year {current_year}")
            if csv_file:
                print(f"📄 CSV file: {csv_file}")
        else:
            print(f"❌ No invoice data found for year {current_year}")
    else:
        print("❌ Connection failed - check credentials and network")

if __name__ == "__main__":
    main()
