# LiteSlido

<img src="./docs/logo.png" width="40%" height="40%">

**A modern, lightweight audience interaction platform for live events, polls, and Q&A sessions.**

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [User Experience](#user-experience)
4. [System Architecture](#system-architecture)
5. [Tech Stack](#tech-stack)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Technical Implementation](#technical-implementation)
9. [Docker & Deployment](#docker--deployment)
10. [Development & Testing](#development--testing)

---

## Project Overview

LiteSlido is a modern, feature-rich clone of Slido—a real-time audience interaction platform—built with Django and enhanced with cutting-edge UI/UX design. It enables organizations, educators, and communities to create engaging live events with interactive polls, Q&A sessions, and real-time audience participation.

### What Makes LiteSlido Special

- **🎯 Dual User Experience**: Both authenticated users and anonymous participants can engage
- **🎨 Modern UI/UX**: Beautiful, responsive design with Tailwind CSS and smooth animations
- **📊 Interactive Charts**: Real-time poll results with Chart.js and enhanced visualizations
- **🔐 Secure & Scalable**: Built with Django best practices and Docker containerization
- **🚀 Production Ready**: Comprehensive error handling, responsive design, and performance optimization

## Key Features

### 🌟 Event Management
- **Create Events**: Generate unique event codes for easy sharing
- **Join Events**: Participate via simple event code entry
- **Event Control**: Event creators can close/reopen events
- **Real-time Updates**: Live synchronization across all participants

### 💬 Interactive Q&A
- **Authenticated Users**: Ask questions, like/unlike, and manage content
- **Anonymous Participation**: Anyone can ask questions without registration
- **Smart Sorting**: Questions automatically sorted by popularity (likes)
- **Content Moderation**: Event creators can delete inappropriate questions

### 📊 Dynamic Polling System
- **Multi-Option Polls**: Create polls with unlimited custom options
- **Real-time Voting**: Instant vote recording and result updates
- **Beautiful Charts**: Interactive bar charts with smooth animations
- **Vote Validation**: One vote per user per poll with secure tracking

### 👤 User Management
- **Profile System**: Customizable user profiles with avatars
- **Authentication**: Secure login/registration with enhanced forms
- **Password Management**: Built-in password change functionality
- **Role-based Access**: Different permissions for creators and participants

### 🎨 Enhanced User Experience
- **Password Visibility Toggles**: Eye icons for password fields
- **Interactive Form States**: Hover, focus, and validation feedback
- **Responsive Design**: Works perfectly on all devices
- **Smooth Animations**: CSS transitions and Chart.js animations

## User Experience

### For Event Creators
1. **Register/Login** with enhanced form experience
2. **Create Events** with custom titles and unique codes
3. **Manage Content** - moderate questions, create polls
4. **Control Access** - close/reopen events as needed
5. **View Analytics** - see engagement metrics and results

### For Authenticated Participants
1. **Join Events** using event codes
2. **Ask Questions** and interact with others
3. **Participate in Polls** and see real-time results
4. **Like/Unlike** questions to influence sorting
5. **Manage Profile** and personal information

### For Anonymous Users
1. **Join Events** without registration
2. **Ask Questions** with optional name display
3. **View Content** and poll results
4. **Limited Interaction** - read-only access to maintain security

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django        │    │   PostgreSQL    │
│                 │    │   Backend       │    │   Database      │
│ • Tailwind CSS  │◄──►│ • Views         │◄──►│ • User Data     │
│ • Chart.js      │    │ • Services      │    │ • Events        │
│ • Responsive    │    │ • Models        │    │ • Questions     │
│ • Animations    │    │ • Forms         │    │ • Polls         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         │         ┌─────────────────────────────┐        │
         │         │      Docker & Compose      │        │
         │         │   • Web Service            │        │
         │         │   • Database Service       │        │
         │         │   • Volume Persistence     │        │
         └─────────┴─────────────────────────────┴────────┘
```

### Architecture Highlights
- **Service Layer**: Business logic separated from views for maintainability
- **Template Inheritance**: Consistent UI across all pages
- **Form Validation**: Client and server-side validation with user feedback
- **Security**: CSRF protection, authentication, and permission checks

## Tech Stack

### Backend
- **Python 3.11+**: Modern Python with type hints support
- **Django 5.2.4**: Latest Django with security updates
- **PostgreSQL**: Robust relational database
- **Django ORM**: Efficient database operations

### Frontend
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js 3.9.1**: Interactive data visualization
- **Vanilla JavaScript**: Modern ES6+ features
- **Responsive Design**: Mobile-first approach

### Infrastructure
- **Docker**: Containerized development environment
- **Docker Compose**: Multi-service orchestration
- **Nginx** (future): Production web server
- **Gunicorn** (future): WSGI application server

## Installation & Setup

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Modern web browser

### Quick Start
1. **Clone the repository**:
   ```bash
   git clone https://github.com/BSc-Project-1404/LiteSlido.git
   cd LiteSlido
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build -d
   ```

3. **Apply database migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create admin user**:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**:
   - **Main App**: http://localhost:8000/events/
   - **Admin Panel**: http://localhost:8000/admin/
   - **Login**: http://localhost:8000/accounts/login/
   - **Register**: http://localhost:8000/accounts/register/

### Environment Configuration
The application uses environment variables for configuration. Key settings include:
- Database connection parameters
- Secret key for Django
- Debug mode settings
- Media file storage paths

## Usage Guide

### Getting Started
1. **Register an Account**: Use the enhanced registration form with password visibility toggles
2. **Login**: Access your personalized dashboard
3. **Create Your First Event**: Generate a unique event code for sharing

### Event Participation
1. **Join Events**: Enter event codes on the main page
2. **Ask Questions**: Submit questions with real-time updates
3. **Vote in Polls**: Participate in interactive polls
4. **View Results**: See beautiful charts and statistics

### Anonymous Participation
1. **Enter Event Code**: No registration required
2. **Ask Questions**: Optional name display
3. **View Content**: Read-only access to maintain security

### Advanced Features
- **Event Management**: Close/reopen events, moderate content
- **Profile Customization**: Upload avatars, edit personal information
- **Password Security**: Secure password change functionality
- **Content Moderation**: Delete inappropriate questions

## Technical Implementation

### Data Models
```python
# Core Models
User (Django Auth) + Profile (1:1 relationship)
Event: code, title, creator, is_closed, created_at
Question: text, author, author_name, event, created_at, likes
Poll: question, event, created_at
PollOption: text, poll, order
PollVote: user, poll_option, timestamp
```

### Key Features Implementation
- **Anonymous Questions**: Unified Question model with optional author field
- **Service Layer**: Business logic separated from views
- **Form Enhancement**: Custom styled forms with interactive elements
- **Chart Integration**: Dynamic Chart.js loading with error handling

### Security Features
- **Authentication**: Django's built-in user authentication
- **Permission System**: Role-based access control
- **CSRF Protection**: Cross-site request forgery prevention
- **Input Validation**: Server-side validation with user feedback

### Performance Optimizations
- **Database Indexing**: Optimized queries for large datasets
- **Template Caching**: Efficient template rendering
- **Static File Optimization**: Compressed CSS and JavaScript
- **Responsive Images**: Optimized media file handling

## Docker & Deployment

### Development Environment
```bash
# Start services
docker-compose up --build -d

# View logs
docker-compose logs -f web

# Execute commands
docker-compose exec web python manage.py shell

# Restart services
docker-compose restart
```

### Production Considerations
- **Environment Variables**: Secure configuration management
- **Static Files**: CDN integration for better performance
- **Database**: Connection pooling and optimization
- **Monitoring**: Health checks and logging
- **SSL/TLS**: Secure HTTPS connections

### Scaling Options
- **Horizontal Scaling**: Multiple web service instances
- **Load Balancing**: Nginx reverse proxy configuration
- **Database Clustering**: PostgreSQL read replicas
- **Caching**: Redis for session and data caching

## Development & Testing

### Development Workflow
1. **Feature Development**: Create feature branches
2. **Code Review**: Pull request reviews and testing
3. **Testing**: Automated and manual testing
4. **Deployment**: Staging and production releases

### Testing Strategy
```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific test modules
docker-compose exec web python manage.py test events.tests

# Check code quality
docker-compose exec web python manage.py check
```

### Code Quality
- **PEP 8**: Python style guide compliance
- **Type Hints**: Modern Python type annotations
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Graceful error handling and user feedback

---

## Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Transform your events with LiteSlido - where engagement meets innovation! 🚀**

*Built with ❤️ using Django, Tailwind CSS, and modern web technologies.*
