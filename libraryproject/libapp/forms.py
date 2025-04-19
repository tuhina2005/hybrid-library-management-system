from django import forms
from django.contrib.auth.models import User
from .models import Student, Book, BookRequest, StudyRoom, RoomBooking
from django.core.exceptions import ValidationError
from datetime import date





from django import forms
from django.contrib.auth.models import User
from .models import Student, Book




class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['phone_no', 'department', 'roll_number', 'registered_id', 'college_name']


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")




from django import forms

class StudentLoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['book_name', 'author', 'book_id', 'description', 'book_image']


from django import forms
from django.contrib.auth.models import User
from .models import Student

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['phone_no', 'department', 'roll_number', 'registered_id', 'college_name']

class RoomBookingForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
        help_text='Select a date for your room booking'
    )
    
    class Meta:
        model = RoomBooking
        fields = ['booking_date', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')
        if booking_date < date.today():
            raise ValidationError("Booking date cannot be in the past")
        return booking_date

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        booking_date = cleaned_data.get('booking_date')
        
        if room and booking_date:
            # Check if room is already booked for this date
            existing_booking = RoomBooking.objects.filter(
                room=room,
                booking_date=booking_date,
                status='approved'
            ).exists()
            
            if existing_booking:
                raise ValidationError("This room is already booked for the selected date")
