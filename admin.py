from django.contrib import admin

# Register your models here.
from . models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin): 
      list_display = ['id','flight_number','origin','destination','departure_time','arrival_time','price','seats']
