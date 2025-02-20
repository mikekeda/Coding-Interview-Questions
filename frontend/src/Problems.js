import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Box,
  Autocomplete,
  TextField,
  Pagination,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  CircularProgress,
  Link,
  IconButton,
  Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';

// For Python syntax highlighting
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';

import './App.css'; // optional if you need global styles from your original

// Example difficulties we might color-code with Chips
const difficulties = ['Easy', 'Medium', 'Hard'];

// Map difficulty -> color for Chip
const difficultyColorMap = {
  Easy: 'success',
  Medium: 'warning',
  Hard: 'error'
};

const limit = 10; // items per page

const protocol = window.location.protocol;
const hostname = window.location.hostname;
const baseUrl = hostname === 'localhost'
  ? 'http://localhost:8000'
  : `${protocol}//${hostname}`;

function ProblemsPage() {
  // 1) MAIN PROBLEMS + LOADING
  const [problems, setProblems] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [loading, setLoading] = useState(false);

  // 2) FILTER STATES (Server-Side)
  const [filterCompany, setFilterCompany] = useState(null);
  const [filterDifficulty, setFilterDifficulty] = useState(null);
  const [filterDataStructure, setFilterDataStructure] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [dataStructures, setDataStructures] = useState([]);

  // 3) PAGINATION (Server-Side)
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // 4) QUICK TITLE SEARCH (Local)
  const [searchTerm, setSearchTerm] = useState('');

  // 5) MARK AS SOLVED / BOOKMARKS (Local)
  // problemStatus = { [problemId]: { solved: bool, bookmarked: bool } }
  const [problemStatus, setProblemStatus] = useState({});

  const [sortOrder, setSortOrder] = useState('asc');

  // ---------------------------------------------------------------------------
  // A) LOAD PREFERENCES FROM LOCALSTORAGE ON MOUNT (solved/bookmarked)
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const storedStatus = localStorage.getItem('problemStatus');
    if (storedStatus) {
      setProblemStatus(JSON.parse(storedStatus));
    }
  }, []);

  // Whenever problemStatus changes, store it
  useEffect(() => {
    localStorage.setItem('problemStatus', JSON.stringify(problemStatus));
  }, [problemStatus]);

  // ---------------------------------------------------------------------------
  // B) FETCH DISTINCT COMPANIES, DATA STRUCTURES
  // ---------------------------------------------------------------------------
  useEffect(() => {
    fetch(`${baseUrl}/api/companies`)
      .then(response => response.json())
      .then(data => setCompanies(data))
      .catch(err => console.error('Error fetching companies:', err));
  }, []);

  useEffect(() => {
    fetch(`${baseUrl}/api/data_structures`)
      .then(response => response.json())
      .then(data => setDataStructures(data))
      .catch(err => console.error('Error fetching data structures:', err));
  }, []);

  // ---------------------------------------------------------------------------
  // C) FETCH PROBLEMS (Server-Side Pagination + Filters)
  // ---------------------------------------------------------------------------
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    params.append('limit', limit);
    params.append('offset', (page - 1) * limit);

    if (filterCompany) {
      params.append('company', filterCompany);
    }
    if (filterDifficulty) {
      params.append('difficulty', filterDifficulty);
    }
    if (filterDataStructure) {
      params.append('data_structure', filterDataStructure);
    }
    if (searchTerm) {
      params.append('search', searchTerm);
    }

    params.append('sort_order', sortOrder);

    fetch(`${baseUrl}/api/problems?${params.toString()}`)
      .then(response => response.json())
      .then(data => {
        // data = { problems: [...], total: number }
        setProblems(data.problems || []);
        setSelectedProblem(null);

        // Recompute total pages from 'data.total'
        const totalCount = data.total || 0;
        const newTotalPages = Math.ceil(totalCount / limit);
        setTotalPages(newTotalPages);
      })
      .catch(err => console.error('Error fetching problems:', err))
      .finally(() => setLoading(false));
  }, [filterCompany, filterDifficulty, filterDataStructure, searchTerm, sortOrder, page]);

  // ---------------------------------------------------------------------------
  // E) HANDLERS
  // ---------------------------------------------------------------------------
  const selectProblem = (problem) => {
    setSelectedProblem(problem);
  };

  const toggleSolved = (problemId) => {
    setProblemStatus(prev => {
      const current = prev[problemId] || { solved: false, bookmarked: false };
      return {
        ...prev,
        [problemId]: {
          ...current,
          solved: !current.solved
        }
      };
    });
  };

  const toggleBookmarked = (problemId) => {
    setProblemStatus(prev => {
      const current = prev[problemId] || { solved: false, bookmarked: false };
      return {
        ...prev,
        [problemId]: {
          ...current,
          bookmarked: !current.bookmarked
        }
      };
    });
  };

  const getStatus = (problemId) => problemStatus[problemId] || { solved: false, bookmarked: false };

  const handleCompanyClick = (companyName) => {
    setFilterCompany(companyName);
    setFilterDifficulty(null);
    setFilterDataStructure(null);
    setPage(1);
  };

  const handleDataStructureClick = (ds) => {
    setFilterDataStructure(ds);
    setFilterCompany(null);
    setFilterDifficulty(null);
    setPage(1);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      {/* Filters Section */}
      <Paper elevation={2} sx={{ mb: 3, p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Filters
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <Autocomplete
              options={companies}
              value={filterCompany}
              onChange={(event, newValue) => {
                setFilterCompany(newValue);
                setPage(1);
              }}
              renderInput={(params) => (
                <TextField {...params} label="Filter by Company" variant="outlined" />
              )}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <Autocomplete
              options={difficulties}
              value={filterDifficulty}
              onChange={(event, newValue) => {
                setFilterDifficulty(newValue);
                setPage(1);
              }}
              renderInput={(params) => (
                <TextField {...params} label="Filter by Difficulty" variant="outlined" />
              )}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <Autocomplete
              options={dataStructures}
              value={filterDataStructure}
              onChange={(event, newValue) => {
                setFilterDataStructure(newValue);
                setPage(1);
              }}
              renderInput={(params) => (
                <TextField {...params} label="Filter by Data Structure" variant="outlined" />
              )}
            />
          </Grid>

          {/* Quick Title Search (local) */}
          <Grid item xs={12} md={3}>
            <TextField
              label="Search by Title"
              variant="outlined"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              fullWidth
            />
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={4}>
        {/* Problem List */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3}>
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                Problem List
                <IconButton
                  onClick={() => setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'))}
                  sx={{ ml: 1 }}
                >
                  {sortOrder === 'asc' ? <ArrowDownwardIcon /> : <ArrowUpwardIcon />}
                </IconButton>
              </Typography>

              {loading ? (
                <Box sx={{ textAlign: 'center', my: 4 }}>
                  <CircularProgress />
                </Box>
              ) : problems.length === 0 ? (
                <Typography variant="body1">No problems match your search/filters.</Typography>
              ) : (
                <List dense>
                  {problems.map(problem => {
                    const { solved, bookmarked } = getStatus(problem.id);
                    return (
                      <ListItem key={problem.id} disablePadding>
                        <ListItemButton
                          selected={selectedProblem?.id === problem.id}
                          onClick={() => selectProblem(problem)}
                        >
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Typography variant="subtitle1" sx={{ mr: 1 }}>
                                  {`${problem.id}. ${problem.title}`}
                                </Typography>
                                {problem.difficulty && (
                                  <Chip
                                    label={problem.difficulty}
                                    color={difficultyColorMap[problem.difficulty] || 'default'}
                                    size="small"
                                    sx={{ ml: 'auto' }}
                                  />
                                )}
                              </Box>
                            }
                          />
                        </ListItemButton>

                        {/* "Mark as Solved" icon */}
                        <IconButton
                          size="small"
                          onClick={() => toggleSolved(problem.id)}
                          sx={{ ml: 1 }}
                        >
                          {solved ? (
                            <CheckCircleIcon color="success" />
                          ) : (
                            <CheckCircleOutlineIcon />
                          )}
                        </IconButton>

                        {/* "Bookmark" icon */}
                        <IconButton
                          size="small"
                          onClick={() => toggleBookmarked(problem.id)}
                        >
                          {bookmarked ? (
                            <StarIcon color="warning" />
                          ) : (
                            <StarBorderIcon />
                          )}
                        </IconButton>
                      </ListItem>
                    );
                  })}
                </List>
              )}

              {!loading && problems.length > 0 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(event, value) => setPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Problem Details */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3}>
            <Box sx={{ p: 2 }}>
              {selectedProblem ? (
                <>
                  <Typography variant="h5" gutterBottom>
                    {selectedProblem.id}. {selectedProblem.title}
                  </Typography>
                  <Typography variant="subtitle1" gutterBottom>
                    {selectedProblem.problem}
                  </Typography>

                  {selectedProblem.company && (
                    <Typography variant="body1">
                      <strong>Company:</strong>{' '}
                      <Link
                        component="button"
                        variant="body2"
                        onClick={() => handleCompanyClick(selectedProblem.company)}
                      >
                        {selectedProblem.company}
                      </Link>
                    </Typography>
                  )}
                  {selectedProblem.source && (
                    <Typography variant="body1">
                      <strong>Source:</strong> {selectedProblem.source}
                    </Typography>
                  )}

                  {/* Data Structures as clickable Chips */}
                  {selectedProblem.data_structures?.length > 0 && (
                    <Box sx={{ mt: 1, mb: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        Data Structures:
                      </Typography>
                      {selectedProblem.data_structures.map((ds, idx) => (
                        <Chip
                          key={idx}
                          label={ds}
                          variant="outlined"
                          color="primary"
                          size="small"
                          sx={{ mr: 1, mt: 1, cursor: 'pointer' }}
                          onClick={() => handleDataStructureClick(ds)}
                        />
                      ))}
                    </Box>
                  )}

                  <Typography variant="body1">
                    <strong>Difficulty:</strong> {selectedProblem.difficulty}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Time Complexity:</strong> {selectedProblem.time_complexity}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Space Complexity:</strong> {selectedProblem.space_complexity}
                  </Typography>
                  {selectedProblem.passes_allowed !== null && (
                    <Typography variant="body1">
                      <strong>Passes Allowed:</strong> {selectedProblem.passes_allowed}
                    </Typography>
                  )}
                  <Typography variant="body1">
                    <strong>Edge Cases:</strong> {selectedProblem.edge_cases.join(', ')}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Input Types:</strong> {selectedProblem.input_types.join(', ')}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Output Types:</strong> {selectedProblem.output_types.join(', ')}
                  </Typography>

                  {/* Hints as Accordions */}
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6">Hints</Typography>
                    {selectedProblem.hints && selectedProblem.hints.length > 0 ? (
                      selectedProblem.hints.map((hint, index) => (
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

                  {/* Solution Accordion */}
                  <Box sx={{ mt: 3 }}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Show Solution</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box>
                          <Typography variant="h6">Solution</Typography>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            {selectedProblem.solution}
                          </Typography>
                          <Box>
                            <Typography variant="h6">Code Solution</Typography>
                            <SyntaxHighlighter
                              language="python"
                              style={solarizedlight}
                              customStyle={{ borderRadius: 4 }}
                            >
                              {selectedProblem.code_solution}
                            </SyntaxHighlighter>
                          </Box>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  </Box>
                </>
              ) : (
                <Typography variant="body1">
                  Select a problem to view its details.
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default ProblemsPage;
