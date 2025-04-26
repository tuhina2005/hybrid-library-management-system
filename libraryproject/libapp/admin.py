from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Student, Book, BookRequest, AcceptedBookRequest, StudyRoom, RoomBooking, DigitalResource, DigitalEngagementRecord
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'registered_id', 'department', 'phone_no', 'college_name')
    list_filter = ('department', 'college_name')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'registered_id', 'phone_no')
    ordering = ('user__username',)
    list_per_page = 20

class BookAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'author', 'book_id', 'available_copies')
    list_filter = ('author', 'available_copies')
    search_fields = ('book_name', 'author', 'book_id', 'description')
    ordering = ('book_name',)
    list_per_page = 20

class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'request_date', 'status')
    list_display_links = ('user', 'book')
    list_editable = ('status',)
    list_filter = ('request_date', 'status')
    search_fields = ('user__username', 'book__book_name')
    ordering = ('-request_date',)
    list_per_page = 20
    actions = ['accept_requests']

    def accept_requests(self, request, queryset):
        accepted_count = 0
        for book_request in queryset:
            if book_request.book.available_copies > 0:
                accepted_date = timezone.now()
                return_date = accepted_date + timedelta(days=5)
                
                # Create AcceptedBookRequest instance
                AcceptedBookRequest.objects.create(
                    user=book_request.user,
                    book=book_request.book,
                    accepted_date=accepted_date,
                    return_date=return_date,
                    fine=0
                )
                
                # Decrease available copies
                book_request.book.available_copies -= 1
                book_request.book.save()
                
                # Delete the original request
                book_request.delete()
                accepted_count += 1
            else:
                self.message_user(
                    request,
                    f'Could not accept request for "{book_request.book.book_name}" - No copies available',
                    level=messages.ERROR
                )
        
        if accepted_count > 0:
            self.message_user(
                request,
                f'Successfully accepted {accepted_count} book request(s)',
                level=messages.SUCCESS
            )
    accept_requests.short_description = "Accept selected book requests"

class AcceptedBookRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'accepted_date', 'return_date', 'fine', 'is_returned')
    list_filter = ('accepted_date', 'return_date', 'is_returned')
    search_fields = ('user__username', 'book__book_name')
    ordering = ('-accepted_date',)
    actions = ['mark_as_returned']

    def mark_as_returned(self, request, queryset):
        for accepted_request in queryset.filter(is_returned=False):
            accepted_request.return_book()
        self.message_user(request, "Selected books have been marked as returned")
    mark_as_returned.short_description = "Mark selected books as returned"

class StudyRoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'room_name', 'room_capacity', 'description')
    list_filter = ('room_capacity',)
    search_fields = ('room_id', 'room_name', 'description')
    ordering = ('room_id',)
    list_per_page = 20

class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'booking_date', 'request_date', 'status')
    list_filter = ('status', 'booking_date', 'request_date')
    search_fields = ('user__username', 'room__room_name', 'remarks')
    ordering = ('-request_date',)
    list_per_page = 20
    actions = ['approve_bookings', 'reject_bookings']

    def approve_bookings(self, request, queryset):
        queryset.update(status='approved')
    approve_bookings.short_description = "Approve selected bookings"

    def reject_bookings(self, request, queryset):
        queryset.update(status='rejected')
    reject_bookings.short_description = "Reject selected bookings"

class DigitalResourceAdmin(admin.ModelAdmin):
    list_display = ('resource_number', 'name', 'author', 'type', 'upload_date', 'file_size')
    list_filter = ('type', 'upload_date')
    search_fields = ('name', 'author', 'description')
    ordering = ('-upload_date',)
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'type', 'description')
        }),
        ('Files', {
            'fields': ('file', 'cover_image'),
            'classes': ('wide',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'file' in form.changed_data or 'cover_image' in form.changed_data:
            # If file or cover image is being updated, handle old files
            if change:
                old_obj = self.model.objects.get(pk=obj.pk)
                if 'file' in form.changed_data and old_obj.file:
                    old_obj.file.delete(False)
                if 'cover_image' in form.changed_data and old_obj.cover_image:
                    old_obj.cover_image.delete(False)
        super().save_model(request, obj, form, change)

class DigitalEngagementRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'resource', 'download_date', 'ip_address')
    list_filter = ('download_date', 'resource__type')
    search_fields = ('user__username', 'resource__name', 'ip_address')
    ordering = ('-download_date',)
    list_per_page = 20
    readonly_fields = ('download_date', 'ip_address', 'user_agent')

# Register models with custom admin classes
admin.site.register(Student, StudentAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookRequest, BookRequestAdmin)
admin.site.register(AcceptedBookRequest, AcceptedBookRequestAdmin)
admin.site.register(StudyRoom, StudyRoomAdmin)
admin.site.register(RoomBooking, RoomBookingAdmin)
admin.site.register(DigitalResource, DigitalResourceAdmin)
admin.site.register(DigitalEngagementRecord, DigitalEngagementRecordAdmin)

# Customize admin site
admin.site.site_header = "Library Management System"
admin.site.site_title = "Library Admin Portal"
admin.site.index_title = "Welcome to Library Management System"

