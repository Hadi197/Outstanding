import fetch from 'node-fetch';

// Directly access the Google Sheets URL
const targetUrl = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ88zxzTOq9RiNLwxNksme7AR4qObWshvhQqAknaSYDk1LC0jpXTid-zRgLmD5ZX382COKY-66kt6QD/pub?gid=1151080218&single=true&output=csv";

// Fungsi untuk mengambil data dari Google Sheets
async function fetchCSV() {
    try {
        const response = await fetch(targetUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const csvText = await response.text();
        console.log("✅ Data Google Sheets berhasil diambil:", csvText.slice(0, 100)); // Cek bagian pertama CSV

        // Parsing CSV sederhana
        const rows = csvText.split("\n").map(row => row.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(col => col.replace(/(^"|"$)/g, '').trim()));
        console.log("✅ Header CSV:", rows[0]); // Debug header

        const headers = rows[0].map(header => header.trim().toLowerCase()); // Bersihkan spasi dan ubah ke huruf kecil
        const noPkkInaportnetIndex = headers.indexOf("no_pkk_inaportnet");
        const noPkkIndex = headers.indexOf("no_pkk");
        const vesselNameIndex = headers.indexOf("vessel_name");
        const gtIndex = headers.indexOf("gt");
        const loaIndex = headers.indexOf("loa");
        const companyNameIndex = headers.indexOf("company_name");
        const noSpbIndex = headers.indexOf("no_spb");
        const waktuSpbIndex = headers.indexOf("waktu_spb");
        const periodeSpbIndex = headers.indexOf("periode_spb");
        const nameProcessCodeIndex = headers.indexOf("name_process_code");
        const nameBranchIndex = headers.indexOf("name_branch");

        console.log("🔍 Indeks Kolom:", { noPkkInaportnetIndex, noPkkIndex, vesselNameIndex, gtIndex, loaIndex, companyNameIndex, noSpbIndex, waktuSpbIndex, periodeSpbIndex, nameProcessCodeIndex, nameBranchIndex });

        if (noPkkInaportnetIndex === -1 || noPkkIndex === -1 || vesselNameIndex === -1 || gtIndex === -1 || loaIndex === -1 || companyNameIndex === -1 || noSpbIndex === -1 || waktuSpbIndex === -1 || periodeSpbIndex === -1 || nameProcessCodeIndex === -1 || nameBranchIndex === -1) {
            console.error("⚠️ Kolom yang diperlukan tidak ditemukan dalam CSV!");
            console.error("📋 Header CSV:", headers);
            return;
        }

        const filteredRows = rows.map(row => [
            row[noPkkInaportnetIndex],
            row[noPkkIndex],
            row[vesselNameIndex],
            row[gtIndex],
            row[loaIndex],
            row[companyNameIndex],
            row[noSpbIndex],
            row[waktuSpbIndex],
            row[periodeSpbIndex],
            row[nameProcessCodeIndex],
            row[nameBranchIndex]
        ]);
        console.log("🔍 Isi Data CSV:", filteredRows); // Log the filtered CSV data

    } catch (error) {
        console.error("❌ Gagal mengambil data dari Google Sheets:", error);
    }
}

// Jalankan fetchCSV()
fetchCSV();
