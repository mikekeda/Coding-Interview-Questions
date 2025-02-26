import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Box,
  CircularProgress,
  Typography,
  IconButton,
  Pagination
} from '@mui/material';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import { Helmet } from 'react-helmet';

// Reusable components
import SearchFilters from '../components/SearchFilters';
import ProblemList from '../components/ProblemList';
import ProblemDetail from '../components/ProblemDetail';

const protocol = window.location.protocol;
const hostname = window.location.hostname;
const baseUrl = hostname === 'localhost'
  ? 'http://localhost:8000'
  : `${protocol}//${hostname}`;

function ProblemsPage() {
  // Problem data & states
  const [problems, setProblems] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [loading, setLoading] = useState(false);

  // Filter states
  const [filterCompany, setFilterCompany] = useState(null);
  const [filterDifficulty, setFilterDifficulty] = useState(null);
  const [filterDataStructure, setFilterDataStructure] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Facet data
  const [facetData, setFacetData] = useState({
    company: [],
    difficulty: [],
    data_structures: []
  });

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Sort
  const [sortOrder, setSortOrder] = useState('asc');

  // local storage for solved/bookmark
  const [problemStatus, setProblemStatus] = useState({});

  // Router
  const { problemId } = useParams();
  const navigate = useNavigate();

  // Load local storage
  useEffect(() => {
    const storedStatus = localStorage.getItem('problemStatus');
    if (storedStatus) {
      setProblemStatus(JSON.parse(storedStatus));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('problemStatus', JSON.stringify(problemStatus));
  }, [problemStatus]);

  // 1) Fetch problems
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    params.append('limit', 10);
    params.append('offset', (page - 1) * 10);

    if (filterCompany) params.append('company', filterCompany);
    if (filterDifficulty) params.append('difficulty', filterDifficulty);
    if (filterDataStructure) params.append('data_structure', filterDataStructure);
    if (searchTerm) params.append('search', searchTerm);

    params.append('sort_order', sortOrder);

    fetch(`${baseUrl}/api/problems?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setProblems(data.problems || []);
        const totalCount = data.total || 0;
        setTotalPages(Math.ceil(totalCount / 10));
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [
    filterCompany,
    filterDifficulty,
    filterDataStructure,
    searchTerm,
    sortOrder,
    page
  ]);

  // 2) Fetch facet counts
  useEffect(() => {
    const params = new URLSearchParams();
    if (filterCompany) params.append('company', filterCompany);
    if (filterDifficulty) params.append('difficulty', filterDifficulty);
    if (filterDataStructure) params.append('data_structure', filterDataStructure);
    if (searchTerm) params.append('search', searchTerm);

    fetch(`${baseUrl}/api/facets?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setFacetData(data);
      })
      .catch(err => console.error(err));
  }, [
    filterCompany,
    filterDifficulty,
    filterDataStructure,
    searchTerm
  ]);

  // 3) Sync URL param => selectedProblem
  useEffect(() => {
    if (!problemId) {
      setSelectedProblem(null);
      return;
    }
    const found = problems.find((p) => p.id === Number(problemId));
    if (found) {
      setSelectedProblem(found);
    } else {
      // Single fetch if not in the current list
      fetch(`${baseUrl}/api/problems/${problemId}`)
        .then(res => {
          if (!res.ok) throw new Error('Problem not found');
          return res.json();
        })
        .then((problem) => {
          setSelectedProblem(problem);
        })
        .catch(err => {
          console.error(err);
          setSelectedProblem(null);
        });
    }
  }, [problemId, problems]);

  // Handlers
  function selectProblem(problem) {
    setSelectedProblem(problem);
    navigate(`/problems/${problem.id}`);
  }

  function toggleSolved(problemId) {
    setProblemStatus(prev => {
      const current = prev[problemId] || { solved: false, bookmarked: false };
      return {
        ...prev,
        [problemId]: { ...current, solved: !current.solved }
      };
    });
  }

  function toggleBookmarked(problemId) {
    setProblemStatus(prev => {
      const current = prev[problemId] || { solved: false, bookmarked: false };
      return {
        ...prev,
        [problemId]: { ...current, bookmarked: !current.bookmarked }
      };
    });
  }

  function getStatus(problemId) {
    return problemStatus[problemId] || { solved: false, bookmarked: false };
  }

  function handleCompanyClick(companyName) {
    setFilterCompany(companyName);
    setFilterDifficulty(null);
    setFilterDataStructure(null);
    setPage(1);
  }

  function handleDataStructureClick(ds) {
    setFilterDataStructure(ds);
    setFilterCompany(null);
    setFilterDifficulty(null);
    setPage(1);
  }

  function handleDifficultyClick(difficulty) {
    setFilterDataStructure(null);
    setFilterCompany(null);
    setFilterDifficulty(difficulty);
    setPage(1);
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Helmet>
        <title>Coding Interview Prep</title>
        <meta
          name="description"
          content="Sharpen your coding interview skills with curated problems, hints, and solutions. Filter by company, difficulty, and data structures."
        />
      </Helmet>

      {/* Reusable filter UI with facet data */}
      <Paper elevation={2} sx={{ mb: 3, p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Filters
        </Typography>
        <SearchFilters
          facetData={facetData}
          filterCompany={filterCompany}
          setFilterCompany={(val) => { setFilterCompany(val); setPage(1); }}
          filterDifficulty={filterDifficulty}
          setFilterDifficulty={(val) => { setFilterDifficulty(val); setPage(1); }}
          filterDataStructure={filterDataStructure}
          setFilterDataStructure={(val) => { setFilterDataStructure(val); setPage(1); }}
          searchTerm={searchTerm}
          setSearchTerm={(val) => { setSearchTerm(val); setPage(1); }}
        />
      </Paper>

      <Grid container spacing={4}>
        {/* Problem List (left) */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3}>
            <Box sx={{ p: 2 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ display: 'flex', alignItems: 'center' }}
              >
                Problem List
                <IconButton
                  onClick={() => setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'))}
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
                <Typography variant="body1">
                  No problems match your filters/search.
                </Typography>
              ) : (
                <ProblemList
                  problems={problems}
                  selectedProblemId={selectedProblem?.id}
                  onSelectProblem={selectProblem}
                  getStatus={getStatus}
                  toggleSolved={toggleSolved}
                  toggleBookmarked={toggleBookmarked}
                />
              )}

              {!loading && problems.length > 0 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(e, value) => setPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Problem Detail (right) */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3}>
            <Box sx={{ p: 2 }}>
              <ProblemDetail
                problem={selectedProblem}
                handleCompanyClick={handleCompanyClick}
                handleDataStructureClick={handleDataStructureClick}
                handleDifficultyClick={handleDifficultyClick}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default ProblemsPage;
