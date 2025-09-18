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

- **Backend**: Django (latest version)
- **Database**: SQLite
- **Authentication**: django-allauth for user registration and login
- **Frontend**: Django templates with HTMX for dynamic interactions
- **Styling**: Lightweight CSS/JS framework (to be determined)
- **Best Practices**: Following Django conventions and recommended modules
- **Unit Tests**: we should have unit tests for all paths and functions to be sure we can refactor without breaking stuff
