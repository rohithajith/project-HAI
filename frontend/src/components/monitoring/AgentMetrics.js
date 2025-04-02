import React, { useState } from 'react';
import {
  Card,
  Grid,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Collapse,
  Chip,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  KeyboardArrowDown as KeyboardArrowDownIcon,
  KeyboardArrowUp as KeyboardArrowUpIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

const AgentRow = ({ agent, metrics }) => {
  const [open, setOpen] = useState(false);

  const getStatusColor = (metrics) => {
    const errorRate = (metrics.failed_requests / metrics.total_requests) * 100;
    if (errorRate > 10) return 'error';
    if (errorRate > 5) return 'warning';
    return 'success';
  };

  const getStatusIcon = (color) => {
    switch (color) {
      case 'success':
        return <CheckCircleIcon fontSize="small" />;
      case 'warning':
        return <WarningIcon fontSize="small" />;
      case 'error':
        return <ErrorIcon fontSize="small" />;
      default:
        return null;
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const calculateSuccessRate = (metrics) => {
    if (metrics.total_requests === 0) return 0;
    return (metrics.successful_requests / metrics.total_requests) * 100;
  };

  const statusColor = getStatusColor(metrics);

  return (
    <>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {agent}
            <Chip
              icon={getStatusIcon(statusColor)}
              label={statusColor.toUpperCase()}
              color={statusColor}
              size="small"
              sx={{ ml: 1 }}
            />
          </Box>
        </TableCell>
        <TableCell align="right">{metrics.total_requests}</TableCell>
        <TableCell align="right">
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress
                variant="determinate"
                value={calculateSuccessRate(metrics)}
                color={statusColor}
              />
            </Box>
            <Box sx={{ minWidth: 35 }}>
              <Typography variant="body2" color="text.secondary">
                {calculateSuccessRate(metrics).toFixed(1)}%
              </Typography>
            </Box>
          </Box>
        </TableCell>
        <TableCell align="right">
          {metrics.average_response_time.toFixed(2)}ms
        </TableCell>
        <TableCell align="right">{formatTime(metrics.last_active)}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Details
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Request Statistics
                    </Typography>
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell>Total Requests</TableCell>
                          <TableCell align="right">{metrics.total_requests}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Successful Requests</TableCell>
                          <TableCell align="right">{metrics.successful_requests}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Failed Requests</TableCell>
                          <TableCell align="right">{metrics.failed_requests}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Success Rate</TableCell>
                          <TableCell align="right">
                            {calculateSuccessRate(metrics).toFixed(2)}%
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Performance Metrics
                    </Typography>
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell>Average Response Time</TableCell>
                          <TableCell align="right">
                            {metrics.average_response_time.toFixed(2)}ms
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Last Active</TableCell>
                          <TableCell align="right">
                            {formatTime(metrics.last_active)}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Last Error</TableCell>
                          <TableCell align="right">
                            {metrics.last_error || 'None'}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

const AgentMetrics = ({ systemHealth }) => {
  if (!systemHealth || !systemHealth.agents) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <Typography>No agent metrics available</Typography>
      </Box>
    );
  }

  return (
    <Card>
      <Box sx={{ p: 2 }}>
        <Typography variant="h5" gutterBottom>
          Agent Performance Metrics
        </Typography>
      </Box>
      <TableContainer component={Paper}>
        <Table aria-label="agent metrics">
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell>Agent</TableCell>
              <TableCell align="right">Total Requests</TableCell>
              <TableCell align="right">Success Rate</TableCell>
              <TableCell align="right">Avg Response Time</TableCell>
              <TableCell align="right">Last Active</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(systemHealth.agents).map(([agent, metrics]) => (
              <AgentRow key={agent} agent={agent} metrics={metrics} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Card>
  );
};

export default AgentMetrics;