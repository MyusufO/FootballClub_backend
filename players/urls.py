from django.urls import path

from players import views

app_name = 'players'

urlpatterns = [
    path('', views.PlayerListView.as_view(), name='player-list'),
    path('random/', views.RandomPlayerView.as_view(), name='player-random'),
    path('<int:player_id>/', views.PlayerDetailView.as_view(), name='player-detail'),
]
