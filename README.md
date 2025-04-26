# Library Management System

A comprehensive Library Management System built with Django, featuring user authentication, book management, study room bookings, and digital resources.

## Features

- User Authentication (Login/Register)
- Book Management
  - View available books
  - Request books
  - Track borrowed books
- Study Room Booking System
- Digital Resources Access
- User Profile Management
- Admin Dashboard

## Technologies Used

- Python 3.x
- Django 3.2
- Bootstrap 5
- SQLite (Development)
- HTML5/CSS3
- JavaScript

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
libraryproject/
├── libapp/                 # Main application
│   ├── migrations/        # Database migrations
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # HTML templates
│   ├── admin.py         # Admin configuration
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   └── urls.py          # URL routing
├── libraryproject/       # Project settings
│   ├── settings.py      # Project settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
└── manage.py            # Django management script
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🚀 Features

### 📚 Book Management
- Add, update, and remove books from the library catalog
- Track book availability in real-time
- Upload and display book cover images
- Detailed book information including title, author, and description
- Search functionality for finding books quickly

### 👥 User Management
- Student registration and profile management
- Role-based access control (Admin/Student)
- Personal dashboard for users
- Track borrowing history

### 📖 Book Borrowing System
- Request books online
- Automatic tracking of due dates
- Fine calculation for overdue books
- Book return management
- Borrowing history for users

### 🏢 Study Room Management
- Book study rooms for group work
- Room capacity management
- Booking status tracking
- Prevent double bookings

### 📱 Digital Resources
- Access to digital magazines, journals, and e-books
- Track digital resource usage
- Download statistics
- Cover image display for digital resources

## 🛠️ Technology Stack

- **Backend**: Django 3.2
- **Database**: SQLite3 (can be configured for MySQL)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap
- **Image Storage**: Django File Storage
- **Icons**: Font Awesome

## 📋 Prerequisites

- Python 3.x
- pip (Python package manager)
- Virtual environment (recommended)

## 🗂️ Project Structure

```
libraryproject/
├── libapp/                 # Main application directory
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL configurations
│   └── templates/         # HTML templates
├── static/                # Static files (CSS, JS, Images)
├── media/                 # User-uploaded files
└── libraryproject/        # Project settings directory
    ├── settings.py        # Project settings
    └── urls.py           # Main URL routing
```

## 💡 Key Features Explained

### Book Management
- Each book has a unique ID, title, author, and availability status
- Real-time tracking of available copies
- Image upload capability for book covers

### User System
- Student profiles with department and roll number
- Secure authentication system
- Role-based permissions

### Borrowing System
- Automated fine calculation (₹10 per day for overdue books)
- Email notifications for due dates (configurable)
- Maximum borrowing period: 14 days

### Study Room System
- Room capacity enforcement
- Booking validation to prevent conflicts
- Status tracking (pending/approved/rejected)

## 🔐 Security Features

- CSRF protection enabled
- Secure password hashing
- User authentication required for sensitive operations
- Form validation and sanitization

## 📊 Database Schema

The project uses a relational database with the following key models:
- Student (User profile information)
- Book (Library resources)
- BookRequest (Borrowing requests)
- AcceptedBookRequest (Approved borrowings)
- StudyRoom (Room management)
- DigitalResource (E-resources)

## 🛠️ Customization

### Adding New Book Categories
1. Update the Book model in `models.py`
2. Create and apply migrations
3. Update the admin interface

### Modifying Fine Calculation
- Edit the `calculate_fine` method in the `AcceptedBookRequest` model
- Default rate: ₹10 per day

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, email your.email@example.com or create an issue in the repository.

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap Team
- Font Awesome
- All contributors who helped with the project

## 📸 Screenshots

[Add screenshots of your application here]

## 🔄 Future Updates

- [ ] Mobile application
- [ ] QR code-based book tracking
- [ ] Integration with external library databases
- [ ] Advanced reporting system
- [ ] Online payment system for fines

---
Made with ❤️ by [Your Name]
