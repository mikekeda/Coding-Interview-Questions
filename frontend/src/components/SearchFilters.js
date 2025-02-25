import React from 'react';
import { Grid, TextField, Autocomplete } from '@mui/material';

function SearchFilters({
  companies,
  difficulties,
  dataStructures,

  filterCompany,
  filterDifficulty,
  filterDataStructure,
  searchTerm,

  setFilterCompany,
  setFilterDifficulty,
  setFilterDataStructure,
  setSearchTerm
}) {
  return (
    <Grid container spacing={2} alignItems="center">
      <Grid item xs={12} md={3}>
        <Autocomplete
          options={companies}
          value={filterCompany}
          onChange={(e, newVal) => setFilterCompany(newVal)}
          renderInput={(params) => (
            <TextField {...params} label="Filter by Company" variant="outlined" />
          )}
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <Autocomplete
          options={difficulties}
          value={filterDifficulty}
          onChange={(e, newVal) => setFilterDifficulty(newVal)}
          renderInput={(params) => (
            <TextField {...params} label="Filter by Difficulty" variant="outlined" />
          )}
        />
      </Grid>
      <Grid item xs={12} md={3}>
        <Autocomplete
          options={dataStructures}
          value={filterDataStructure}
          onChange={(e, newVal) => setFilterDataStructure(newVal)}
          renderInput={(params) => (
            <TextField {...params} label="Filter by Data Structure" variant="outlined" />
          )}
        />
      </Grid>
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
  );
}

export default SearchFilters;
