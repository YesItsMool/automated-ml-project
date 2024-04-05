// src/components/Navigation.js

import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';

function Navigation() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6">
          Machine Learning Dashboard
        </Typography>
      </Toolbar>
    </AppBar>
  );
}

export default Navigation;
