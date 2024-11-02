# Guestbook Backend API

A Django REST Framework based guestbook application with optimized database queries and caching system.

## Features

- Create entries with user name, subject and message
- Automatic user creation for new names 
- Paginated entry list (3 per page)
- User statistics
- Database query optimization
- Built-in caching system
- PostgreSQL database support

## Installation

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DB_NAME=guestbook_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start development server:
```bash
python manage.py runserver
```

## API Documentation

### 1. Create Entry
- **URL:** `/api/entries/`
- **Method:** POST
- **Content-Type:** application/json
- **Request Body:**
```json
{
    "name": "user_name",
    "subject": "entry_subject",
    "message": "entry_message"
}
```

### 2. List Entries
- **URL:** `/api/entries/`
- **Method:** GET
- **Query Parameters:** `page` (optional)
- **Response Format:**
```json
{
    "count": 10,
    "page_size": 3,
    "total_pages": 4,
    "current_page_number": 1,
    "links": {
        "next": "http://api/entries/?page=2",
        "previous": null
    },
    "entries": [
        {
            "user": "user_name",
            "subject": "entry_subject",
            "message": "entry_message"
        }
    ]
}
```

### 3. Get Users Data
- **URL:** `/api/users-data/`
- **Method:** GET
- **Response Format:**
```json
{
    "users": [
        {
            "username": "user_name",
            "last_entry": "subject | message"
        }
    ]
}
```

### Validation Rules
- **Name:**
  - Minimum length: 2 characters
  - Maximum length: 255 characters
  - Only letters, spaces, and hyphens allowed
  - Cannot contain numbers
- **Subject:**
  - Minimum length: 3 characters
  - Maximum length: 255 characters
  - Cannot contain inappropriate content
- **Message:**
  - Minimum length: 10 characters
- **General Rules:**
  - Message cannot be identical to subject
  - Same message cannot be posted within 5 minutes

### Postman Collection

A ready-to-use Postman collection is available for testing the API. To use it:

1. Open Postman application
2. Click on "Import" button
3. Select the file from `postman/Guestbook_API.postman_collection.json`
4. The collection includes pre-configured requests for all endpoints

## Technical Details

### Database Optimizations
- Indexes on foreign keys
- Composite indexes (user + created_at)
- select_related usage
- Database-level aggregation

### Security
- CORS protection
- Environment variables
- Debug mode disabled in production

### Caching
- 5 minute cache duration
- LocMemCache implementation

