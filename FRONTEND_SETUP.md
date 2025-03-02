# Sentient Inbox Frontend Setup Instructions

Follow these step-by-step instructions to set up and run the Sentient Inbox frontend.

## Prerequisites

Ensure you have the following installed on your system:
- Node.js (v14 or newer)
- npm or yarn package manager
- Git

## Step 1: Clone the Repository (If Not Already Done)

```bash
git clone https://github.com/itsvetkov1/Sentient-Inbox.git
cd Sentient-Inbox
```

## Step 2: Check Out the API Branch

```bash
git checkout API
```

## Step 3: Navigate to the Frontend Directory

```bash
cd frontend
```

## Step 4: Install Dependencies

Using npm:
```bash
npm install
```

Or using yarn:
```bash
yarn install
```

This will install all required packages defined in package.json, including:
- React and React DOM
- React Router
- Framer Motion for animations
- Material UI icons
- Axios for API requests

## Step 5: Configure Environment Variables (Optional)

The frontend is already configured with a `.env` file containing:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=0.1.0
REACT_APP_ENV=development
```

If your API is running on a different URL, modify the REACT_APP_API_URL value accordingly.

## Step 6: Start the Development Server

Using npm:
```bash
npm start
```

Or using yarn:
```bash
yarn start
```

This will:
1. Compile the React application
2. Start a development server
3. Open your default browser to http://localhost:3000

## Step 7: Exploring the Application

1. **Home Page**: The default route (/) will show the landing page with:
   - Hero section
   - Features overview
   - How It Works section
   - Call to Action

2. **Login Page**: Click "Sign In" or "Get Started" to access the login page:
   - Use demo credentials:
     - Email: demo@example.com
     - Password: password

## Step 8: Development Notes

If you wish to modify the frontend:

### Component Structure:
- Main components are in `/src/components/`
- Page layouts are in `/src/pages/`
- Global styles are in `/src/styles/globals.css`

### Adding New Pages:
1. Create a new component in `/src/pages/`
2. Add a new route in `/src/App.js`

### Styling:
- The application uses inline styles and CSS variables
- CSS variables are defined in `/src/styles/globals.css`

## Troubleshooting

### Common Issues:

1. **"Module not found" errors**:
   - Make sure you've run `npm install` or `yarn install`
   - Check that package names are spelled correctly in import statements

2. **Blank page or rendering issues**:
   - Check browser console for errors (F12 or right-click > Inspect > Console)
   - Verify React components are correctly exported and imported

3. **API connection issues**:
   - Verify API is running at the URL specified in .env
   - Check network tab in browser developer tools for failed requests

4. **Port conflicts**:
   - If port 3000 is already in use, React will prompt you to use a different port

For additional help, consult the React documentation or create an issue in the project repository.