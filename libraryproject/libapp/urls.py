from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from .views import (IndexView, UserRegisterView, student_login, ProfileView, add_book, edit_profile, view_books,
                    book_detail, CreateBookRequestView, RequestBooksView, AcceptBookRequestView, AcceptedBooksView,
                    borrowed_books, borrowed_history, study_room_list, book_study_room, my_bookings, cancel_booking,
                    digital_resources, download_resource, user_borrow_history, cancel_book_request)

urlpatterns = [
    url(r'^index/$', IndexView.as_view(), name='index'),
    url(r'^register/$', UserRegisterView.as_view(), name='user_register'),
    url(r'^login/$', student_login, name='student_login'),
    url(r'^logout/$', LogoutView.as_view(next_page='student_login'), name='logout'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^add_book/$', add_book, name='add_book'),
    url(r'^view-books/$', view_books, name='view_books'),
    url(r'^book/(?P<pk>\d+)/$', book_detail, name='book_detail'),
    url(r'^edit-profile/$', edit_profile, name='edit_profile'),
    url(r'^request/(?P<pk>\d+)/$', CreateBookRequestView.as_view(), name='create_request'),
    url(r'^requested-books/$', RequestBooksView.as_view(), name='requested_books'),
    url(r'^accept/(?P<pk>\d+)/$', AcceptBookRequestView.as_view(), name='accept_book_request'),
    url(r'^accepted-books/$', AcceptedBooksView.as_view(), name='accepted_books'),
    url(r'^borrowed-books/$', borrowed_books, name='borrowed_books'),
    url(r'^borrowed-history/$', borrowed_history, name='borrowed_history'),
    # Study room URLs
    url(r'^study-rooms/$', study_room_list, name='study_room_list'),
    url(r'^study-room/(?P<room_id>\d+)/book/$', book_study_room, name='book_study_room'),
    url(r'^my-bookings/$', my_bookings, name='my_bookings'),
    url(r'^booking/(?P<booking_id>\d+)/cancel/$', cancel_booking, name='cancel_booking'),
    url(r'^digital-resources/$', digital_resources, name='digital_resources'),
    url(r'^download/(?P<resource_id>\d+)/$', download_resource, name='download_resource'),
    url(r'^user-borrow-history/$', user_borrow_history, name='user_borrow_history'),
    url(r'^request/(?P<request_id>\d+)/cancel/$', cancel_book_request, name='cancel_book_request'),
]





