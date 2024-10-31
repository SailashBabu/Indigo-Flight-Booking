# flights/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),  # Home page - Flight Search  # Booking a flight
    path('my-bookings/', views.my_bookings, name='my_bookings'), 
    path('search-flights/', views.search_flights, name='search_flights'), # View user's bookings
    path('passenger-details/', views.passenger_details, name='passenger_details'),
    path('select-seats/', views.select_seats, name='select_seats'),
    path('confirm-booking/', views.confirm_booking, name='confirm_booking'),
    path('book/<str:flight_number>/', views.book_flight, name='book_flight'),
    path('my-bookings/',views.my_bookings, name='my_bookings'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]

