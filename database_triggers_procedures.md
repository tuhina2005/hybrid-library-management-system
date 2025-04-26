# Database Triggers, Procedures, and Limitations

## 1. Implicit Triggers in Django Models

### 1.1 Book Availability Trigger
This trigger is implemented in the `AcceptedBookRequest` model through the `return_book` method:

```python
def return_book(self):
    if not self.is_returned:
        self.is_returned = True
        self.returned_date = timezone.now()
        if self.book:
            self.book.available_copies += 1  # Trigger: Automatically updates book availability
            self.book.save()
        elif self.details:
            self.details.book.available_copies += 1
            self.details.book.save()
        self.save()
```
**Purpose**: Automatically updates book availability when a book is returned.

### 1.2 Fine Calculation Trigger
Implemented in the `AcceptedBookRequest` model:

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
**Purpose**: Automatically calculates fines for overdue books.

### 1.3 Save Method Trigger
In the `AcceptedBookRequest` model:

```python
def save(self, *args, **kwargs):
    # Trigger: Auto-populate user and book from details
    if self.details and not self.user and not self.book:
        self.user = self.details.user
        self.book = self.details.book
    super().save(*args, **kwargs)
```
**Purpose**: Automatically populates user and book information when saving an accepted request.

## 2. Database Procedures (Django Methods)

### 2.1 Book Request Processing
```python
class BookRequest(models.Model):
    @classmethod
    def create_request(cls, user, book):
        """
        Procedure to create a new book request with validation
        """
        if book.available_copies > 0:
            request = cls.objects.create(
                user=user,
                book=book,
                request_date=timezone.now()
            )
            return request
        return None

    @classmethod
    def approve_request(cls, request_id):
        """
        Procedure to approve a book request
        """
        try:
            request = cls.objects.get(id=request_id)
            if request.book.available_copies > 0:
                accepted = AcceptedBookRequest.objects.create(
                    user=request.user,
                    book=request.book,
                    details=request,
                    return_date=timezone.now() + timedelta(days=14)
                )
                request.book.available_copies -= 1
                request.book.save()
                return accepted
        except cls.DoesNotExist:
            return None
```

### 2.2 Room Booking Procedure
```python
class RoomBooking(models.Model):
    @classmethod
    def book_room(cls, user, room, date):
        """
        Procedure to book a study room with validation
        """
        # Check if room is already booked
        existing_booking = cls.objects.filter(
            room=room,
            booking_date=date,
            status='approved'
        ).exists()
        
        if not existing_booking:
            booking = cls.objects.create(
                user=user,
                room=room,
                booking_date=date,
                status='pending'
            )
            return booking
        return None
```

## 3. Database Limitations and Constraints

### 3.1 Model Field Constraints

#### Book Model
```python
class Book(models.Model):
    book_id = models.CharField(max_length=20, unique=True)  # Unique constraint
    available_copies = models.PositiveIntegerField(default=1)  # Non-negative constraint
```

#### StudyRoom Model
```python
class StudyRoom(models.Model):
    room_id = models.CharField(max_length=10, unique=True)  # Unique constraint
    room_capacity = models.IntegerField()  # Required field
```

#### RoomBooking Model
```python
class RoomBooking(models.Model):
    class Meta:
        unique_together = ['room', 'booking_date']  # Composite unique constraint
```

### 3.2 Business Logic Constraints

1. **Book Availability**
   - Books cannot have negative available copies
   - Books cannot be borrowed if no copies are available

2. **Fine System**
   - Fines are calculated at ₹10 per day
   - Fines only apply to overdue books
   - Fines are non-negative

3. **Room Booking**
   - A room cannot be double-booked for the same date
   - Room capacity cannot be exceeded
   - Booking dates must be in the future

### 3.3 Data Integrity Constraints

1. **Cascade Deletion**
```python
user = models.ForeignKey(User, on_delete=models.CASCADE)
book = models.ForeignKey(Book, on_delete=models.CASCADE)
```
- When a user or book is deleted, all related records are automatically deleted

2. **Null Handling**
```python
returned_date = models.DateTimeField(null=True, blank=True)
description = models.TextField(null=True, blank=True)
```
- Specific fields are allowed to be null based on business requirements

## 4. Recommended Additional Triggers and Procedures

### 4.1 Automated Fine Collection Trigger
```sql
CREATE TRIGGER calculate_daily_fines
AFTER UPDATE ON libapp_acceptedbookrequest
FOR EACH ROW
BEGIN
    IF NOT NEW.is_returned AND NEW.return_date < CURRENT_TIMESTAMP THEN
        SET NEW.fine = DATEDIFF(CURRENT_TIMESTAMP, NEW.return_date) * 10;
    END IF;
END;
```

### 4.2 Book Status Update Procedure
```sql
DELIMITER //
CREATE PROCEDURE update_book_status()
BEGIN
    UPDATE libapp_book b
    SET available_copies = (
        SELECT COUNT(*)
        FROM libapp_acceptedbookrequest ar
        WHERE ar.book_id = b.id AND ar.is_returned = FALSE
    );
END //
DELIMITER ;
```

### 4.3 Room Booking Validation Procedure
```sql
DELIMITER //
CREATE PROCEDURE validate_room_booking(
    IN p_room_id INT,
    IN p_booking_date DATE,
    OUT p_is_available BOOLEAN
)
BEGIN
    SELECT NOT EXISTS(
        SELECT 1 FROM libapp_roombooking
        WHERE room_id = p_room_id
        AND booking_date = p_booking_date
        AND status = 'approved'
    ) INTO p_is_available;
END //
DELIMITER ;
```

## 5. Implementation Notes

1. **Current Implementation**
   - Most constraints and triggers are implemented at the application level using Django's ORM
   - Database-level triggers and procedures can be added for better performance
   - Current system relies on Django's model validation and signals

2. **Potential Improvements**
   - Implement database-level triggers for real-time fine calculation
   - Add stored procedures for complex booking operations
   - Create database-level constraints for data integrity

3. **Migration Considerations**
   - When implementing new triggers or procedures, create proper database migrations
   - Test thoroughly with existing data
   - Consider performance impact on large datasets

## 6. Best Practices

1. **Performance Optimization**
   - Use database indexes for frequently queried fields
   - Implement batch processing for large operations
   - Cache frequently accessed data

2. **Data Integrity**
   - Use transactions for critical operations
   - Implement proper error handling
   - Maintain audit logs for important changes

3. **Maintenance**
   - Regularly review and update triggers
   - Monitor procedure performance
   - Clean up old or unused constraints 