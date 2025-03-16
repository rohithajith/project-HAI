#!/bin/bash

# Initialize Git repository
git init

# Add all files to Git
git add .

# Make initial commit
git commit -m "Initial commit: Hotel Management System"

# Instructions for adding a remote repository
echo ""
echo "Git repository initialized with initial commit."
echo ""
echo "To push to a remote repository, run the following commands:"
echo "  git remote add origin <your-repository-url>"
echo "  git push -u origin main"
echo ""
echo "Your project is now ready to be shared across different systems!"