# CodeCut: Barbershop Appointment Management System

A web-based appointment management system for small barbershops. Customers can register and book appointments online; the admin/barber can confirm or cancel bookings through a dashboard.

## Tech Stack
- **Backend:** Python, Django
- **Database:** PostgreSQL (Supabase)
- **Frontend:** HTML, CSS, Bootstrap 5
- **Deployment:** Railway / Render

## Setup Instructions

1. Clone the repository

`git clone <your-repo-url>`  
`cd CodeCut`

3. Create and activate a virtual environment
   
`python -m venv .venv`  
`.venv\Scripts\activate`   

3. Install dependencies

`pip install -r requirements.txt`

4. Create a `.env` file in the project root with the following:

`DEBUG=True`  
`SECRET_KEY=your-secret-key`  
`DATABASE_URL=your-supabase-connection-string`

5. Run migrations

`python manage.py migrate`

7. Run the development server
   
`python manage.py runserver`

## Project Structure
- `codecut_project/` — Django project settings
- `appointments/` — Main app (models, views, booking logic)
- `manage.py` — Django management script

## Features
- Customer registration & login
- Role-based dashboards (Admin / Customer)
- Book, confirm, and cancel appointments
- Appointment status tracking (Pending / Confirmed / Cancelled)
- Appointment history
