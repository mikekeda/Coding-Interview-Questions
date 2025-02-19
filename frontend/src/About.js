import React from 'react';
import { Container, Typography, Box } from '@mui/material';

function About() {
  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" gutterBottom>
          About This Site
        </Typography>
        <Typography variant="body1" paragraph>
          This site provides a curated list of coding interview questions,
          complete with hints, AI generated solutions, and the ability to filter by company,
          difficulty, and data structures. Our mission is to help developers
          prepare for technical interviews effectively.
        </Typography>
        <Typography variant="body1" paragraph>
          Built with React, Sanic, SQLite, and Material UI, this project is an
          ongoing effort to create a comprehensive practice resource for
          programmers at all levels. We welcome feedback and suggestions for
          improvement!
        </Typography>
      </Box>
    </Container>
  );
}

export default About;
