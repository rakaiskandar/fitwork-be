# fitwork-be
Fitwork adalah aplikasi berbasis AI yang berfungsi untuk melakukan penilaian kesesuaian budaya kerja (culture fit) secara otomatis berdasarkan Employee Value Proposition (EVP) perusahaan.

## Instalasi 
Clone project ini
```bash
git clone https://github.com/rakaiskandar/fitwork-be.git
```
Lalu, buat virtual environment di folder project kamu
```bash
virtualenv venv
```
atau
```bash
py -m venv venv
```
Aktifkan virtual environment di folder kamu\
untuk Linux/macOS:
```bash
source venv/bin/activate
```
untuk Windows:
```bash
venv\Scripts\activate
```
Setelah mengaktifkan virtual environment, install dependency atau library yang dibutuhkan
```bash 
pip install -r requirements.txt
```
Jika ingin menambahkan dependency atau library baru gunakan command:
```bash
pip install <nama-library> 
pip freeze > requirements.txt
```
Buat file `.env` dengan isian seperti `.env.example`
```bash
SECRET_KEY=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
``` 
