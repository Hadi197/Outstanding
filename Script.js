import dotenv from 'dotenv';
import nodemailer from 'nodemailer';
import fetch from 'node-fetch';

dotenv.config();
console.log("EMAIL_USER:", process.env.EMAIL_USER);
console.log("EMAIL_PASS:", process.env.EMAIL_PASS);

// Daftar penerima (50 email)
const emailRecipients = [
    "purwana.hadi@gmail.com",
    "email2@example.com",
    "email3@example.com",
    "email4@example.com",
    "email5@example.com",
    // Tambahkan hingga 50 email...
];

// Buat transporter Nodemailer
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

// Fungsi untuk mengirim email
function kirimEmail(totalSurabaya, totalGresik) {
    const subject = "Laporan Nota Outstanding";
    const body = `
        <p><strong>Nota Outstanding</strong></p>
        <p><strong>Surabaya:</strong> ${totalSurabaya}</p>
        <p><strong>Gresik:</strong> ${totalGresik}</p>
        <p>Untuk lebih detail silahkan cek di link ini: 
        <a href="https://hadi197.github.io/Outstanding/dashboard.html">Dashboard</a></p>
        <p>Terima kasih.</p>
    `;

    const mailOptions = {
        from: `"PJMWilayah3" <${process.env.EMAIL_USER}>`,
        to: emailRecipients.join(","),
        subject: subject,
        html: body
    };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.error("❌ Gagal mengirim email:", error);
        } else {
            console.log("✅ Email berhasil dikirim ke:", info.accepted);
        }
    });
}

// CORS Proxy URL
const proxyUrl = "https://cors-anywhere.herokuapp.com/";
const targetUrl = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRamhRDNlh6CfJCttO-FHkv3x11BrTu5nsSl9kUs-lULcAzC83pyp2op2BaRXXppLaSmmOmxIoVqGar/pub?gid=4285570&single=true&output=csv";

// Fungsi untuk mengambil data dari Google Sheets
async function fetchCSV() {
    try {
        const response = await fetch(proxyUrl + targetUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const csvText = await response.text();
        console.log("✅ Data Google Sheets berhasil diambil:", csvText.slice(0, 100)); // Cek bagian pertama CSV

        // Parsing CSV sederhana
        const rows = csvText.split("\n").map(row => row.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(col => col.replace(/(^"|"$)/g, '').trim()));
        console.log("✅ Header CSV:", rows[0]); // Debug header

        const headers = rows[0].map(header => header.trim().toLowerCase()); // Bersihkan spasi dan ubah ke huruf kecil
        const periodColumnIndex = headers.indexOf("periode");
        const gtColumnIndex = headers.indexOf("grt");
        const agentColumnIndex = headers.indexOf("nama agen");

        console.log("🔍 Indeks Kolom:", { periodColumnIndex, gtColumnIndex, agentColumnIndex });

        if (periodColumnIndex === -1 || gtColumnIndex === -1 || agentColumnIndex === -1) {
            console.error("⚠️ Kolom yang diperlukan tidak ditemukan dalam CSV!");
            console.error("📋 Header CSV:", headers);
            return;
        }

        const totalSurabaya = rows.length > 1 ? rows.length - 1 : 0;
        const totalGresik = Math.floor(totalSurabaya * 0.5);

        kirimEmail(totalSurabaya, totalGresik);
    } catch (error) {
        console.error("❌ Gagal mengambil data dari Google Sheets:", error);
    }
}

// Jalankan fetchCSV()
fetchCSV();
