# ⚽ e-football (Django)

O'zbekiston futboli uchun demo veb-loyiha: public sahifalar + custom admin panel (`/panel/`) + Django admin (`/django-admin/`).

## 🚀 Ishga tushirish (Windows)

```bash
# 1) Virtual muhit (repo ichida .venv bo'lsa shuni ishlating)
.\.venv\Scripts\activate

# 2) Kutubxonalar
python -m pip install -r .\football_project\requirements.txt

# 3) Env (ixtiyoriy, tavsiya qilinadi)
copy .env.example .env
set DJANGO_SECRET_KEY=change-me
set DJANGO_DEBUG=1
set DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# 4) DB
cd .\football_project
python manage.py migrate

# 5) Demo data (superuser + coachlar)
python manage.py seed_data

# 6) Server
python manage.py runserver 127.0.0.1:8000
```

## 🔗 Linklar

- Public: `http://127.0.0.1:8000/`
- Panel: `http://127.0.0.1:8000/panel/`
- Django admin: `http://127.0.0.1:8000/django-admin/`

## 👤 Demo login

| Rol | Username | Parol |
|-----|----------|-------|
| Admin | `admin` | `admin123` |
| Coach | `coach1`...`coach8` | `coach123` |

## 📋 Funksiyalar (qisqa)

- **Public**: yangiliklar, jamoalar (filter/pagination), musobaqalar (round-robin/olimpik), o'yinchi qidirish, ID-card PDF.
- **Panel**: CRUD (news/teams/players/competitions), player request (coach → region admin), transferlar, region/city/category/stadium/coach boshqaruvi.

---

Ichki loyiha hujjati: `football_project/README.md`
