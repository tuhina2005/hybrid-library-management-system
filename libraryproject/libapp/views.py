from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, StudentRegistrationForm, StudentLoginForm, BookForm, RoomBookingForm
from .models import Student, Book, BookRequest, AcceptedBookRequest, StudyRoom, RoomBooking, DigitalResource, DigitalEngagementRecord
from django.views.generic import DetailView
from django.views import generic
from django.views import View
from django.views.generic import ListView, DetailView
from django.views import View
from django.shortcuts import render, get_object_or_404
from datetime import timedelta, date
from .models import Book
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from .models import BookRequest, AcceptedBookRequest
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.db import models
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.contrib.admin.views.decorators import staff_member_required

# Assuming you have a Book model









from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from .forms import UserRegisterForm, StudentRegistrationForm
from .models import Student



from django.shortcuts import render
from django.views import View

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

class UserRegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request):
        user_form = UserRegisterForm()
        student_form = StudentRegistrationForm()
        return render(request, self.template_name, {
            'user_form': user_form,
            'student_form': student_form
        })

    def post(self, request):
        user_form = UserRegisterForm(request.POST)
        student_form = StudentRegistrationForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            student = student_form.save(commit=False)
            student.user = user
            student.save()

            # Automatically log in the user
            login(request, user)
            return redirect('student_login')
        return render(request, self.template_name, {
            'user_form': user_form,
            'student_form': student_form
        })

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = StudentLoginForm()
    return render(request, 'student_login.html', {'form': form})


class ProfileView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'libapp/profile.html'
    context_object_name = 'student'
    login_url = 'student_login'

    def get_object(self):
        try:
            return Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            messages.error(self.request, "Student profile not found. Please contact administrator.")
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate total pending fines
        total_fines = AcceptedBookRequest.objects.filter(
            user=self.request.user,
            is_returned=False
        ).aggregate(total_fines=models.Sum('fine'))['total_fines'] or 0
        context['total_fines'] = total_fines

        # Add currently borrowed books
        current_borrowed = AcceptedBookRequest.objects.filter(
            models.Q(user=self.request.user) | models.Q(details__user=self.request.user),
            is_returned=False
        ).order_by('-accepted_date')
        context['borrowed_books'] = current_borrowed
        
        # Add book requests (pending and rejected)
        book_requests = BookRequest.objects.filter(
            user=self.request.user
        ).order_by('-request_date')
        context['book_requests'] = book_requests
        
        # Add current date for template comparisons
        context['current_date'] = timezone.now().date()
        
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return redirect('student_login')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


@login_required
def add_book(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('view_books')
        
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('view_books')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})


def view_books(request):
    books = Book.objects.all()
    return render(request, 'view_books.html', {'books': books})



def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserEditForm, StudentEditForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        student_form = StudentEditForm(request.POST, instance=request.user.student)
        if user_form.is_valid() and student_form.is_valid():
            user_form.save()
            student_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        student_form = StudentEditForm(instance=request.user.student)
    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'student_form': student_form
    })


from django.views import View, generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Book, BookRequest, Student
from django.contrib.auth.models import User

@method_decorator(login_required, name='dispatch')
class CreateBookRequestView(View):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        user = request.user

        # Check if user has already requested this book
        if BookRequest.objects.filter(user=user, book=book).exists():
            messages.warning(request, 'You have already requested this book.')
            return redirect('view_books')
        
        # Check if book is available
        if book.available_copies <= 0:
            messages.error(request, 'This book is currently not available.')
            return redirect('view_books')

        # Create the book request
        BookRequest.objects.create(user=user, book=book)
        messages.success(request, 'Your book request has been submitted successfully.')
        return redirect('view_books')

class RequestBooksView(generic.ListView):
    model = BookRequest
    template_name = 'requested_books.html'
    context_object_name = 'requested_books'

    def get_queryset(self):
        user = self.request.user
        return BookRequest.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the book request objects along with their primary keys (pks) to the template
        context['book_requests'] = BookRequest.objects.filter(user=self.request.user)
        return context


from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.utils import timezone
from datetime import timedelta
from .models import BookRequest, AcceptedBookRequest

@method_decorator(csrf_protect, name='dispatch')
class AcceptBookRequestView(View):

    def get(self, request, pk):
        book_request = get_object_or_404(BookRequest, pk=pk)
        accepted_date = timezone.now()
        return_date = accepted_date + timedelta(days=5)  # Calculate return date

        # Calculate fine if book is returned late
        current_date = timezone.now()
        fine = 0
        if current_date > return_date:
            days_late = (current_date - return_date).days
            fine = days_late * 10

        # Create AcceptedBookRequest instance with calculated details
        accepted_book = AcceptedBookRequest.objects.create(
            details=book_request,
            accepted_date=accepted_date,
            return_date=return_date,  # Set the return_date
            fine=fine
        )

        # Delete the original book request
        book_request.delete()

        return redirect('requested_books')

    def post(self, request, pk):
        return self.get(request, pk)








from django.shortcuts import render
from django.views import View
from .models import AcceptedBookRequest

class AcceptedBooksView(View):
    def get(self, request):
        accepted_books = AcceptedBookRequest.objects.all()
        return render(request, 'accepted_books.html', {'accepted_books': accepted_books})

@login_required
def borrowed_books(request):
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')  # all, current, returned
    sort_by = request.GET.get('sort', '-accepted_date')  # -accepted_date, return_date, book__book_name
    
    # Get all borrowed books for the user
    borrowed_books = AcceptedBookRequest.objects.filter(
        models.Q(user=request.user) | models.Q(details__user=request.user)
    )
    
    # Apply status filter
    if status_filter == 'current':
        borrowed_books = borrowed_books.filter(is_returned=False)
    elif status_filter == 'returned':
        borrowed_books = borrowed_books.filter(is_returned=True)
    
    # Apply sorting
    borrowed_books = borrowed_books.order_by(sort_by)
    
    # Prepare sort options for template
    sort_options = [
        ('-accepted_date', 'Latest First'),
        ('accepted_date', 'Oldest First'),
        ('return_date', 'Return Date'),
        ('-fine', 'Highest Fine'),
    ]
    
    return render(request, 'borrowed_books.html', {
        'borrowed_books': borrowed_books,
        'current_status': status_filter,
        'current_sort': sort_by,
        'sort_options': sort_options
    })

@login_required
def borrowed_history(request):
    # Get all borrowed books history
    history = AcceptedBookRequest.objects.filter(
        models.Q(user=request.user) | models.Q(details__user=request.user)
    ).order_by('-accepted_date')
    
    return render(request, 'borrowed_history.html', {
        'borrowed_history': history
    })

@login_required
def study_room_list(request):
    rooms = StudyRoom.objects.all()
    return render(request, 'libapp/study_room_list.html', {'rooms': rooms})

@login_required
def book_study_room(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    
    if request.method == 'POST':
        form = RoomBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking_date = form.cleaned_data['booking_date']
            
            # Check if room is already booked for this date
            existing_booking = RoomBooking.objects.filter(
                room=room,
                booking_date=booking_date,
                status__in=['pending', 'approved']
            ).exists()
            
            if existing_booking:
                messages.error(
                    request,
                    f'Sorry, {room.room_name} is not available on {booking_date.strftime("%B %d, %Y")}. '
                    'Please choose a different date or room.'
                )
            else:
                booking.user = request.user
                booking.room = room
                booking.status = 'pending'
                booking.save()
                messages.success(
                    request,
                    'Your room booking request has been submitted and is pending approval.'
                )
                return redirect('my_bookings')
    else:
        form = RoomBookingForm(initial={'room': room})
    
    # Get existing bookings for this room to show availability
    existing_bookings = RoomBooking.objects.filter(
        room=room,
        booking_date__gte=timezone.now().date(),
        status__in=['pending', 'approved']
    ).order_by('booking_date')
    
    return render(request, 'libapp/book_study_room.html', {
        'form': form,
        'room': room,
        'existing_bookings': existing_bookings
    })

@login_required
def my_bookings(request):
    bookings = RoomBooking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'libapp/my_bookings.html', {
        'bookings': bookings,
        'today': date.today()
    })

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(RoomBooking, id=booking_id, user=request.user)
    if booking.status == 'pending' or booking.status == 'approved':
        if booking.booking_date >= date.today():
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Your booking has been cancelled successfully.')
        else:
            messages.error(request, 'Cannot cancel past bookings.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('my_bookings')

@login_required
def digital_resources(request):
    # Get filter parameters from request
    resource_type = request.GET.get('type', '')
    sort_by = request.GET.get('sort', '-upload_date')
    search_query = request.GET.get('search', '')
    
    # Start with all resources
    resources = DigitalResource.objects.all()
    
    # Apply type filter if specified
    if resource_type:
        resources = resources.filter(type=resource_type)
    
    # Apply search filter if specified
    if search_query:
        resources = resources.filter(
            models.Q(name__icontains=search_query) |
            models.Q(author__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    # Apply sorting
    resources = resources.order_by(sort_by)
    
    # Get all available resource types for the filter dropdown
    resource_types = DigitalResource.RESOURCE_TYPES
    
    # Get sort options
    sort_options = [
        ('-upload_date', 'Newest First'),
        ('upload_date', 'Oldest First'),
        ('name', 'Name (A-Z)'),
        ('-name', 'Name (Z-A)'),
        ('author', 'Author (A-Z)'),
        ('-author', 'Author (Z-A)'),
    ]
    
    return render(request, 'libapp/digital_resources.html', {
        'resources': resources,
        'resource_types': resource_types,
        'sort_options': sort_options,
        'selected_type': resource_type,
        'selected_sort': sort_by,
        'search_query': search_query,
    })

@login_required
def download_resource(request, resource_id):
    resource = get_object_or_404(DigitalResource, resource_number=resource_id)
    
    # Create engagement record
    DigitalEngagementRecord.objects.create(
        user=request.user,
        resource=resource,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    response = HttpResponse(resource.file, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename="{resource.file.name}"'
    return response

@staff_member_required
def user_borrow_history(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'username')

    # Get all users who have borrowed books
    users = User.objects.filter(
        Q(acceptedbookrequest__isnull=False) | 
        Q(bookrequest__details__isnull=False)
    ).distinct()

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Sort users based on selected criteria
    if sort_by == 'total_books':
        users = users.annotate(
            total_books=Count('acceptedbookrequest') + Count('bookrequest__details')
        ).order_by('-total_books')
    elif sort_by == 'overdue':
        users = users.annotate(
            overdue_count=Count(
                'acceptedbookrequest',
                filter=Q(acceptedbookrequest__return_date__lt=timezone.now())
            )
        ).order_by('-overdue_count')
    else:  # Default sort by username
        users = users.order_by('username')

    user_histories = []
    for user in users:
        # Get all borrowed books for the user
        borrowed_books = AcceptedBookRequest.objects.filter(
            Q(user=user) | Q(details__user=user)
        ).select_related('book')

        # Calculate statistics
        total_books = borrowed_books.count()
        current_books = borrowed_books.filter(
            Q(return_date__isnull=True) | 
            Q(return_date__gt=timezone.now())
        ).count()
        overdue_books = borrowed_books.filter(
            return_date__lt=timezone.now()
        ).count()
        total_fine = borrowed_books.aggregate(
            total_fine=Sum('fine')
        )['total_fine'] or 0

        user_histories.append({
            'user': user,
            'total_books': total_books,
            'current_books': current_books,
            'overdue_books': overdue_books,
            'total_fine': total_fine,
            'borrowed_books': borrowed_books
        })

    context = {
        'user_histories': user_histories,
        'search_query': search_query,
        'sort_by': sort_by
    }
    return render(request, 'libapp/user_borrow_history.html', context)

@login_required
def cancel_book_request(request, request_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method. Please use the cancel button.')
        return redirect('profile')
        
    try:
        book_request = get_object_or_404(BookRequest, id=request_id, user=request.user)
        if book_request.status == 'pending':
            book_name = book_request.book.book_name  # Store book name before deletion
            book_request.delete()
            messages.success(request, f'Book request for "{book_name}" cancelled successfully.')
        else:
            messages.error(request, 'This request cannot be cancelled.')
    except Exception as e:
        messages.error(request, f'Error cancelling request: {str(e)}')
    return redirect('profile')



