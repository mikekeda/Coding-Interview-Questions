import React from 'react';
import { Grid, TextField, Autocomplete } from '@mui/material';

function SearchFilters({
  // Facet data, e.g. { company: [...], difficulty: [...], data_structures: [...] }
  facetData,

  // Existing filter states + setters
  filterCompany,
  setFilterCompany,
  filterDifficulty,
  setFilterDifficulty,
  filterDataStructure,
  setFilterDataStructure,
  searchTerm,
  setSearchTerm
}) {
  // Convert facet data into Autocomplete options
  // Example: each item is { value: "Google", count: 5 }
  // We'll display "Google (5)" as the label
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

  return (
    <Grid container spacing={2} alignItems="center">
      {/* Filter by Company */}
      <Grid item xs={12} md={3}>
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
      <Grid item xs={12} md={3}>
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

      {/* Filter by Data Structure */}
      <Grid item xs={12} md={3}>
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

      {/* Title Search */}
      <Grid item xs={12} md={3}>
        <TextField
          label="Search by Title"
          variant="outlined"
          value={searchTerm || ''}
          onChange={(e) => setSearchTerm(e.target.value)}
          fullWidth
        />
      </Grid>
    </Grid>
  );
}

export default SearchFilters;
