from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    News, Team, Player, Competition, Match, TransferRequest,
    Region, City, Category, Coach, Stadium, RegionAdmin, PlayerRequest
)


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Foydalanuvchi nomi'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Parol'}))


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'short_text', 'text']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'short_text': forms.TextInput(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 8}),
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'logo', 'description', 'coach', 'city', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'coach': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'fathers_name', 'photo',
                  'height', 'weight', 'birthday', 'jersey_number', 'position', 'team']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'fathers_name': forms.TextInput(attrs={'class': 'form-input'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'birthday': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}, format='%Y-%m-%d'),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-input'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'team': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.birthday:
            self.initial['birthday'] = self.instance.birthday.strftime('%Y-%m-%d')


class PlayerRequestForm(forms.ModelForm):
    """Coach o'yinchi so'rovi uchun form — team avtomatik coach jamoasidan olinadi."""
    class Meta:
        model = PlayerRequest
        fields = ['first_name', 'last_name', 'fathers_name', 'photo',
                  'height', 'weight', 'birthday', 'jersey_number', 'position']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'fathers_name': forms.TextInput(attrs={'class': 'form-input'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'birthday': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-input'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
        }


class PlayerRequestEditForm(forms.ModelForm):
    """Viloyat admin so'rovni edit qilish uchun — xatoni to'g'irlab tasdiqlaydi."""
    class Meta:
        model = PlayerRequest
        fields = ['first_name', 'last_name', 'fathers_name', 'photo',
                  'height', 'weight', 'birthday', 'jersey_number', 'position', 'admin_note']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'fathers_name': forms.TextInput(attrs={'class': 'form-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'birthday': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}, format='%Y-%m-%d'),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-input'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'admin_note': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Izoh (ixtiyoriy)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Date field formatni to'g'ri ko'rsatish uchun
        if self.instance and self.instance.birthday:
            self.initial['birthday'] = self.instance.birthday.strftime('%Y-%m-%d')


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['name', 'category', 'type', 'date', 'stadium', 'teams']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'stadium': forms.Select(attrs={'class': 'form-select'}),
            'teams': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, region=None, **kwargs):
        """region berilsa — faqat shu viloyat stadionlari filtrlandi, jamoalar hammasi ko'rinadi."""
        super().__init__(*args, **kwargs)
        self.fields['stadium'].required = True
        self.fields['teams'].required = True
        if region:
            self.fields['stadium'].queryset = Stadium.objects.filter(city__region=region)

    def clean_teams(self):
        teams = self.cleaned_data.get('teams')
        if not teams or teams.count() < 2:
            raise forms.ValidationError("Kamida 2 ta jamoa tanlang!")
        return teams


class TransferRequestForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.none(), widget=forms.Select(attrs={'class': 'form-select'}), label="O'yinchi")
    to_team = forms.ModelChoiceField(queryset=Team.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}), label="Yangi jamoa")
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}), required=False, label="Xabar")

    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        if team:
            self.fields['player'].queryset = Player.objects.filter(team=team)
            self.fields['to_team'].queryset = Team.objects.exclude(id=team.id)


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-input'})}


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'region']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-input'}), 'region': forms.Select(attrs={'class': 'form-select'})}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-input'})}


class CoachForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = ['first_name', 'last_name', 'fathers_name', 'photo', 'user']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'fathers_name': forms.TextInput(attrs={'class': 'form-input'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
        }


class StadiumForm(forms.ModelForm):
    class Meta:
        model = Stadium
        fields = ['name', 'city']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-input'}), 'city': forms.Select(attrs={'class': 'form-select'})}

    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, **kwargs)
        if region:
            self.fields['city'].queryset = City.objects.filter(region=region)


class RegionAdminForm(forms.ModelForm):
    """Superuser viloyat admin tayinlash uchun."""

    class Meta:
        model = RegionAdmin
        fields = ['first_name', 'last_name', 'phone', 'region']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
        }


class CoachCreateForm(forms.Form):
    """Superuser/region admin coach yaratish uchun — user ham yaratiladi."""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}), label="Login")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}), label="Parol")
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}), label="Ismi")
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}), label="Familiyasi")
    fathers_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}), required=False, label="Otasining ismi")
    photo = forms.ImageField(required=False, label="Rasm")
    team = forms.ModelChoiceField(queryset=Team.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}), label="Jamoa", required=False)

    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, **kwargs)
        if region:
            self.fields['team'].queryset = Team.objects.filter(city__region=region)
