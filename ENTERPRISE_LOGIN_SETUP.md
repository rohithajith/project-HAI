# Enterprise Login System Setup

This document provides instructions for setting up and running the enterprise login system for the hotel management application.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Testing the Login System](#testing-the-login-system)
7. [API Endpoints](#api-endpoints)
8. [Security Considerations](#security-considerations)

## Overview

The enterprise login system provides secure authentication and authorization for the hotel management application. It supports multiple user types (admin, manager, staff, guest) with different permission levels, and includes features such as:

- JWT-based authentication
- Role-based access control
- Password reset functionality
- Audit logging
- Session management

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)
- SQLite3

## Installation

1. Install backend dependencies:

```bash
cd backend
npm install
```

2. Install frontend dependencies:

```bash
cd frontend
npm install
```

## Database Setup

The application uses SQLite for data storage. The database schema includes tables for users, roles, permissions, and more.

1. Create the password reset tokens table:

```bash
cd backend
node scripts/createPasswordResetTable.js
```

2. Seed the database with test users:

```bash
cd backend
node scripts/seedUsers.js
```

This will create the following test users:

| Email | Password | Role | Type |
|-------|----------|------|------|
| admin@hotel.com | Admin123! | admin | admin |
| manager@hotel.com | Manager123! | manager | staff |
| staff@hotel.com | Staff123! | staff | staff |
| guest1@example.com | Guest123! | guest | guest |
| guest2@example.com | Guest123! | guest | guest |

## Running the Application

1. Start the backend server:

```bash
cd backend
npm run dev
```

The backend server will run on http://localhost:5000 by default.

2. Start the frontend development server:

```bash
cd frontend
npm start
```

The frontend application will run on http://localhost:3000 by default.

## Testing the Login System

1. Open your browser and navigate to http://localhost:3000
2. You should see the landing page with login and registration options
3. Use one of the test user credentials to log in
4. Different user types will be redirected to different dashboards based on their roles

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/auth/register` | POST | Register new user | Public |
| `/api/auth/login` | POST | Authenticate user | Public |
| `/api/auth/logout` | POST | Logout user | Authenticated |
| `/api/auth/refresh-token` | POST | Refresh JWT token | Authenticated |
| `/api/auth/me` | GET | Get current user | Authenticated |
| `/api/auth/password/reset-request` | POST | Request password reset | Public |
| `/api/auth/password/reset` | POST | Reset password with token | Public |
| `/api/auth/password/change` | POST | Change password | Authenticated |

### User Management Endpoints

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/users` | GET | List users | Admin, Manager |
| `/api/users/:id` | GET | Get user details | Admin, Manager, Self |
| `/api/users` | POST | Create new user | Admin |
| `/api/users/:id` | PUT | Update user | Admin, Self |
| `/api/users/:id` | DELETE | Delete user | Admin |
| `/api/users/:id/roles` | GET | Get user roles | Admin |
| `/api/users/:id/roles` | PUT | Update user roles | Admin |

## Security Considerations

The login system implements several security measures:

1. **Password Security**:
   - Passwords are hashed using bcrypt
   - Password policies enforce minimum length and complexity

2. **JWT Security**:
   - Short-lived access tokens (1 hour by default)
   - Refresh token rotation
   - Token blacklisting on logout

3. **Protection Against Common Attacks**:
   - CORS protection
   - Rate limiting for login attempts
   - Protection against brute force attacks

4. **Audit Logging**:
   - All authentication events are logged
   - User management actions are logged
   - IP addresses and user agents are recorded

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
PORT=5000
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=1h
JWT_REFRESH_EXPIRES_IN=7d
```

For production, make sure to use strong, randomly generated secrets.