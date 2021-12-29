from django.urls import path
from . import views

urlpatterns = [

path('profile/<str:username>', views.profile_page, name='profile'),
    path('learning/', views.learning_page, name='learning'),
    path('analytics/', views.analytics_page, name='analytics'),

    path('settings/<str:pk>', views.settings_page, name='settings'),
    path('edit-card/<str:pk>', views.edit_card_page, name='edit-card'),

    path('create-deck/', views.create_deck, name='create-deck'),
    path('learn-deck/<str:pk>/', views.learn_deck, name='learn-deck'),
    path('add-card/<str:pk>/', views.add_card, name='add-card'),
    path('passed-deck/<str:pk>/', views.passed_deck, name='passed-deck'),
    path('search-deck/', views.search_deck, name='search-deck'),
    path('select-deck/<str:pk>/', views.select_deck, name='select-deck'),

    path('search-friends/', views.search_friend, name='search-friend'),
    path('messages/', views.messages_page, name='messages'),
    path('write-message/', views.write_message, name='write-message'),
    path('read-message/<str:pk>/', views.read_message, name='read-message'),

]