from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('teams/', views.team_list, name='team_list'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
    path('competitions/', views.competition_list, name='competition_list'),
    path('competitions/<int:pk>/', views.competition_detail, name='competition_detail'),
    path('statistics/', views.statistics, name='statistics'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search_player, name='search_player'),
    path('player/<int:pk>/id-card/', views.player_id_card_pdf, name='player_id_card'),

    # ADMIN PANEL
    path('panel/', views.admin_dashboard, name='admin_dashboard'),

    path('panel/news/', views.admin_news_list, name='admin_news_list'),
    path('panel/news/create/', views.admin_news_create, name='admin_news_create'),
    path('panel/news/<int:pk>/edit/', views.admin_news_edit, name='admin_news_edit'),
    path('panel/news/<int:pk>/delete/', views.admin_news_delete, name='admin_news_delete'),

    path('panel/teams/', views.admin_team_list, name='admin_team_list'),
    path('panel/teams/create/', views.admin_team_create, name='admin_team_create'),
    path('panel/teams/<int:pk>/edit/', views.admin_team_edit, name='admin_team_edit'),
    path('panel/teams/<int:pk>/delete/', views.admin_team_delete, name='admin_team_delete'),

    path('panel/players/', views.admin_player_list, name='admin_player_list'),
    path('panel/players/create/', views.admin_player_create, name='admin_player_create'),
    path('panel/players/<int:pk>/edit/', views.admin_player_edit, name='admin_player_edit'),
    path('panel/players/<int:pk>/delete/', views.admin_player_delete, name='admin_player_delete'),

    # Player requests (coach -> region admin)
    path('panel/player-requests/', views.admin_player_requests, name='admin_player_requests'),
    path('panel/player-requests/create/', views.admin_player_request_create, name='admin_player_request_create'),
    path('panel/player-requests/<int:pk>/review/', views.admin_player_request_review, name='admin_player_request_review'),

    path('panel/competitions/', views.admin_competition_list, name='admin_competition_list'),
    path('panel/competitions/create/', views.admin_competition_create, name='admin_competition_create'),
    path('panel/competitions/<int:pk>/edit/', views.admin_competition_edit, name='admin_competition_edit'),
    path('panel/competitions/<int:pk>/draw/', views.admin_competition_draw, name='admin_competition_draw'),
    path('panel/competitions/<int:pk>/scores/', views.admin_competition_scores, name='admin_competition_scores'),
    path('panel/competitions/<int:pk>/finish/', views.admin_competition_finish, name='admin_competition_finish'),
    path('panel/competitions/<int:pk>/next-round/', views.admin_competition_next_round, name='admin_competition_next_round'),

    path('panel/transfers/', views.admin_transfers, name='admin_transfers'),
    path('panel/transfers/create/', views.admin_transfer_create, name='admin_transfer_create'),
    path('panel/transfers/<int:pk>/accept/', views.admin_transfer_accept, name='admin_transfer_accept'),
    path('panel/transfers/<int:pk>/reject/', views.admin_transfer_reject, name='admin_transfer_reject'),

    path('panel/regions/', views.admin_regions, name='admin_regions'),
    path('panel/regions/create/', views.admin_region_create, name='admin_region_create'),
    path('panel/regions/<int:pk>/edit/', views.admin_region_edit, name='admin_region_edit'),
    path('panel/regions/<int:pk>/delete/', views.admin_region_delete, name='admin_region_delete'),
    path('panel/cities/', views.admin_cities, name='admin_cities'),
    path('panel/cities/create/', views.admin_city_create, name='admin_city_create'),
    path('panel/cities/<int:pk>/edit/', views.admin_city_edit, name='admin_city_edit'),
    path('panel/cities/<int:pk>/delete/', views.admin_city_delete, name='admin_city_delete'),
    path('panel/categories/', views.admin_categories, name='admin_categories'),
    path('panel/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('panel/categories/<int:pk>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('panel/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),
    path('panel/coaches/', views.admin_coaches, name='admin_coaches'),
    path('panel/coaches/create/', views.admin_coach_create, name='admin_coach_create'),
    path('panel/coaches/<int:pk>/delete/', views.admin_coach_delete, name='admin_coach_delete'),
    path('panel/stadiums/', views.admin_stadiums, name='admin_stadiums'),
    path('panel/stadiums/create/', views.admin_stadium_create, name='admin_stadium_create'),
    path('panel/stadiums/<int:pk>/edit/', views.admin_stadium_edit, name='admin_stadium_edit'),
    path('panel/stadiums/<int:pk>/delete/', views.admin_stadium_delete, name='admin_stadium_delete'),

    # Region admin management (superuser only)
    path('panel/region-admins/', views.admin_region_admins, name='admin_region_admins'),
    path('panel/region-admins/create/', views.admin_region_admin_create, name='admin_region_admin_create'),
    path('panel/region-admins/<int:pk>/delete/', views.admin_region_admin_delete, name='admin_region_admin_delete'),
]
