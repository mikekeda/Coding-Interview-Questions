import React from 'react';
import {
  Grid,
  TextField,
  Autocomplete,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

/**
 * Props:
 * - facetData: object containing arrays of facet info, e.g.:
 *   {
 *     company: [{ value: "Google", count: 10 }, ...],
 *     difficulty: [{ value: "Easy", count: 5 }, ...],
 *     data_structures: [{ value: "Array", count: 8 }, ...],
 *     algorithms: [{ value: "Two Pointers", count: 7 }, ...],
 *     tags: [{ value: "In-Place", count: 4 }, ...]
 *   }
 *
 * - filterCompany, setFilterCompany (string)
 * - filterDifficulty, setFilterDifficulty (string)
 * - filterDataStructure, setFilterDataStructure (string)
 * - filterAlgorithm, setFilterAlgorithm (string)
 * - filterTag, setFilterTag (string)
 * - searchTerm, setSearchTerm (string)
 */
function SearchFilters({
  facetData = {},

  filterCompany,
  setFilterCompany,
  filterDifficulty,
  setFilterDifficulty,
  filterDataStructure,
  setFilterDataStructure,
  filterAlgorithm,
  setFilterAlgorithm,
  filterTag,
  setFilterTag,
  searchTerm,
  setSearchTerm
}) {
  // Convert facet data into Autocomplete options
  const companyOptions = (facetData.company || []).map((item) => ({
    label: `${item.value} (${item.count})`,
    value: item.value,
  }));

  const difficultyOptions = (facetData.difficulty || []).map((item) => ({
    label: `${item.value} (${item.count})`,
    value: item.value,
  }));

  const dataStructureOptions = (facetData.data_structures || []).map((item) => ({
    label: `${item.value} (${item.count})`,
    value: item.value,
  }));

  // Advanced filters
  const algorithmOptions = (facetData.algorithms || []).map((item) => ({
    label: `${item.value} (${item.count})`,
    value: item.value,
  }));

  const tagOptions = (facetData.tags || []).map((item) => ({
    label: `${item.value} (${item.count})`,
    value: item.value,
  }));

  return (
    <>
      {/* Basic Filters (always visible) */}
      <Grid container spacing={2} alignItems="center">
        {/* Filter by Company */}
        <Grid item xs={12} md={4}>
          <Autocomplete
            options={companyOptions}
            getOptionLabel={(option) => option.label}
            value={
              filterCompany
                ? companyOptions.find((opt) => opt.value === filterCompany) || null
                : null
            }
            onChange={(e, newVal) => {
              setFilterCompany(newVal ? newVal.value : null);
            }}
            renderInput={(params) => (
              <TextField {...params} label="Filter by Company" variant="outlined" />
            )}
          />
        </Grid>

        {/* Filter by Difficulty */}
        <Grid item xs={12} md={4}>
          <Autocomplete
            options={difficultyOptions}
            getOptionLabel={(option) => option.label}
            value={
              filterDifficulty
                ? difficultyOptions.find((opt) => opt.value === filterDifficulty) || null
                : null
            }
            onChange={(e, newVal) => {
              setFilterDifficulty(newVal ? newVal.value : null);
            }}
            renderInput={(params) => (
              <TextField {...params} label="Filter by Difficulty" variant="outlined" />
            )}
          />
        </Grid>

        {/* Title Search */}
        <Grid item xs={12} md={4}>
          <TextField
            label="Search by Title"
            variant="outlined"
            value={searchTerm || ''}
            onChange={(e) => setSearchTerm(e.target.value)}
            fullWidth
          />
        </Grid>
      </Grid>

      {/* Advanced Filters (hidden by default in an Accordion) */}
      <Accordion sx={{ mt: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Advanced Filters</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2} alignItems="center">
            {/* Filter by Data Structure */}
            <Grid item xs={12} md={4}>
              <Autocomplete
                options={dataStructureOptions}
                getOptionLabel={(option) => option.label}
                value={
                  filterDataStructure
                    ? dataStructureOptions.find((opt) => opt.value === filterDataStructure) || null
                    : null
                }
                onChange={(e, newVal) => {
                  setFilterDataStructure(newVal ? newVal.value : null);
                }}
                renderInput={(params) => (
                  <TextField {...params} label="Filter by Data Structure" variant="outlined" />
                )}
              />
            </Grid>

            {/* Filter by Algorithm (single-select) */}
            <Grid item xs={12} md={4}>
              <Autocomplete
                options={algorithmOptions}
                getOptionLabel={(option) => option.label}
                value={
                  filterAlgorithm
                    ? algorithmOptions.find((opt) => opt.value === filterAlgorithm) || null
                    : null
                }
                onChange={(e, newVal) => {
                  setFilterAlgorithm(newVal ? newVal.value : null);
                }}
                renderInput={(params) => (
                  <TextField {...params} label="Filter by Algorithm" variant="outlined" />
                )}
              />
            </Grid>

            {/* Filter by Tag (single-select) */}
            <Grid item xs={12} md={4}>
              <Autocomplete
                options={tagOptions}
                getOptionLabel={(option) => option.label}
                value={
                 filterTag
                   ? tagOptions.find((opt) => opt.value === filterTag) || null
                   : null
                }
                onChange={(e, newVal) => {
                  // newVal is an array of selected options
                  setFilterTag(newVal ? newVal.value : null);
                }}
                renderInput={(params) => (
                  <TextField {...params} label="Filter by Tag" variant="outlined" />
                )}
              />
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    </>
  );
}

export default SearchFilters;
