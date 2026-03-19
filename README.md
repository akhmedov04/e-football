# ⚽ e-football (Django)

O'zbekiston futboli uchun demo veb-loyiha: **public sahifalar** + **custom panel** (`/panel/`) + **Django admin** (`/django-admin/`).

## 🚀 Ishga tushirish (Windows / PowerShell)

Repo root papkada (`e_futbol`) quyidagilarni bajaring.

```powershell
# 1) Virtual muhit
.\.venv\Scripts\Activate.ps1

# 2) Kutubxonalar
python -m pip install -r .\football_project\requirements.txt

# 3) Env (ixtiyoriy, tavsiya qilinadi)
Copy-Item .env.example .env
$env:DJANGO_SECRET_KEY = "change-me"
$env:DJANGO_DEBUG = "1"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"

# 4) DB va demo data
cd .\football_project
python manage.py migrate
python manage.py seed_data

# 5) Server
python manage.py runserver 127.0.0.1:8000
```

## 🔗 Linklar

- Public: `http://127.0.0.1:8000/`
- Panel: `http://127.0.0.1:8000/panel/`
- Django admin: `http://127.0.0.1:8000/django-admin/`

## 👤 Demo login (seed_data’dan keyin)

| Rol | Username | Parol | Izoh |
|-----|----------|-------|------|
| Admin | `admin` | `admin123` | To'liq boshqaruv |
| Viloyat admin | `radmin1..radmin3` | `radmin123` | Region bo'yicha cheklangan boshqaruv |
| Coach | `coach1..coach8` | `coach123` | O'z jamoasi: so'rov/transferlar |

## 📋 Funksiyalar (qisqa)

- **Public**: yangiliklar, jamoalar (filter/pagination), musobaqalar (round-robin/olimpik), o'yinchi qidirish, ID-card PDF.
- **Panel**: CRUD (news/teams/players/competitions), **player request** (coach → viloyat admin), transferlar, region/city/category/stadium/coach boshqaruvi.

## 📁 Struktura

- `football_project/` — Django project (manage.py shu yerda)
- `football_project/core/` — asosiy app (models/views/forms)
- `football_project/templates/` — sahifalar
- `football_project/static/` — CSS

---

Batafsil: `football_project/README.md`
