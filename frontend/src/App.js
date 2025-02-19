import React, { useState, useEffect } from 'react';
import { AppBar, Container, Toolbar, Typography, Box, Switch, FormControlLabel } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// React Router imports
import { Routes, Route, Link } from 'react-router-dom';

import About from './About';  // The About page you just created
import ProblemsPage from './Problems'; // import the new page

// Light theme
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#9c27b0' }
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h5: { fontWeight: 600 },
    h6: { fontWeight: 500 }
  }
});

// Dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#90caf9' },
    secondary: { main: '#ce93d8' }
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h5: { fontWeight: 600 },
    h6: { fontWeight: 500 }
  }
});

function App() {
  // Dark mode state
  const [darkMode, setDarkMode] = useState(false);

  // Load dark mode preference from localStorage on mount
  useEffect(() => {
    const storedDarkMode = localStorage.getItem('darkMode');
    if (storedDarkMode !== null) {
      setDarkMode(JSON.parse(storedDarkMode));
    }
  }, []);

  // Whenever darkMode changes, store it
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
  };

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default', color: 'text.primary' }}>

        {/* Top App Bar with Dark Mode Toggle */}
        <AppBar position="static">
          <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                Coding Interview Problems
              </Link>
            </Typography>
            {/* Link to About page in the AppBar */}
            <Link to="/about" style={{ textDecoration: 'none', color: 'inherit', marginRight: '16px' }}>
              About
            </Link>
            <FormControlLabel
              control={<Switch checked={darkMode} onChange={handleDarkModeToggle} color="default" />}
              label="Dark Mode"
            />
          </Toolbar>
        </AppBar>

        <Container maxWidth="lg" sx={{ mt: 4 }}>
          {/* Define your routes here */}
          <Routes>
            {/* Existing "main" route, possibly the problem list */}
            <Route
              path="/"
              element={
                // your existing Home / Problem List / Filters layout
                <ProblemsPage />
              }
            />

            {/* The new About page */}
            <Route path="/about" element={<About />} />
          </Routes>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
