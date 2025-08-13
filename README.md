# HomiGo Backend

## Description
This is the Django backend for the HomiGo project, a home service application designed to connect users with professional technicians for various home services. The platform supports three user types: **Admin**, **Technician**, and **User**, each with specific roles and functionalities. Admins manage the platform, technicians provide services, and users book and pay for services. The backend includes payment processing via the Stripe payment gateway.

## Tech Stack
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Celery + Redis (for async tasks)
- Stripe (for payment processing)

## Features
- User authentication and role-based access (Admin, Technician, User)
- Service category and type management
- Booking system with status tracking (Pending, Cancelled, Booked, Confirmed, Completed)
- Address management for users
- Secure payment processing using Stripe
- Technician assignment and verification

## Setup

### 1. Clone the repo:
```bash
git clone https://github.com/yourusername/homigo.git