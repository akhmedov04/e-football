# ⚽ e-football (Django) — ichki hujjat

Bu fayl loyihaning ichki hujjati. GitHub uchun asosiy README repo root’da: `README.md`.

## 🧩 Rollar

- **Admin (superuser)**: hamma bo'limlarga to'liq ruxsat.
- **Viloyat admin (RegionAdmin)**: o'z viloyati doirasidagi jamoa/stadion/musobaqa va player requestlarni boshqaradi.
- **Coach**: o'z jamoasi o'yinchilari, player request, transferlar.

## 🔁 Asosiy oqimlar

### Player request (coach → viloyat admin)

1. Coach `/panel/player-requests/create/` orqali o'yinchi so'rovi yuboradi.
2. Viloyat admin so'rovni ko'rib chiqadi:
   - **Approve** → `PlayerRequest.approve()` orqali `Player` yaratiladi, status `accepted`.
   - **Reject** → status `rejected`, `admin_note` saqlanadi.

### Musobaqa

- **`round_robin`**: barcha jamoalar o'zaro o'ynaydi; `Competition.get_standings()` jadvalni hisoblaydi.
- **`olympic`**: `generate_draw()` juftlab match yaratadi; keyingi raund `admin_competition_next_round` orqali g'oliblardan tuziladi.

### Transfer

- Coach transfer so'rovi yuboradi → qabul qilinsa `TransferRequest.accept()` o'yinchining `team`ini yangilaydi.

## 🧪 Demo data (`seed_data`)

`python manage.py seed_data` quyidagilarni yaratadi:
- `admin / admin123`
- `radmin1..radmin3 / radmin123`
- `coach1..coach8 / coach123`
