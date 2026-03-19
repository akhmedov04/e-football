from django.db import models
from django.contrib.auth.models import User
import random


# =========================
# LOCATION
# =========================

class Region(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")

    class Meta:
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cities", verbose_name="Viloyat")

    class Meta:
        verbose_name = "Shahar"
        verbose_name_plural = "Shaharlar"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


# =========================
# CATEGORY
# =========================

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']

    def __str__(self):
        return self.name


# =========================
# REGION ADMIN (Viloyat admini)
# =========================

class RegionAdmin(models.Model):
    """Viloyat bo'yicha admin — faqat o'z viloyatidagi jamoalar, stadionlar, musobaqalarni boshqaradi."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="region_admin_profile", verbose_name="Foydalanuvchi")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="admins", verbose_name="Viloyat")
    first_name = models.CharField(max_length=255, verbose_name="Ismi")
    last_name = models.CharField(max_length=255, verbose_name="Familiyasi")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")

    class Meta:
        verbose_name = "Viloyat admini"
        verbose_name_plural = "Viloyat adminlari"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.region.name})"


# =========================
# COACH
# =========================

class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="coach_profile", verbose_name="Foydalanuvchi", null=True, blank=True)
    first_name = models.CharField(max_length=255, verbose_name="Ismi")
    last_name = models.CharField(max_length=255, verbose_name="Familiyasi")
    fathers_name = models.CharField(max_length=255, blank=True, verbose_name="Otasining ismi")
    photo = models.ImageField(upload_to="coach_photos/", blank=True, null=True, verbose_name="Rasm")

    class Meta:
        verbose_name = "Murabbiy"
        verbose_name_plural = "Murabbiylar"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# =========================
# TEAM
# =========================

class Team(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    logo = models.ImageField(upload_to="team_logos/", blank=True, null=True, verbose_name="Logotip")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    coach = models.OneToOneField(Coach, on_delete=models.SET_NULL, null=True, blank=True, related_name="team", verbose_name="Murabbiy")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="teams", verbose_name="Shahar")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="teams", verbose_name="Kategoriya")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Jamoa"
        verbose_name_plural = "Jamoalar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_players_by_position(self):
        positions = {}
        for player in self.players.all().order_by('position', 'last_name'):
            pos = player.get_position_display() if player.position else "Boshqa"
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(player)
        return positions


# =========================
# PLAYER
# =========================

class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Darvozabon'),
        ('DEF', 'Himoyachi'),
        ('MID', 'Yarim himoyachi'),
        ('FWD', 'Hujumchi'),
    ]

    player_id = models.CharField(max_length=20, unique=True, blank=True, verbose_name="O'yinchi ID")
    first_name = models.CharField(max_length=255, verbose_name="Ismi")
    last_name = models.CharField(max_length=255, verbose_name="Familiyasi")
    fathers_name = models.CharField(max_length=255, blank=True, verbose_name="Otasining ismi")
    photo = models.ImageField(upload_to="player_photos/", blank=True, null=True, verbose_name="Rasm")
    height = models.FloatField(blank=True, null=True, verbose_name="Bo'yi (sm)")
    weight = models.FloatField(blank=True, null=True, verbose_name="Vazni (kg)")
    birthday = models.DateField(verbose_name="Tug'ilgan sana")
    jersey_number = models.PositiveIntegerField(blank=True, null=True, verbose_name="Futbolka raqami")
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, blank=True, verbose_name="Pozitsiya")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players", verbose_name="Jamoa")

    class Meta:
        verbose_name = "O'yinchi"
        verbose_name_plural = "O'yinchilar"
        ordering = ['position', 'last_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def save(self, *args, **kwargs):
        if not self.player_id:
            while True:
                pid = str(random.randint(10000, 99999))
                if not Player.objects.filter(player_id=pid).exists():
                    self.player_id = pid
                    break
        super().save(*args, **kwargs)

    def get_position_display(self):
        return dict(self.POSITION_CHOICES).get(self.position, self.position or "Boshqa")


# =========================
# PLAYER REQUEST (Coach → Viloyat admin tasdiqlashi kerak)
# =========================

class PlayerRequest(models.Model):
    """Coach yangi o'yinchi qo'shmoqchi — viloyat admini tasdiqlaydi/rad etadi/tahrirlaydi."""
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('accepted', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]

    first_name = models.CharField(max_length=255, verbose_name="Ismi")
    last_name = models.CharField(max_length=255, verbose_name="Familiyasi")
    fathers_name = models.CharField(max_length=255, blank=True, verbose_name="Otasining ismi")
    photo = models.ImageField(upload_to="player_request_photos/", blank=True, null=True, verbose_name="Rasm")
    height = models.FloatField(blank=True, null=True, verbose_name="Bo'yi (sm)")
    weight = models.FloatField(blank=True, null=True, verbose_name="Vazni (kg)")
    birthday = models.DateField(verbose_name="Tug'ilgan sana")
    jersey_number = models.PositiveIntegerField(blank=True, null=True, verbose_name="Futbolka raqami")
    position = models.CharField(max_length=10, choices=Player.POSITION_CHOICES, blank=True, verbose_name="Pozitsiya")

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="player_requests", verbose_name="Jamoa")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player_requests", verbose_name="Yuboruvchi (Coach)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    admin_note = models.TextField(blank=True, verbose_name="Admin izohi")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="request", verbose_name="Yaratilgan o'yinchi")

    class Meta:
        verbose_name = "O'yinchi so'rovi"
        verbose_name_plural = "O'yinchi so'rovlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.last_name} {self.first_name} → {self.team} ({self.get_status_display()})"

    def approve(self):
        """Tasdiqlash — Player yaratish."""
        from django.utils import timezone
        p = Player.objects.create(
            first_name=self.first_name, last_name=self.last_name,
            fathers_name=self.fathers_name, photo=self.photo,
            height=self.height, weight=self.weight,
            birthday=self.birthday, jersey_number=self.jersey_number,
            position=self.position, team=self.team,
        )
        self.player = p
        self.status = 'accepted'
        self.reviewed_at = timezone.now()
        self.save()
        return p

    def reject(self, note=''):
        from django.utils import timezone
        self.status = 'rejected'
        self.admin_note = note
        self.reviewed_at = timezone.now()
        self.save()


# =========================
# STADIUM
# =========================

class Stadium(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="stadiums", verbose_name="Shahar")

    class Meta:
        verbose_name = "Stadion"
        verbose_name_plural = "Stadionlar"

    def __str__(self):
        return f"{self.name} ({self.city.region.name})"


# =========================
# COMPETITION
# =========================

class Competition(models.Model):
    COMP_TYPES = [
        ('olympic', 'Olimpik tizim'),
        ('round_robin', 'Doiraviy tizim'),
    ]

    name = models.CharField(max_length=255, verbose_name="Nomi")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="competitions", verbose_name="Kategoriya")
    type = models.CharField(max_length=20, choices=COMP_TYPES, verbose_name="Turi")
    date = models.DateField(verbose_name="Sana")
    stadium = models.ForeignKey(Stadium, on_delete=models.SET_NULL, null=True, blank=True, related_name="competitions", verbose_name="Stadion")
    teams = models.ManyToManyField(Team, related_name="competitions", blank=True, verbose_name="Jamoalar")
    is_finished = models.BooleanField(default=False, verbose_name="Yakunlangan")
    draw_done = models.BooleanField(default=False, verbose_name="Qur'a tashlangan")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Yaratuvchi")

    class Meta:
        verbose_name = "Musobaqa"
        verbose_name_plural = "Musobaqalar"
        ordering = ['-date']

    def __str__(self):
        return self.name

    def generate_draw(self):
        if self.draw_done:
            return
        team_list = list(self.teams.all())
        random.shuffle(team_list)
        self.matches.all().delete()

        if self.type == 'round_robin':
            for i in range(len(team_list)):
                for j in range(i + 1, len(team_list)):
                    Match.objects.create(competition=self, team_home=team_list[i], team_away=team_list[j], round_number=1)
        elif self.type == 'olympic':
            i = 0
            while i < len(team_list) - 1:
                Match.objects.create(competition=self, team_home=team_list[i], team_away=team_list[i + 1], round_number=1)
                i += 2
            if len(team_list) % 2 == 1:
                Match.objects.create(competition=self, team_home=team_list[-1], team_away=team_list[-1],
                                     round_number=1, score_home=0, score_away=0, is_finished=True, is_bye=True)
        self.draw_done = True
        self.save()

    def get_standings(self):
        if self.type != 'round_robin':
            return []
        standings = {}
        for team in self.teams.all():
            standings[team.id] = {'team': team, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0, 'goals_for': 0, 'goals_against': 0, 'points': 0}

        for m in self.matches.filter(is_finished=True, is_bye=False):
            for tid, sf, sa in [(m.team_home_id, m.score_home or 0, m.score_away or 0), (m.team_away_id, m.score_away or 0, m.score_home or 0)]:
                if tid in standings:
                    s = standings[tid]
                    s['played'] += 1; s['goals_for'] += sf; s['goals_against'] += sa
                    if sf > sa: s['won'] += 1; s['points'] += 3
                    elif sf == sa: s['drawn'] += 1; s['points'] += 1
                    else: s['lost'] += 1

        result = sorted(standings.values(), key=lambda x: (x['points'], x['goals_for'] - x['goals_against'], x['goals_for']), reverse=True)
        for row in result:
            row['goal_diff'] = row['goals_for'] - row['goals_against']
        return result

    def get_olympic_rounds(self):
        if self.type != 'olympic':
            return {}
        rounds = {}
        for match in self.matches.all().order_by('round_number'):
            rounds.setdefault(match.round_number, []).append(match)
        return dict(sorted(rounds.items()))


# =========================
# MATCH
# =========================

class Match(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="matches")
    team_home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team_away = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    score_home = models.PositiveIntegerField(null=True, blank=True)
    score_away = models.PositiveIntegerField(null=True, blank=True)
    round_number = models.PositiveIntegerField(default=1)
    is_finished = models.BooleanField(default=False)
    is_bye = models.BooleanField(default=False)
    match_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "O'yin"
        verbose_name_plural = "O'yinlar"

    def __str__(self):
        if self.is_bye:
            return f"{self.team_home} (BYE)"
        score = f" ({self.score_home}:{self.score_away})" if self.is_finished else ""
        return f"{self.team_home} vs {self.team_away}{score}"

    def get_winner(self):
        if not self.is_finished:
            return None
        if self.is_bye:
            return self.team_home
        if (self.score_home or 0) > (self.score_away or 0):
            return self.team_home
        elif (self.score_away or 0) > (self.score_home or 0):
            return self.team_away
        return None


# =========================
# NEWS
# =========================

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    text = models.TextField(verbose_name="Matn")
    short_text = models.CharField(max_length=500, blank=True, verbose_name="Qisqa matn")
    date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-date', '-id']

    def __str__(self):
        return self.title

    def get_first_photo(self):
        photo = self.photos.first()
        return photo.file.url if photo else None


class NewsPhoto(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="photos")
    file = models.ImageField(upload_to="news_photos/")

    def __str__(self):
        return f"Rasm: {self.news.title}"


class TransferRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Kutilmoqda'), ('accepted', 'Qabul qilindi'), ('rejected', 'Rad etildi')]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="transfer_requests")
    from_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="outgoing_transfers")
    to_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="incoming_transfers")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.player} -> {self.to_team} ({self.get_status_display()})"

    def accept(self):
        self.player.team = self.to_team
        self.player.save()
        self.status = 'accepted'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()


class Document(models.Model):
    DOC_TYPES = [('passport', 'Pasport'), ('license', 'Litsenziya'), ('medical', 'Tibbiy'), ('other', 'Boshqa')]
    file = models.FileField(upload_to="documents/")
    document_type = models.CharField(max_length=50, choices=DOC_TYPES)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="documents", null=True, blank=True)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="documents", null=True, blank=True)

    def __str__(self):
        return f"{self.get_document_type_display()}"
