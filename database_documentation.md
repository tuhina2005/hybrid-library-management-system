# Library Management System - Database Documentation

## 1. Database Configuration

The project is configured to use SQLite3 by default, but the models are compatible with MySQL. The database configuration is defined in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

To use MySQL, you would modify this configuration to:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'library_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 2. Data Models and Relationships

### 2.1 User Management
#### Student Model
```python
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no = models.CharField(max_length=15)
    department = models.CharField(max_length=400)
    roll_number = models.CharField(max_length=10)
    registered_id = models.CharField(max_length=10)
    college_name = models.CharField(max_length=100)
```
- One-to-One relationship with Django's built-in User model
- Stores additional student information

### 2.2 Book Management
#### Book Model
```python
class Book(models.Model):
    book_name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    book_id = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    book_image = models.ImageField(upload_to='book_images/')
    available_copies = models.PositiveIntegerField(default=1)
```
- Core model for book information
- Tracks book availability

### 2.3 Book Borrowing System
#### BookRequest Model
```python
class BookRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(default=timezone.now)
```
- Handles book borrowing requests
- Many-to-One relationships with User and Book

#### AcceptedBookRequest Model
```python
class AcceptedBookRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    details = models.ForeignKey(BookRequest, on_delete=models.CASCADE)
    accepted_date = models.DateTimeField(auto_now_add=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2)
    return_date = models.DateTimeField()
    is_returned = models.BooleanField(default=False)
    returned_date = models.DateTimeField(null=True)
```
- Tracks approved book requests
- Handles book returns and fines

### 2.4 Study Room Management
#### StudyRoom Model
```python
class StudyRoom(models.Model):
    room_id = models.CharField(max_length=10, unique=True)
    room_name = models.CharField(max_length=100)
    room_capacity = models.IntegerField()
    description = models.TextField()
```

#### RoomBooking Model
```python
class RoomBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE)
    booking_date = models.DateField()
    status = models.CharField(max_length=10)
```

### 2.5 Digital Resources
#### DigitalResource Model
```python
class DigitalResource(models.Model):
    resource_number = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    type = models.CharField(max_length=20)
    file = models.FileField(upload_to='digital_resources/')
```

#### DigitalEngagementRecord Model
```python
class DigitalEngagementRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(DigitalResource, on_delete=models.CASCADE)
    download_date = models.DateTimeField(auto_now_add=True)
```

## 3. Key Database Operations

### 3.1 Book Management
```python
# Adding a new book
Book.objects.create(
    book_name="Sample Book",
    author="Author Name",
    book_id="BK001",
    available_copies=5
)

# Updating book availability
book.available_copies -= 1
book.save()
```

### 3.2 Book Borrowing
```python
# Creating a book request
BookRequest.objects.create(
    user=request.user,
    book=book,
    request_date=timezone.now()
)

# Accepting a book request
AcceptedBookRequest.objects.create(
    user=book_request.user,
    book=book_request.book,
    details=book_request,
    return_date=timezone.now() + timedelta(days=14)
)
```

### 3.3 Fine Calculation
```python
def calculate_fine(self):
    if not self.is_returned:
        current_date = timezone.now()
        if current_date > self.return_date:
            days_late = (current_date - self.return_date).days
            self.fine = days_late * 10  # ₹10 per day
            self.save()
    return self.fine
```

## 4. Database Schema and Relationships

### 4.1 Key Relationships
- User ←→ Student (One-to-One)
- User ←→ BookRequest (One-to-Many)
- Book ←→ BookRequest (One-to-Many)
- BookRequest ←→ AcceptedBookRequest (One-to-One)
- User ←→ RoomBooking (One-to-Many)
- StudyRoom ←→ RoomBooking (One-to-Many)
- User ←→ DigitalEngagementRecord (One-to-Many)
- DigitalResource ←→ DigitalEngagementRecord (One-to-Many)

### 4.2 Constraints and Indexes
- Unique constraints: `book_id`, `room_id`, `[room, booking_date]`
- Foreign key constraints with CASCADE deletion
- Auto-incrementing fields: `resource_number`, `download_number`
- Default ordering by dates in relevant models

## 5. Important Queries and Operations

### 5.1 Book Availability
```python
# Check available books
available_books = Book.objects.filter(available_copies__gt=0)

# Check borrowed books for a user
borrowed_books = AcceptedBookRequest.objects.filter(
    user=user,
    is_returned=False
)
```

### 5.2 Room Booking
```python
# Check room availability
available_rooms = StudyRoom.objects.exclude(
    roombooking__booking_date=date,
    roombooking__status='approved'
)
```

### 5.3 Digital Resource Access
```python
# Track resource downloads
DigitalEngagementRecord.objects.create(
    user=user,
    resource=digital_resource,
    ip_address=request.META.get('REMOTE_ADDR')
)
```

### 5.4 Fine Management
```python
# Get users with pending fines
users_with_fines = AcceptedBookRequest.objects.filter(
    is_returned=False,
    fine__gt=0
)
```

## 6. Database Maintenance

### 6.1 Regular Tasks
- Calculate fines for overdue books
- Update book availability status
- Clean up expired room bookings
- Track digital resource usage

### 6.2 Data Integrity
- Cascade deletion for related records
- Null handling for optional fields
- Unique constraints for critical fields
- Default values for required fields

This documentation provides a comprehensive overview of the database structure and operations in the Library Management System. For specific implementation details, refer to the respective model files and views in the codebase. 