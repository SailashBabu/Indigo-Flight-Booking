# flights/views.py
import datetime
from django.shortcuts import render, redirect,get_object_or_404
from .models import Flight, Booking,User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.forms import formset_factory


def register(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists.")
            return redirect('register')

        user = User(email=email, password=password,name=name)
        user.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'signup.html')

def logout(request):
    request.session.flush() 
    messages.success(request, "You have been logged out.")
    response = render(request, 'login.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Retrieve the user based on email from the MongoDB collection using Djongo ORM
            user = User.objects.get(email=email,password=password)

            # Check the password using Django's ⁠ check_password ⁠
            if password==user.password:
                # Save user ID in the session
                request.session['name'] = str(user.name) 
                request.session['user_id']=str(user.email)# Store the user's ID as a string in session
                messages.success(request, "Login successful!")
                return render(request, 'flights/search.html',{'user_id':request.session['name']}) # Redirect to the home page or another destination
            else:
                messages.error(request, "Invalid email or password.")
                return redirect('login')

        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
            return redirect('login')

    return render(request, 'login.html')






def search_flights(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        all_flights = Flight.objects.filter(origin=origin, destination=destination)
        flights = [flight for flight in all_flights if flight.departure_time.date() == date]


        context={
            "flights":flights,
            "origin":origin,
            "destination":destination,
        }
        return render(request, 'flights/search_results.html', context)
    return render(request, 'flights/search.html')


def passenger_details(request):
    # Get data from the query string
    flight_number= request.GET.get('flight_id')
    request.session["fli"]=flight_number
    passengers = int(request.GET.get('passengers'))
    flight = Flight.objects.get(flight_number=flight_number)
    context = {
        'flight': flight,
        'passengers': passengers,
        'range_passenger':range(passengers),
    }
    return render(request, 'flights/passenger_details.html', context)
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Flight

def select_seats(request):
    if request.method == "POST":
        number_of_passengers = int(request.POST.get("number_of_passengers"))
        passengers = []

        # Collect all passenger data from the form
        for i in range(number_of_passengers):
            passenger_data = {
                'name': request.POST.get(f'name_{i}'),
                'age': request.POST.get(f'age_{i}'),
                'gender': request.POST.get(f'gender_{i}')
            }
            passengers.append(passenger_data)

        print("Passenger Data:", passengers)

        flight_number=request.session.get('fli')
        request.session.pop('selected_seats', None)
        flight = get_object_or_404(Flight, flight_number=flight_number)

        # Ensure seats are accessed as a list of dictionaries
        seats = flight.seats  # Array of dictionaries

        # Create a seat map grouped by row
        rows = sorted(set(seat['row'] for seat in seats))  # Extract unique row numbers
        seat_map = {
            row: sorted(
                [seat for seat in seats if seat['row'] == row], 
                key=lambda x: x['column']
            ) for row in rows
        }

        # Pass the seat map and passenger data to the template
        context = {
            'passengers': passengers,
            'flight': flight,
            'seat_map': seat_map,
            'passenger_count':len(passengers)
        }
        return render(request, 'flights/select_seats.html', context)

    return render(request, 'flights/passenger_details.html')



from django.shortcuts import render, redirect
from django.http import HttpResponse



def confirm_booking(request):
    passengers = request.session.get('passengers', [])
    
    if not passengers:
        return HttpResponse("No passenger data found.")

    # Render a confirmation page with selected passengers and seats
    return render(request, 'flights/confirm_boking.html', {'passengers': passengers})





@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'flights/my_bookings.html', {'bookings': bookings})






from django.shortcuts import render, redirect, get_object_or_404
from .models import Flight

from django.shortcuts import render, redirect, get_object_or_404
from .models import Flight, Booking



def book_flight(request, flight_number):
    flight = get_object_or_404(Flight, flight_number=flight_number)

    if request.method == 'POST':
        selected_seats = request.POST.get('selected_seats', '').split(',')

        # Modify the seats directly in the flight object
        updated_seats = []
        for seat in flight.seats:
            seat_id = f"{seat['row']}{seat['column']}"
            if seat_id in selected_seats:
                seat['is_booked'] = True  # Mark the seat as booked
            updated_seats.append(seat)

        # Ensure the updated seats list is assigned
        flight.seats = updated_seats

        # Save the document with the primary key to avoid the 'no primary key' error
        Flight.objects.filter(pk=flight.pk).update(seats=updated_seats)
        print(request.session.get('user_id'))

        booking = Booking(
            user_id=request.session.get('user_id'),  # Assuming user is authenticated
            flight_number=flight_number,
            selected_seats=selected_seats
        )
        booking.save()

        return render(request, 'flights/confirm_boking.html', {'flight': flight})

    return redirect('select_seats', flight_number=flight_number)

def my_bookings(request):
     # Redirect to login if not authenticated

    # Fetch bookings for the authenticated user
    bookings = Booking.objects.filter(user_id=request.session.get('user_id'))
    print(request.session.get('user_id'))

    return render(request, 'flights/my_bookings.html', {'bookings': bookings})

