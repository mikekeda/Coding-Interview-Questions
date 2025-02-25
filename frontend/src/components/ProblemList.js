import React from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  IconButton,
  Box,
  Typography,
  Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';

const difficultyColorMap = {
  Easy: 'success',
  Medium: 'warning',
  Hard: 'error'
};

function ProblemList({
  problems,
  selectedProblemId,
  onSelectProblem,
  getStatus,
  toggleSolved,
  toggleBookmarked
}) {
  return (
    <List dense>
      {problems.map(problem => {
        const { solved, bookmarked } = getStatus(problem.id);
        return (
          <ListItem key={problem.id} disablePadding>
            <ListItemButton
              selected={selectedProblemId === problem.id}
              onClick={() => onSelectProblem(problem)}
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

            {/* Solved icon */}
            <IconButton size="small" onClick={() => toggleSolved(problem.id)}>
              {solved ? <CheckCircleIcon color="success" /> : <CheckCircleOutlineIcon />}
            </IconButton>

            {/* Bookmark icon */}
            <IconButton size="small" onClick={() => toggleBookmarked(problem.id)}>
              {bookmarked ? <StarIcon color="warning" /> : <StarBorderIcon />}
            </IconButton>
          </ListItem>
        );
      })}
    </List>
  );
}

export default ProblemList;
