from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('EC', 'Electronics and Communication'),
        ('EEE', 'Electrical and Electronics Engineering'),
        ('BCA', 'Bachelor of Computer Applications'),
        ('OTHER', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)

    phone_no = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    department = models.CharField(max_length=400, choices=DEPARTMENT_CHOICES)
    roll_number = models.CharField(max_length=10)
    registered_id = models.CharField(max_length=10)
    college_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.user.first_name} {self.user.last_name}"



class Book(models.Model):
    book_name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    book_id = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    book_image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.book_name



class BookRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Request by {self.user.username} for {self.book.book_name} on {self.request_date}"


class AcceptedBookRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    details = models.ForeignKey(BookRequest, on_delete=models.CASCADE, null=True, blank=True)  # Keep this temporarily
    accepted_date = models.DateTimeField(auto_now_add=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    return_date = models.DateTimeField()
    is_returned = models.BooleanField(default=False)
    returned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.book and self.user:
            return f"Accepted request for {self.book.book_name} by {self.user.username}"
        elif self.details:
            return f"Accepted request for {self.details.book.book_name} by {self.details.user.username}"
        return "Accepted book request"

    def return_book(self):
        if not self.is_returned:
            self.is_returned = True
            self.returned_date = timezone.now()
            if self.book:
                self.book.available_copies += 1
                self.book.save()
            elif self.details:
                self.details.book.available_copies += 1
                self.details.book.save()
            self.save()

    def calculate_fine(self):
        if not self.is_returned:
            current_date = timezone.now()
            if current_date > self.return_date:
                days_late = (current_date - self.return_date).days
                self.fine = days_late * 10  # ₹10 per day
                self.save()
        return self.fine

    def save(self, *args, **kwargs):
        # If this is a new object being created from details
        if self.details and not self.user and not self.book:
            self.user = self.details.user
            self.book = self.details.book
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-accepted_date']


class StudyRoom(models.Model):
    room_id = models.CharField(max_length=10, unique=True)
    room_name = models.CharField(max_length=100)
    room_capacity = models.IntegerField(help_text="Maximum number of students allowed")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.room_name} (Capacity: {self.room_capacity})"

    class Meta:
        ordering = ['room_id']

class RoomBooking(models.Model):
    APPROVAL_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE)
    booking_date = models.DateField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default='pending')
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-request_date']
        unique_together = ['room', 'booking_date']  # Prevent double booking

    def __str__(self):
        return f"{self.user.username} - {self.room.room_name} - {self.booking_date}"

class DigitalResource(models.Model):
    RESOURCE_TYPES = [
        ('MAGAZINE', 'Magazine'),
        ('JOURNAL', 'Journal'),
        ('BOOK', 'Book'),
        ('RESEARCH', 'Research Paper'),
    ]

    resource_number = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='digital_resources/')
    cover_image = models.ImageField(upload_to='digital_resources/covers/', blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def file_size(self):
        if self.file:
            # Return file size in MB
            size_bytes = self.file.size
            return f"{size_bytes / (1024*1024):.2f} MB"
        return "0 MB"

    class Meta:
        ordering = ['-upload_date']

class DigitalEngagementRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(DigitalResource, on_delete=models.CASCADE)
    download_date = models.DateTimeField(auto_now_add=True)
    download_number = models.AutoField(primary_key=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['-download_date']
        verbose_name = 'Digital Engagement Record'
        verbose_name_plural = 'Digital Engagement Records'

    def __str__(self):
        return f"{self.user.username} - {self.resource.name} ({self.download_date.strftime('%Y-%m-%d %H:%M')})"



