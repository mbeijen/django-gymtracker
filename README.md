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
