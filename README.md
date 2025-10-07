# Django Gym Tracker

A Django web application designed to track gym workouts and exercise progress. The app is optimized for mobile browsers but works well on desktop devices too. It follows an HTML-first approach using Django templates with HTMX, avoiding heavy JavaScript frameworks like React.

## Use Case

I go to the gym about once or twice a week, sometimes with my girlfriend. Currently, I use Apple Notes on my phone to track which machines or exercises I performed and how much weight I used. This helps me remember my previous performance - for example, what weight I used on the leg press last week - so I can properly adjust the machine for my current session.

When my girlfriend joins me, I also track her weight usage from previous sessions. I note whether I used more or less weight than last time, and after each exercise, I rate the difficulty as easy, OK, or hard. This helps me decide whether to increase the weight next time or continue with the current weight until it becomes easier.

It's also important for me to track how many exercises I've completed that day and how many days I've been to the gym this week/month.

This app aims to replace my current Apple Notes system with a more structured and user-friendly solution.

## Features

### Workout Sessions

- Track workout sessions that occur on a single day
- Record which exercises were performed during each session
- Add and remove exercises as you expand your workout repertoire

### Multi-User Support

- Multi-user Django application with individual user settings and profiles
- Users can start workout sessions and indicate if they're working out alone or with a partner
- Each user sees a personalized list of available exercises

### Exercise Tracking

- View historical performance data for each exercise, including trends (increasing/decreasing weight)
- See previous difficulty ratings (1-10 scale) to gauge exercise progression
- Get weight recommendations based on previous sessions
- Record actual weight used and difficulty rating after completing each exercise

### Session Management

- Add exercises to your current workout session
- Complete the session when finished
- View progress over time

## Technical Stack

- **Backend**: Django 5.2.6
- **Database**: SQLite
- **Authentication**: django-allauth for user registration and login
- **Frontend**: Django templates with HTMX for dynamic interactions
- **Styling**: Bootstrap 5.3 for mobile-first responsive design
- **Best Practices**: Following Django conventions and recommended modules

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd django-gymtracker
   ```

2. **Install dependencies with uv (recommended)**

   ```bash
   uv sync
   ```

   Or with pip:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. **Run migrations**

   ```bash
   uv run python manage.py migrate
   ```

4. **Create test users for development**

   ```bash
   uv run python manage.py create_test_users
   ```

5. **Start the development server**

   ```bash
   uv run python manage.py runserver
   ```

   The server will start on port 8098 by default.

6. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8098/`
   - Login with one of the test accounts or create your own

## Development Login

For easy testing, the app comes with two pre-created test accounts:

- **Alice**: `alice@example.com` / `some_pass`
- **Bob**: `bob@example.com` / `some_pass`

These accounts are set up as workout partners, so you can test the multi-user features.

## Features Implemented

✅ **User Authentication**: Email-based login and registration
✅ **Workout Sessions**: Create, manage, and complete workout sessions
✅ **Exercise Tracking**: Add exercises with weight, reps, sets, and difficulty rating
✅ **Exercise Library**: Pre-populated with common gym exercises
✅ **Weight Recommendations**: Smart suggestions based on previous performance
✅ **Mobile-First Design**: Optimized for mobile browsers
✅ **Workout History**: View and filter past workout sessions
✅ **Admin Interface**: Manage exercises and view user data
✅ **Responsive UI**: Works great on both mobile and desktop

## Usage

1. **Create Account**: Sign up with your email address
2. **Start Workout**: Click "Start New Workout" from the dashboard
3. **Add Exercises**: Select exercises and record your performance
4. **Track Progress**: View your workout history and progress over time
5. **Get Recommendations**: The app suggests weights based on your previous performance

## Development

The app follows Django best practices with:

- Clean separation of concerns (models, views, templates)
- Mobile-first responsive design
- HTMX for dynamic interactions without heavy JavaScript
- Comprehensive forms with validation
- Admin interface for data management
- Modern Python packaging with `pyproject.toml`
- Fast dependency management with `uv`

## Email Configuration

The app is configured to work with Mailpit for local development and supports production email providers via environment variables.

### Local Development (Mailpit)

For local development, the app is pre-configured to use Mailpit on `localhost:1025`. Just start Mailpit and the app will automatically use it for sending emails.

### Production Deployment

For production deployment, create a `.env` file in your home directory (`~/.env`) with your email provider settings:

```bash
# Copy the example file
cp env.example ~/.env

# Edit with your email provider settings
nano ~/.env
```

Example configuration for Gmail:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## Production Deployment

### Error Tracking with Bugsink

The app is configured to work with Bugsink (Sentry API compatible) for error tracking in production. Bugsink provides a self-hosted alternative to Sentry with full API compatibility.

#### Setup Bugsink Error Tracking

1. **Install and configure Bugsink** on your server
2. **Add Bugsink DSN to your environment**:

```bash
# Add to your ~/.env file
BUGSINK_DSN=https://your-bugsink-instance.com/api/your-project-id/store/
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=1.0.0
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

#### Production Environment Variables

For production deployment, configure these environment variables in your `~/.env` file:

```env
# Security
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (configure with your provider)
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@yourdomain.com

# Error tracking
BUGSINK_DSN=https://your-bugsink-instance.com/api/your-project-id/store/
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=1.0.0
```

#### Deployment Steps

**Initial Server Setup:**

> **Security Note**: The gymtracker user is created without sudo permissions for security. The setup script assumes `/srv/gymtracker` exists and is owned by the gymtracker user.

1. **Run the setup script on your VPS**:

   ```bash
   # On your VPS, clone the repository and run setup
   git clone <your-repo-url> /tmp/gymtracker
   cd /tmp/gymtracker
   chmod +x deploy/setup-server.sh
   sudo ./deploy/setup-server.sh
   ```

2. **Configure environment variables**:
   ```bash
   # Copy and edit the environment file
   sudo cp env.example /home/gymtracker/.env
   sudo chown gymtracker:gymtracker /home/gymtracker/.env
   sudo -u gymtracker nano /home/gymtracker/.env  # Edit with your production values
   ```

**Automatic Deployment:**

The app uses GitHub Actions for automated deployment:

1. **Push to main branch** - triggers automatic deployment
2. **Manual deployment** - use "workflow_dispatch" in GitHub Actions

**Manual Deployment (if needed):**

1. **Stop the service**:

   ```bash
   systemctl --user stop gymtracker
   ```

2. **Deploy files**:

   ```bash
   rsync -av --delete --exclude='db.sqlite3' --exclude='data/' --exclude='staticfiles/' . /srv/gymtracker/app/
   ```

3. **Install dependencies and run migrations**:

   ```bash
   cd /srv/gymtracker/app
   uv sync
   uv run python manage.py migrate
   uv run python manage.py collectstatic --noinput
   ```

4. **Start the service**:
   ```bash
   systemctl --user start gymtracker
   ```

**Service Management:**

```bash
# Check service status
systemctl --user status gymtracker

# Start/stop/restart service
systemctl --user start gymtracker
systemctl --user stop gymtracker
systemctl --user restart gymtracker

# View logs
journalctl --user -u gymtracker -f
```

### Management Commands

- `uv run python manage.py create_test_users` - Creates Alice and Bob test accounts for development
- `uv run python manage.py createsuperuser` - Create an admin user for the Django admin interface
- `uv run pytest` - Run the test suite
- `uv run python manage.py runserver` - Start the development server

### Testing the App

1. Run `uv run python manage.py create_test_users` to create test accounts
2. Start the server with `uv run python manage.py runserver`
3. Login with `alice@example.com` / `some_pass` or `bob@example.com` / `some_pass`
4. Create workout sessions and add exercises to test the functionality
5. Run `uv run pytest` to execute the test suite
