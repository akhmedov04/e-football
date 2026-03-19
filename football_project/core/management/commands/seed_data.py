from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import *
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Demo ma'lumotlarni yaratish"

    def handle(self, *args, **options):
        # SUPERUSER
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser: admin / admin123'))

        # REGIONS & CITIES
        regions_data = {
            "Toshkent": ["Toshkent shahri", "Chirchiq", "Olmaliq"],
            "Samarqand": ["Samarqand shahri", "Kattaqo'rg'on"],
            "Farg'ona": ["Farg'ona shahri", "Marg'ilon", "Qo'qon"],
            "Buxoro": ["Buxoro shahri", "Kogon"],
            "Andijon": ["Andijon shahri", "Asaka"],
        }
        for rname, cities in regions_data.items():
            r, _ = Region.objects.get_or_create(name=rname)
            for cname in cities:
                City.objects.get_or_create(name=cname, region=r)
        self.stdout.write(self.style.SUCCESS('Viloyatlar va shaharlar yaratildi'))

        # CATEGORIES
        for c in ["Kattalar", "Yoshlar U-21", "O'smirlar U-17", "Bolalar U-14"]:
            Category.objects.get_or_create(name=c)

        # STADIUMS
        cities_all = list(City.objects.all())
        for i, sn in enumerate(["Milliy stadion", "Lokomotiv arena", "Bunyodkor stadioni", "Zarafshon stadioni", "Farg'ona stadioni", "Andijon stadioni"]):
            Stadium.objects.get_or_create(name=sn, defaults={'city': cities_all[i % len(cities_all)]})

        # REGION ADMINS - jamoalar joylashgan viloyatlarga admin tayinlash
        region_names = ["Toshkent", "Samarqand", "Farg'ona"]
        for i, rname in enumerate(region_names):
            r = Region.objects.filter(name=rname).first()
            if not r: continue
            un = f"radmin{i+1}"
            u, created = User.objects.get_or_create(username=un)
            if created:
                u.set_password('radmin123')
                u.save()
            RegionAdmin.objects.get_or_create(user=u, defaults={
                'region': r, 'first_name': f"Admin{i+1}", 'last_name': r.name
            })
            self.stdout.write(self.style.SUCCESS(f'Viloyat admin: {un} / radmin123 ({r.name})'))

        # COACHES & TEAMS
        kattalar = Category.objects.get(name="Kattalar")
        yoshlar = Category.objects.get(name="Yoshlar U-21")
        coach_data = [
            ("Mirjalol", "Qosimov", "Toshkent shahri", kattalar, "Bunyodkor"),
            ("Shota", "Arveladze", "Toshkent shahri", kattalar, "Paxtakor"),
            ("Samvel", "Babayan", "Toshkent shahri", kattalar, "Lokomotiv"),
            ("Ruzikul", "Berdiyev", "Buxoro shahri", kattalar, "Nasaf"),
            ("Andrey", "Miklyayev", "Farg'ona shahri", kattalar, "Navbahor"),
            ("Oleg", "Kubarev", "Andijon shahri", kattalar, "Andijon FK"),
            ("Ilhom", "Murodov", "Samarqand shahri", yoshlar, "Dinamo"),
            ("Faxriddin", "Tadjiyev", "Samarqand shahri", yoshlar, "Sogdiana"),
        ]
        for i, (fn, ln, cname, cat, tname) in enumerate(coach_data):
            un = f"coach{i+1}"
            u, created = User.objects.get_or_create(username=un)
            if created:
                u.set_password('coach123')
                u.save()
            coach, _ = Coach.objects.get_or_create(first_name=fn, last_name=ln, defaults={'user': u})
            city = City.objects.filter(name=cname).first() or cities_all[0]
            team, _ = Team.objects.get_or_create(name=tname, defaults={'city': city, 'category': cat, 'coach': coach})
            self.stdout.write(self.style.SUCCESS(f'Coach: {un} / coach123 → {tname}'))

        # PLAYERS
        positions = ['GK', 'DEF', 'DEF', 'DEF', 'DEF', 'MID', 'MID', 'MID', 'MID', 'FWD', 'FWD']
        fnames = ["Eldor", "Sardor", "Dostonbek", "Jaloliddin", "Islom", "Otabek", "Aziz", "Bobur", "Jamshid", "Firdavs", "Ulugbek", "Sanjar", "Temur", "Sherzod", "Nodir"]
        lnames = ["Shomurodov", "Rashidov", "Hamdamov", "Masharipov", "Tukhtasinov", "Ashurmatov", "Ganiev", "Abdullaev", "Yaxshiboev", "Komilov", "Ahmedov", "Ibragimov", "Normatov", "Urunov", "Hasanov"]

        for team in Team.objects.all():
            if team.players.exists(): continue
            for j in range(11):
                Player.objects.create(
                    first_name=random.choice(fnames), last_name=random.choice(lnames),
                    birthday=date(random.randint(1995, 2005), random.randint(1, 12), random.randint(1, 28)),
                    height=round(random.uniform(168, 195), 1), weight=round(random.uniform(65, 90), 1),
                    position=positions[j], jersey_number=j + 1, team=team,
                )
        self.stdout.write(self.style.SUCCESS("O'yinchilar yaratildi"))

        # NEWS
        for title in ["Bunyodkor yangi mavsum uchun tayyorlanmoqda", "Paxtakor xalqaro turnirda g'olib chiqdi", "Yoshlar ligasi natijalari e'lon qilindi",
                       "Milliy terma jamoa yangi bosh murabbiyni tanladi", "O'zbekiston futbol federatsiyasi yangiliklar", "Superliga 2025 mavsumi taqvimi tasdiqlandi",
                       "Yangi stadion qurilishi boshlandi", "Transfer oynasi: Kim qayerga ketdi?", "Yoshlarni rivojlantirish dasturi", "Buxoroda yangi futbol akademiyasi ochildi"]:
            News.objects.get_or_create(title=title, defaults={'text': f"Bu {title.lower()} haqida batafsil ma'lumot.", 'short_text': f"{title} — batafsil..."})

        # COMPETITIONS
        today = date.today()
        stadiums = list(Stadium.objects.all())
        teams = list(Team.objects.all())
        comp1, cr = Competition.objects.get_or_create(name="Superliga 2025", defaults={'category': kattalar, 'type': 'round_robin', 'date': today + timedelta(days=5), 'stadium': stadiums[0] if stadiums else None})
        if cr: comp1.teams.set(teams[:4])
        comp2, cr = Competition.objects.get_or_create(name="O'zbekiston kubogi 2024", defaults={'category': kattalar, 'type': 'olympic', 'date': today - timedelta(days=30), 'stadium': stadiums[1] if len(stadiums) > 1 else None, 'is_finished': True, 'draw_done': True})
        if cr:
            comp2.teams.set(teams[:4])
            Match.objects.create(competition=comp2, team_home=teams[0], team_away=teams[1], score_home=2, score_away=1, round_number=1, is_finished=True)
            Match.objects.create(competition=comp2, team_home=teams[2], team_away=teams[3], score_home=0, score_away=3, round_number=1, is_finished=True)
            Match.objects.create(competition=comp2, team_home=teams[0], team_away=teams[3], score_home=1, score_away=0, round_number=2, is_finished=True)

        self.stdout.write(self.style.SUCCESS('\n=== BARCHA MA\'LUMOTLAR YARATILDI ==='))
        self.stdout.write(self.style.WARNING('\nLogin ma\'lumotlari:'))
        self.stdout.write('  Sayt admini:     admin / admin123')
        self.stdout.write('  Viloyat adminlar: radmin1 / radmin123 (Toshkent), radmin2 / radmin123 (Samarqand), radmin3 / radmin123 (Farg\'ona)')
        self.stdout.write('  Coachlar:        coach1...coach8 / coach123')
