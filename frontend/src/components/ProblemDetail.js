import React from 'react';
import { Box, Typography, Accordion, AccordionSummary, AccordionDetails, Link } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Helmet } from 'react-helmet';

function ProblemDetail({ problem, handleCompanyClick, handleDataStructureClick }) {
  if (!problem) {
    return <Typography variant="body1">Select a problem to view its details.</Typography>;
  }

  return (
    <Box>
      <Helmet>
        <title>{`${problem.title} - Coding Interview Prep`}</title>
        <meta
          name="description"
          content={`Practice solving: ${problem.title}. Enhance your coding interview skills with curated hints, solutions, and data-structure insights.`}
        />
      </Helmet>
      <Typography variant="h5" gutterBottom>
        {problem.id}. {problem.title}
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        {problem.problem}
      </Typography>

      {problem.company && (
        <Typography variant="body1">
          <strong>Company:</strong>{' '}
          <Link component="button" variant="body2" onClick={() => handleCompanyClick(problem.company)}>
            {problem.company}
          </Link>
        </Typography>
      )}
      {problem.source && (
        <Typography variant="body1">
          <strong>Source:</strong> {problem.source}
        </Typography>
      )}

      {/* Additional fields (difficulty, data structures, etc.) */}
      {/* e.g. Data structures, time complexity, etc. */}
      {/* Hints */}
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6">Hints</Typography>
        {problem.hints && problem.hints.length > 0 ? (
          problem.hints.map((hint, index) => (
            <Accordion key={index} sx={{ mt: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Hint #{index + 1}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2">{hint}</Typography>
              </AccordionDetails>
            </Accordion>
          ))
        ) : (
          <Typography variant="body2">No hints available.</Typography>
        )}
      </Box>

      {/* Solution */}
      <Box sx={{ mt: 3 }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Show AI-generated Solution</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="h6">Solution</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {problem.solution}
              </Typography>
              <Box>
                <Typography variant="h6">Code Solution</Typography>
                <SyntaxHighlighter
                  language="python"
                  style={solarizedlight}
                  customStyle={{ borderRadius: 4 }}
                >
                  {problem.code_solution}
                </SyntaxHighlighter>
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
    </Box>
  );
}

export default ProblemDetail;
