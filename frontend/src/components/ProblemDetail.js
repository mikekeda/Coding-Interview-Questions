import React from 'react';
import {
  Box,
  Chip,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Link,
  Grid,
  Stack
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Helmet } from 'react-helmet';

function ProblemDetail({
  problem,
  handleCompanyClick,
  handleDataStructureClick,
  handleDifficultyClick
}) {
  if (!problem) {
    return (
      <Typography variant="body1">
        Select a problem to view its details.
      </Typography>
    );
  }

  // Optional color mapping for difficulty
  const difficultyColorMap = {
    Easy: 'success',
    Medium: 'warning',
    Hard: 'error'
  };

  return (
    <Box>
      {/* SEO */}
      <Helmet>
        <title>{`${problem.title} - Coding Interview Prep`}</title>
        <meta
          name="description"
          content={`Practice solving: ${problem.title}. Enhance your coding interview skills with curated hints, solutions, and data-structure insights.`}
        />
      </Helmet>

      {/* Title & Description */}
      <Typography variant="h5" gutterBottom>
        {problem.id}. {problem.title}
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        {problem.problem}
      </Typography>

      {/* Company & Source (Stack them for spacing) */}
      <Stack spacing={1} sx={{ mb: 2 }}>
        {problem.company && (
          <Typography variant="body1">
            <strong>Company:</strong>{' '}
            <Link
              component="button"
              variant="body2"
              onClick={() => handleCompanyClick(problem.company)}
              underline="hover"
            >
              {problem.company}
            </Link>
          </Typography>
        )}
        {problem.source && (
          <Typography variant="body1">
            <strong>Source:</strong> {problem.source}
          </Typography>
        )}
      </Stack>

      {/* Data Structures & Difficulty */}
      <Stack spacing={1} sx={{ mb: 2 }}>
        {/* Data Structures */}
        {problem.data_structures?.length > 0 && (
          <Box>
            <strong>Data Structures:</strong>{' '}
            {problem.data_structures.map((ds, idx) => (
              <Chip
                key={ds}
                label={ds}
                variant="outlined"
                color="primary"
                size="small"
                onClick={() => handleDataStructureClick(ds)}
                sx={{ mr: 1, mb: 1, cursor: 'pointer' }}
              />
            ))}
          </Box>
        )}

        {/* Difficulty */}
        <Box>
          <strong>Difficulty:</strong>{' '}
          {problem.difficulty ? (
            <Chip
              label={problem.difficulty}
              color={difficultyColorMap[problem.difficulty] || 'default'}
              size="small"
              onClick={() => handleDifficultyClick(problem.difficulty)}
              sx={{ cursor: 'pointer' }}
            />
          ) : (
            'N/A'
          )}
        </Box>
      </Stack>

      {/* Additional Metadata in a 2-column Grid */}
      <Grid container spacing={1} sx={{ mb: 2 }}>
        {/* Time Complexity */}
        <Grid item xs={6} sm={4} md={3}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Time Complexity:
          </Typography>
        </Grid>
        <Grid item xs={6} sm={8} md={9}>
          <Typography variant="body2">
            {problem.time_complexity || 'N/A'}
          </Typography>
        </Grid>

        {/* Space Complexity */}
        <Grid item xs={6} sm={4} md={3}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Space Complexity:
          </Typography>
        </Grid>
        <Grid item xs={6} sm={8} md={9}>
          <Typography variant="body2">
            {problem.space_complexity || 'N/A'}
          </Typography>
        </Grid>

        {/* Passes Allowed (if present) */}
        {problem.passes_allowed !== null && (
          <>
            <Grid item xs={6} sm={4} md={3}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Passes Allowed:
              </Typography>
            </Grid>
            <Grid item xs={6} sm={8} md={9}>
              <Typography variant="body2">
                {problem.passes_allowed}
              </Typography>
            </Grid>
          </>
        )}

        {/* Edge Cases */}
        <Grid item xs={6} sm={4} md={3}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Edge Cases:
          </Typography>
        </Grid>
        <Grid item xs={6} sm={8} md={9}>
          <Typography variant="body2">
            {problem.edge_cases.join(', ') || 'N/A'}
          </Typography>
        </Grid>

        {/* Input Types */}
        <Grid item xs={6} sm={4} md={3}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Input Types:
          </Typography>
        </Grid>
        <Grid item xs={6} sm={8} md={9}>
          <Typography variant="body2">
            {problem.input_types.join(', ') || 'N/A'}
          </Typography>
        </Grid>

        {/* Output Types */}
        <Grid item xs={6} sm={4} md={3}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Output Types:
          </Typography>
        </Grid>
        <Grid item xs={6} sm={8} md={9}>
          <Typography variant="body2">
            {problem.output_types.join(', ') || 'N/A'}
          </Typography>
        </Grid>
      </Grid>

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
              <Typography variant="h6" sx={{ mb: 1 }}>
                Solution
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {problem.solution}
              </Typography>
              <Box>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  Code Solution
                </Typography>
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
