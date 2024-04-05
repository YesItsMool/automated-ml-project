// src/MyGridComponent.js

import React from 'react';
import Grid from '@mui/material/Grid';

function MyGridComponent() {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        {/* Content for the first half */}
      </Grid>
      <Grid item xs={12} sm={6}>
        {/* Content for the second half */}
      </Grid>
    </Grid>
  );
}

export default MyGridComponent;
