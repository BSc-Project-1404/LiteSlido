# LiteSlido

<img src="./docs/logo.png" width="40%" height="40%">


## Table of Contents

1. [Project Overview](#project-overview)
2. [Business Case](#business-case)
3. [Features](#features)
4. [System Architecture](#system-architecture)
5. [Tech Stack](#tech-stack)
6. [Installation & Setup](#installation--setup)
7. [Usage](#usage)

   * [Running the App](#running-the-app)
   * [User Flow](#user-flow)
8. [Technical Details](#technical-details)

   * [Data Models](#data-models)
   * [API & Views](#api--views)
   * [Frontend Templates](#frontend-templates)
   * [Styling & Dark Mode](#styling--dark-mode)
   * [Charting Results](#charting-results)
9. [Docker & Deployment](#docker--deployment)
10. [Testing](#testing)
11. [Contributing](#contributing)
12. [License](#license)

---

## Project Overview

LiteSlido is a lightweight clone of Slido—a real-time audience interaction platform—for creating, joining, and managing live events, polls, and Q\&A sessions. Entirely built using Django and Tailwind CSS, LiteSlido demonstrates how to leverage modern frameworks, containerization, and LLM-assisted code generation to deliver a polished, production-ready application within a short timeframe.

## Business Case

Organizations, lecturers, and online communities need quick, user-friendly tools to engage participants during presentations or virtual meetups. Paid platforms can be costly and bulky. LiteSlido offers:

* **Cost-efficiency**: Open-source, free to deploy on any infrastructure.
* **Rapid setup**: Dockerized services for one-command deployment.
* **Essential interactions**: Polls, Q\&A, and live results with charts.
* **User management**: Profiles, authentication, and robust permissions.

By delivering core engagement features in a minimal footprint, LiteSlido addresses budget-conscious teams and educators seeking customizable, self-hosted solutions.

## Features

### Event Management

* **Create & close events** with unique codes
* **Join events** via event code
* **Owner-only controls** for closing events

### Q\&A

* **Submit questions** tied to a specific event
* **Like/unlike questions** to upvote content
* **Sort questions** by popularity
* **Delete questions** (owner privilege)

### Polls

* **Create multi-option polls** dynamically
* **Vote once per user** with option selection
* **Real-time results** displayed as interactive bar charts
* **Results persistence** across page refreshes

### User Profiles

* **View & edit** personal info (full name, bio, avatar)
* **Change password** securely within the app

### UI & UX

* **Tailwind CSS** for responsive, modern design
* **Dark Mode toggle** with persisted preference
* **Accessible forms** with field-level and non-field error handling

## System Architecture

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   Browser   │ ←───── │   Django    │ ←───── │ PostgreSQL  │
│ (Tailwind,  │        │  Backend    │        │   Database  │
│  Chart.js)  │        │  Services   │        │             │
└─────────────┘        └─────────────┘        └─────────────┘
       ▲                     ▲                       ▲
       │                     │                       │
       │      ┌──────────────┴──────────────┐        │
       │      │        Docker & Compose     │        │
       │      └────────────────────────────┘        │
       │                                           │
       └───────────────────────────────────────────┘
```

* **Frontend**: Django templates + Tailwind CSS + Chart.js for result visualization.
* **Backend**: Django 5.2.4 with RESTful view patterns, authentication, signals.
* **Database**: PostgreSQL for event, user, question, poll persistence.
* **Containerization**: Docker & Docker Compose orchestrate web and db services.

## Tech Stack

* **Python & Django**: Core web framework
* **PostgreSQL**: Relational database
* **Tailwind CSS**: Utility-first styling
* **Chart.js**: Interactive bar charts
* **Docker & Compose**: Container management
* **Gunicorn** (future prod): WSGI HTTP server

## Installation & Setup

1. Clone the repo:

   ```bash
   git clone https://github.com/BSc-Project-1404/LiteSlido.git
   cd liteslido
   ```
2. Copy environment variables:

   ```bash
   cp .env.example .env
   ```
3. Build and start containers:

   ```bash
   docker compose up --build -d
   ```
4. Apply migrations and create superuser:

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```
5. Access the app at `http://localhost:8000/events/`.

## Usage

### Running the App

* **Web**: `http://localhost:8000/accounts/login/`
* **Admin**: `http://localhost:8000/admin/`

### User Flow

1. **Register/Login** → lands on **My Events** page
2. **Create New Event** or **Join Event** by code
3. Inside an event:

   * **Ask a question** → appears in the Q\&A feed
   * **Like/unlike** others’ questions → votes sort order
   * **Participate in polls** → see real-time chart results
4. **Profile** → view/edit personal info, change password
5. **Owner**: close/reopen event, delete any question or create polls

## Technical Details

### Data Models

* **User** (`django.contrib.auth`) + **Profile** (`1:1`)
* **Event**: `code`, `title`, `creator`, `is_closed`
* **Question**: `text`, `author`, `created_at`, `likes M2M`
* **Poll**: `question`, `event`, `created_at`
* **PollOption**: `text`, `poll`, `order`
* **PollVote**: `user`, `poll_option`, `timestamp`

### API & Views

* **Event List/Create**: `event_list`, `event_create`
* **Event Detail**: `event_detail` (handles Q\&A + polls)
* **Add Question**: `add_question`
* **Toggle Like**: `toggle_like` (POST)
* **Delete Question**: `delete_question` (owner only)
* **Add Poll**: `add_poll`, dynamic formset for options
* **Poll Detail/Vote**: `poll_detail` (GET shows form/results, POST records vote)
* **Toggle Close Event**: `toggle_close`
* **Profile**: `profile_view`, `profile_edit`, `change_password`

### Frontend Templates

* **Base**: `base.html` with navbar, dark-mode toggle, CSRF, static files
* **Forms**: consistent error handling (`non_field_errors`, field errors)
* **Event Pages**: responsive grids, card-based UI


### Charting Results

* **Chart.js** loaded from CDN
* `<canvas>` container given height (`h-64`) and full width
* **Bar chart** with custom colors, rounded bars, hidden gridlines
* Re-initializes on each page load to reflect real-time counts

## Docker & Deployment

* **`Dockerfile`**: Python 3.11, installs dependencies from `requirements.txt`
* **`docker-compose.yml`**: services for `web` and `db`
* **Volumes**: persist `postgres_data` and `media`
* **Commands**:

  * `docker compose up --build` → start development environment
  * future: add **production** with `nginx` + `gunicorn`

## Testing

* **Manual**: browser-based walkthrough of flows (register, create/join event, Q\&A, polls, profile)
* **Automated**: Django `TestCase` modules for:

  * Profile creation and editing
  * Password change
  * Poll voting
  * Permissions (owner-only actions)

Run tests:

```bash
docker compose exec web python manage.py test
```

---

**Enjoy interacting with your audience—spice up every session with LiteSlido!**
