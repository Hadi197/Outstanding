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
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST request for /api/abaikan"""
        if self.path != '/api/abaikan':
            self.send_error(404, "Not Found")
            return
            
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
            
            # Save to abai.csv
            success = self.save_to_abai_csv(no_pkk_inaportnet, timestamp)
            
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
    
    def save_to_abai_csv(self, no_pkk_inaportnet, timestamp):
        """Save no_pkk_inaportnet to abai.csv"""
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
                
                # Write header if new file
                if not file_exists:
                    writer.writerow(['no_pkk_inaportnet', 'timestamp', 'status'])
                
                # Write data
                writer.writerow([no_pkk_inaportnet, timestamp, 'diabaikan'])
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {str(e)}")
            return False
    
    def do_GET(self):
        """Handle GET request - show status"""
        if self.path == '/api/status':
            self.send_response(200)
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