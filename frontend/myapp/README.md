# MyHotelApp Frontend

This is the frontend application for the MyHotelApp project, built with Create React App. It provides interfaces for both hotel guests and staff members.

## Overview

The application presents different views based on the user's role:

*   **Guests:** Interact with a chatbot interface for assistance and requests.
*   **Staff (Room Service, Maintenance, Wellness, Admin):** Access a dashboard to view and manage relevant information and tasks, likely interacting with guest requests received via the chatbot.

## Features

*   **Role-Based Access:** Users select their role upon entering the application (Guest, RoomServiceAgent, Maintenance, Wellness, Admin).
*   **Guest Chatbot:** Provides an interactive chat interface for guests.
*   **Staff Dashboard:** A central hub for staff members to manage their responsibilities.
*   **Real-time Communication:** Utilizes Socket.IO for real-time updates and interactions.
*   **Responsive UI:** Built with React-Bootstrap.

## Routing and Views

The application uses a simple conditional rendering logic based on the selected role (`agent` stored in `localStorage`):

1.  **Role Selection:** If no role is selected, a screen prompts the user to choose their role.
2.  **Guest View:** If the role is "Guest", the `ChatBot` component is rendered.
3.  **Staff View:** If the role is any other staff role, the `Dashboard` component is rendered.
4.  **Navigation:** A `CustomNavbar` is displayed once a role is selected.
5.  **Role Reset:** A button allows resetting the selected role and returning to the selection screen.

## Key Dependencies

*   React & React DOM
*   React Bootstrap & Bootstrap
*   Socket.IO Client
*   Framer Motion
*   Create React App (react-scripts)

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.
