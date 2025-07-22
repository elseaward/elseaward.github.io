from django.urls import path
from . import views

app_name = 'visualizer'

urlpatterns = [
    path('', views.landing, name='landing'),  # New landing page
    path('grapheme-color/', views.grapheme_color, name='grapheme_color'),  # Renamed from home
    path('sequence-space/', views.sequence_space, name='sequence_space'),  # New
    path('ticker-tape/', views.ticker_tape, name='ticker_tape'),  # New
    path('settings/', views.color_settings, name='color_settings'),
    path('save-colors/', views.save_colors, name='save_colors'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('switch-profile/<int:profile_id>/', views.switch_profile, name='switch_profile'),
    path('delete-profile/<int:profile_id>/', views.delete_profile, name='delete_profile'),
    path('get-colors-for-text/', views.get_colors_for_text, name='get_colors_for_text'),
    path('save-word-shading/', views.save_word_shading, name='save_word_shading'),
    path('save-bright-letters/', views.save_bright_letters, name='save_bright_letters'),
    path('faq/', views.faq, name='faq'),  # New FAQ page
    path('statistics/', views.color_statistics, name='color_statistics'),  # New URL for statistics
]