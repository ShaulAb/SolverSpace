# Solver Space

An open-source Kaggle-like platform for hosting competitions, submitting solutions, and sharing notebooks with the community.

## Key Technical Components

1. Backend Stack:
   - FastAPI for the web framework
   - Supabase for authentication and database
   - Celery with Redis for async task processing
   - PostgreSQL (via Supabase) for data storage

2. Core Features:
   - User authentication system (email-based via Supabase)
   - Competition management system
   - Async submission processing pipeline
   - Notebook sharing system
   - Leaderboard system

3. File Handling:
   - CSV submission processing
   - Jupyter notebook file storage and sharing
   - Competition dataset management

4. Processing Architecture:
   - Async task queue for submission processing
   - Real-time leaderboard updates
   - Separate worker processes for heavy computations

## Local Development Setup

### Prerequisites
- Python 3.11+
- `uv` for Python package management
- A Supabase account (free tier works fine)

### 1. Environment Setup
```bash
# Create and activate environment with uv
uv venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
uv pip install reflex supabase python-dotenv
```

### 2. Supabase Setup

1. Create a Supabase Project:
   - Go to [Supabase](https://supabase.com)
   - Sign up or log in
   - Click "New Project"
   - Fill in project details
   - Note down your project URL and anon/public key

2. Configure Authentication:
   - In your Supabase dashboard, go to Authentication → Settings
   - Under "Email Auth", enable "Enable Email Signup"
   - Configure password settings as needed
   - (Optional) Set up additional providers like Google, GitHub, etc.

3. Set up Database Schema:
```sql
-- Users table is automatically created by Supabase Auth
-- We'll extend it with additional fields

-- Create a profile table that extends auth.users
create table public.profiles (
  id uuid references auth.users on delete cascade not null primary key,
  username text unique,
  full_name text,
  avatar_url text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS (Row Level Security)
alter table public.profiles enable row level security;

-- Create policies
create policy "Public profiles are viewable by everyone"
  on public.profiles for select
  using ( true );

create policy "Users can insert their own profile"
  on public.profiles for insert
  with check ( auth.uid() = id );

create policy "Users can update own profile"
  on public.profiles for update
  using ( auth.uid() = id );
```

### 3. Environment Configuration

Create a `.env` file in your project root:
```env
# Supabase Configuration
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret  # Found in Project Settings → API
```

Add `.env` to your `.gitignore`:
```bash
echo ".env" >> .gitignore
```

### 4. Project Structure

```bash
solver-space/
├── assets/ # Static files
├── components/ # Reusable UI components
│ └── auth/
│ ├── login_form.py
│ └── signup_form.py
├── models/ # Database models
│ └── user.py
├── pages/ # Application pages
│ ├── index.py
│ ├── login.py
│ └── signup.py
├── services/ # Business logic
│ └── supabase.py # Supabase client configuration
├── .env # Environment variables (not in git)
├── .gitignore
├── README.md
└── solver_space.py # Main application file
```

### 5. Initialize Supabase Client

Create `services/supabase.py`:
```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
```

### 6. Run the Application
```bash
# Start the development server
reflex run
```

Visit `http://localhost:3000` to see your application.

## Authentication Flow

1. **Sign Up**:
   - User enters email, password, and username
   - Supabase creates auth.users entry
   - Our trigger creates matching profiles entry
   - Verification email sent (if enabled)

2. **Login**:
   - User enters email and password
   - Supabase validates credentials
   - JWT token issued and stored
   - User redirected to dashboard

3. **Protected Routes**:
   - JWT token validated on each request
   - Row Level Security (RLS) policies enforce access control
   - Invalid/expired tokens redirect to login

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| SUPABASE_URL | Your Supabase project URL | Yes |
| SUPABASE_KEY | Your Supabase anon/public key | Yes |
| SUPABASE_JWT_SECRET | JWT secret for token validation | Yes |

## Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes
4. Push to your fork and submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

