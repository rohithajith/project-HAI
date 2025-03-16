# Installation Guide for Hotel Management System

This guide provides step-by-step instructions for setting up the Hotel Management System on a new system.

## Quick Setup (Recommended)

If you've cloned this repository, you can use our one-command setup:

```bash
npm run setup-and-start
```

This will install all dependencies and start the application.

## Manual Setup

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Step 1: Install Dependencies

```bash
# Install all dependencies (root, backend, and frontend)
npm run install:all
```

### Step 2: Start the Application

```bash
# Start both backend and frontend
npm start
```

### Step 3: Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api

## Setting Up Git for Your Own Repository

We've included a script to help you set up Git for this project:

```bash
# Make the script executable (if not already)
chmod +x setup-git.sh

# Run the script
./setup-git.sh
```

This will initialize a Git repository, add all files, and make an initial commit.

## Project Structure Overview

```
project-root/
├── frontend/                  # React frontend application
│   ├── public/                # Static files
│   └── src/                   # Source code
│       ├── components/        # UI components
│       ├── contexts/          # State management
│       ├── pages/             # Page components
│       └── services/          # API and WebSocket services
│
├── backend/                   # Node.js backend application
│   ├── config/                # Configuration files
│   ├── controllers/           # Request handlers
│   ├── models/                # Database models
│   ├── routes/                # API routes
│   └── services/              # Business logic
│
└── hotel_bookings.db          # SQLite database file
```

## Environment Variables

All necessary environment variables are included in the repository:

- Backend environment variables are in `backend/.env`

## Troubleshooting

If you encounter any issues:

1. **Port conflicts**: If ports 3000 or 5000 are already in use, modify the port in:
   - Backend: Edit `PORT` in `backend/.env`
   - Frontend: Create a `.env` file in the frontend directory with `PORT=3001`

2. **Database errors**: If you encounter database errors, try deleting the `hotel_bookings.db` file and restart the application.

3. **Missing dependencies**: If you encounter errors about missing modules, run:
   ```
   npm run install:all
   ```

For more detailed information, refer to the README.md file.