# fitwork-be
Fitwork adalah aplikasi berbasis AI yang berfungsi untuk melakukan penilaian kesesuaian budaya kerja (culture fit) secara otomatis berdasarkan Employee Value Proposition (EVP) perusahaan. Proyek ini merupakan backend service yang dibangun menggunakan Django.

## Daftar Isi
* [Deskripsi](#fitwork-be)
* [Teknologi yang Digunakan](#teknologi-yang-digunakan)
* [Fitur Utama](#fitur-utama)
* [Prasyarat](#prasyarat)
* [Struktur Folder](#struktur-folder)
* [Instalasi](#instalasi)
* [Konfigurasi Environment](#konfigurasi-environment)
* [Menjalankan Aplikasi](#menjalankan-aplikasi)
* [Credit](#credit)

## Teknologi yang Digunakan
* **Backend Framework:** Django
* **Bahasa Pemrograman:** Python
* **Database:** PostgreSQL
* **AI/Machine Learning:** Google Gemini API, Langchain

## Fitur Utama
* **Autentikasi Pengguna:**
    * Registrasi pengguna baru
    * Login pengguna
    * Logout pengguna
    * Manajemen token (access & refresh token)
    * Registrasi admin perusahaan
* **Penilaian Culture Fit Berbasis AI:**
    * Memproses Employee Value Proposition (EVP) perusahaan.
    * Melakukan penilaian kesesuaian budaya kerja calon karyawan atau karyawan secara otomatis menggunakan input teks dan Gemini API.
    * Membandingkan hasil penilaian kesesuaian budaya kerja kandidat.
    * Mengevaluasi hasil penilaian kesesuaian budaya kerja kandidat.
* **Konsultasi Karir dengan AI:**
    * Konsultasi dengan AI yang sudah disesuaikan untuk dapat menjawab tentang perihal karir secara spesifik
* **Manajemen Data:**
    * Pengelolaan data perusahaan dan EVP-nya.
    * Penyimpanan dan pengambilan hasil penilaian.

## Prasyarat
Sebelum memulai, pastikan sistem Anda telah terinstal:
* Python (versi 3.8+ direkomendasikan)
* pip (Python package installer)
* virtualenv (atau modul `venv` bawaan Python 3)
* PostgreSQL (server sudah berjalan dan terkonfigurasi)
* Git

## Struktur Folder 
Berikut adalah struktur folder yang digunakan dalam proyek ini.

```tree
fitwork-be/
├── .gitignore
├── manage.py                     # Utilitas baris perintah Django
├── requirements.txt              # Daftar pustaka Python yang dibutuhkan
├── .env                          # Variabel lingkungan (lokal, jangan di-commit)
├── .env.example                  # Contoh variabel lingkungan
│
├── config/                       # Direktori konfigurasi utama proyek Django
│   ├── asgi.py                   # Konfigurasi ASGI untuk server asinkron
│   ├── settings.py               # Pengaturan utama proyek Django
│   ├── urls.py                   # Definisi URL utama tingkat proyek
│   └── wsgi.py                   # Konfigurasi WSGI untuk server sinkron
│
├── api/                          # Direktori utama aplikasi utama Django 
│   ├── users                     # Direktori aplikasi untuk manajemen users
│   │    ├── admin.py             # Konfigurasi model untuk antarmuka admin Django
│   │    ├── apps.py              # Konfigurasi aplikasi 'users'
│   │    ├── models.py            # Definisi model data
│   │    ├── serializers.py       # Serializer untuk konversi data model ke JSON (jika pakai DRF)
│   │    ├── views.py             # Logika untuk menangani permintaan API (misal: registrasi, login)
│   │    ├── urls.py              # Definisi URL spesifik untuk aplikasi 'users'
│   │    └── migrations/          # Direktori untuk skema migrasi basis data
│   │        └── ...
│   ├── companies/                # Direktori aplikasi untuk manajemen companies
|   │   ├── ...                   (sama seperti users) 
│   ├── assessments/              # Direktori aplikasi untuk manajemen assessments atau penilaian
|   │   ├── .../                  
│   ├── chatbot/                  # Direktori aplikasi untuk manajemen chatbot
|   │   ├── .../                   
│   ├── common/                   # Direktori aplikasi untuk reusable function
└── data/                  # Knowledge untuk AI (json)
└── media/                 # File yang diunggah pengguna
```

## Instalasi

1.  **Clone repository ini:**
    ```bash
    git clone https://github.com/rakaiskandar/fitwork-be.git
    cd fitwork-be
    ```

2.  **Buat dan aktifkan virtual environment:**
    Disarankan menggunakan `venv` yang merupakan bagian dari Python 3:
    ```bash
    python -m venv venv
    ```
    Atau jika Anda lebih memilih `virtualenv`:
    ```bash
    virtualenv venv
    ```
    Aktifkan virtual environment:
    * Linux/macOS:
        ```bash
        source venv/bin/activate
        ```
    * Windows:
        ```bash
        venv\Scripts\activate
        ```

3.  **Install dependencies:**
    Pastikan virtual environment sudah aktif, lalu install library yang dibutuhkan:
    ```bash
    pip install -r requirements.txt
    ```
    Jika ingin menambahkan dependency atau library baru, jalankan:
    ```bash
    pip install <nama-library>
    ```
    Kemudian, perbarui file `requirements.txt`:
    ```bash
    pip freeze > requirements.txt
    ```
    *Catatan: Pastikan direktori `venv/` dan file `.env` sudah ditambahkan ke dalam `.gitignore` Anda untuk menghindari commit yang tidak perlu.*

## Konfigurasi Environment

1.  Buat file `.env` di root folder proyek.
2.  Salin konten dari `.env.example` (jika ada) atau isi dengan variabel berikut (sesuaikan nilainya):
    ```env
    SECRET_KEY=your_django_secret_key_here
    POSTGRES_DB=fitwork_db
    POSTGRES_USER=fitwork_user
    POSTGRES_PASSWORD=your_postgres_password
    GEMINI_API_KEY=your_google_gemini_api_key_here
    ```
    * Untuk `SECRET_KEY`, Anda bisa membuatnya sendiri (string acak yang panjang dan kompleks) atau menggunakan generator online.
    * Pastikan database PostgreSQL dengan nama yang Anda tentukan di `POSTGRES_DB` sudah dibuat dan user `POSTGRES_USER` memiliki hak akses ke database tersebut.
    * Untuk `GEMINI_API_KEY`, dapatkan dari [Console Google Cloud](https://console.cloud.google.com/).

## Menjalankan Aplikasi

1.  **Lakukan migrasi database:**
    Pastikan file `.env` sudah terisi dengan benar dan virtual environment aktif.
    ```bash
    py manage.py migrate
    ```

2.  **Jalankan server backend:**
    ```bash
    py manage.py runserver
    ```
    Secara default, server akan berjalan di `http://127.0.0.1:8000/`.

## Credit
* **Dosen Pengampu:** Yuli Sopianti S. Pd, M. Kom
* **Kelompok 8:**
    * Ellyazar Swastiko - 2309749 - UI/UX Designer
    * Ma'rifatu Ambiya - 2300822 - Frontend Developer
    * Muhammad Rivalby - 2307068 - Frontend Developer
    * Raka Iskandar - 2306068 - Backend Developer