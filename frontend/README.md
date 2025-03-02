# Sentient Inbox Frontend

Modern, responsive web interface for the Sentient Inbox application - an intelligent email management system with AI-powered email analysis.

## Features

- **Modern UI**: Clean, professional design with smooth animations and responsive layout
- **Pre-login Homepage**: Showcases product features, benefits, and how the system works
- **Authentication**: User login interface with form validation
- **Interactive Elements**: Animated sections and responsive components
- **Mobile-Friendly**: Fully responsive design that works across all device sizes

## Tech Stack

- **React**: Frontend library for building user interfaces
- **React Router**: Navigation and routing between pages
- **Framer Motion**: Smooth animations and transitions
- **Material UI Icons**: High-quality icon set
- **Modern CSS**: Custom styling using CSS variables for consistent theming

## Running the Frontend

### Prerequisites

- Node.js (v14 or newer recommended)
- npm or yarn package manager

### Installation

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

3. Start the development server:
   ```
   npm start
   ```
   or
   ```
   yarn start
   ```

4. Open your browser to `http://localhost:3000` to view the application

## Project Structure

- `/src/components`: Reusable UI components
- `/src/pages`: Main page components (HomePage, LoginPage)
- `/src/styles`: Global CSS styles and variables
- `/src/utils`: Utility functions and helpers
- `/src/assets`: Static assets like images and icons

## Integration with Backend API

The frontend is designed to connect with the Sentient Inbox API backend. By default, it expects the API to be running at `http://localhost:8000`.

## Demo Credentials

For testing purposes, you can use these demo credentials:

- Email: `demo@example.com`
- Password: `password`

## Next Steps

- Dashboard implementation
- Email processing visualization
- User settings and preferences
- Responsive email list views
- Meeting management interface