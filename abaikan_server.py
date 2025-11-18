#!/usr/bin/env python3
"""
Server untuk menangani request Abaikan dari dashboard Outstanding.
Menambahkan no_pkk_inaportnet ke file abai.csv
"""

import os
import csv
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import signal
import sys

class AbaikanHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.csv_file = os.path.join(os.path.dirname(__file__), 'abai.csv')
        self.keterangan_file = os.path.join(os.path.dirname(__file__), 'keterangan.csv')
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST request for /api/abaikan or /api/keterangan"""
        if self.path == '/api/abaikan':
            self.handle_abaikan()
        elif self.path == '/api/keterangan':
            self.handle_keterangan_save()
        else:
            self.send_error(404, "Not Found")
    
    def handle_abaikan(self):
        """Handle abaikan request"""
        try:
            # Get request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            if 'no_pkk_inaportnet' not in data:
                self.send_error(400, "Missing no_pkk_inaportnet")
                return
            
            no_pkk_inaportnet = data['no_pkk_inaportnet']
            timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
            
            # Extract additional fields for CSV columns
            pelabuhan = data.get('pelabuhan', '')
            alasan = data.get('reason', '')  # 'reason' from client maps to 'alasan' in CSV
            keterangan = data.get('notes', '')  # 'notes' from client maps to 'keterangan' in CSV
            
            # Save to abai.csv with all columns
            success = self.save_to_abai_csv(no_pkk_inaportnet, pelabuhan, alasan, keterangan, timestamp)
            
            if success:
                # Send success response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'message': f'Data berhasil ditambahkan ke abai.csv',
                    'no_pkk_inaportnet': no_pkk_inaportnet,
                    'timestamp': timestamp
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
                print(f"✅ Berhasil menambahkan ke abai.csv: {no_pkk_inaportnet}")
                
            else:
                self.send_error(500, "Failed to save data")
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def save_to_abai_csv(self, no_pkk_inaportnet, pelabuhan, alasan, keterangan, timestamp):
        """Save no_pkk_inaportnet and additional info to abai.csv"""
        try:
            # Check if file exists, create if not
            file_exists = os.path.isfile(self.csv_file)
            
            # Check if entry already exists
            if file_exists:
                with open(self.csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) > 0 and row[0] == no_pkk_inaportnet:
                            print(f"⚠️  Data sudah ada di abai.csv: {no_pkk_inaportnet}")
                            return True  # Already exists, consider success
            
            # Append to file
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header if new file (matches the structure we set up earlier)
                if not file_exists:
                    writer.writerow(['no_pkk_inaportnet', 'Pelabuhan', 'Alasan', 'Keterangan'])
                
                # Write data with all columns
                writer.writerow([no_pkk_inaportnet, pelabuhan, alasan, keterangan])
            
            print(f"✅ Saved to abai.csv: {no_pkk_inaportnet}, Pelabuhan: {pelabuhan}, Alasan: {alasan}, Keterangan: {keterangan}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {str(e)}")
            return False
    
    def do_GET(self):
        """Handle GET request - show status or get keterangan"""
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'status': 'ok', 'message': 'Abaikan server is running'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/api/keterangan':
            self.handle_keterangan_get()
        else:
            self.send_error(404, "Not Found")
    
    def handle_keterangan_save(self):
        """Handle save keterangan request"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Get data
            pkk = data.get('pkk', '')
            keterangan_text = data.get('keterangan', '')
            
            if not pkk:
                self.send_error(400, "Missing PKK")
                return
            
            # Save to CSV
            success = self.save_to_keterangan_csv(pkk, keterangan_text)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': success,
                'message': 'Keterangan saved successfully' if success else 'Failed to save keterangan',
                'pkk': pkk,
                'keterangan': keterangan_text
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Error saving keterangan: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def save_to_keterangan_csv(self, pkk, keterangan_text):
        """Save keterangan to keterangan.csv"""
        try:
            # Ensure CSV exists
            file_exists = os.path.isfile(self.keterangan_file)
            
            # Read existing data
            data = {}
            if file_exists:
                with open(self.keterangan_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        data[row['no_pkk_inaportnet']] = row['keterangan']
            
            # Update or delete
            if keterangan_text.strip():
                data[pkk] = keterangan_text.strip()
            else:
                data.pop(pkk, None)
            
            # Write back
            with open(self.keterangan_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['no_pkk_inaportnet', 'keterangan'])
                for k, v in sorted(data.items()):
                    writer.writerow([k, v])
            
            print(f"✅ Saved keterangan to CSV: {pkk}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to keterangan CSV: {str(e)}")
            return False
    
    def handle_keterangan_get(self):
        """Handle get all keterangan request"""
        try:
            # Ensure CSV exists
            if not os.path.isfile(self.keterangan_file):
                with open(self.keterangan_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['no_pkk_inaportnet', 'keterangan'])
            
            # Read all keterangan
            data = {}
            with open(self.keterangan_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['keterangan'].strip():
                        data[row['no_pkk_inaportnet']] = row['keterangan']
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            print(f"📤 Sent {len(data)} keterangan entries")
            
        except Exception as e:
            print(f"❌ Error loading keterangan: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Count entries in abai.csv
            count = 0
            if os.path.isfile(self.csv_file):
                with open(self.csv_file, 'r', encoding='utf-8') as f:
                    count = sum(1 for line in f) - 1  # Exclude header
                    count = max(0, count)
            
            response = {
                'status': 'running',
                'csv_file': self.csv_file,
                'total_entries': count,
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8001):
    """Run the abaikan server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, AbaikanHandler)
    
    print(f"🚀 Abaikan Server berjalan di http://localhost:{port}")
    print(f"📁 CSV file: {os.path.join(os.path.dirname(__file__), 'abai.csv')}")
    print("📌 Endpoints:")
    print("   POST /api/abaikan - Tambah data ke abai.csv")
    print("   GET  /api/status  - Cek status server")
    print("⏹️  Tekan Ctrl+C untuk berhenti")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server dihentikan")
        httpd.server_close()

if __name__ == '__main__':
    # Handle command line arguments
    port = 8001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Port harus berupa angka")
            sys.exit(1)
    
    run_server(port)