import React from 'react';
import { 
  Card, 
  Grid, 
  Typography, 
  Box, 
  CircularProgress,
  Chip
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  AccessTime as AccessTimeIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material';

const SystemHealth = ({ data }) => {
  if (!data) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return <CheckCircleIcon />;
      case 'degraded':
        return <WarningIcon />;
      case 'critical':
        return <ErrorIcon />;
      default:
        return null;
    }
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    
    return parts.join(' ');
  };

  const MetricCard = ({ title, value, icon, unit, color }) => (
    <Card sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        {icon}
        <Typography variant="h6" sx={{ ml: 1 }}>
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" color={color || 'textPrimary'}>
        {value}
        {unit && <Typography component="span" variant="body1" sx={{ ml: 1 }}>{unit}</Typography>}
      </Typography>
    </Card>
  );

  return (
    <Box>
      <Grid container spacing={3}>
        {/* System Status */}
        <Grid item xs={12}>
          <Card sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography variant="h5" sx={{ flexGrow: 1 }}>
                System Health Status
              </Typography>
              <Chip
                icon={getStatusIcon(data.status)}
                label={data.status}
                color={getStatusColor(data.status)}
                sx={{ ml: 2 }}
              />
            </Box>
            
            <Grid container spacing={3}>
              {/* Uptime */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Uptime"
                  value={formatUptime(data.metrics.uptime)}
                  icon={<AccessTimeIcon color="primary" />}
                />
              </Grid>

              {/* CPU Usage */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="CPU Usage"
                  value={data.metrics.cpu_usage.toFixed(1)}
                  unit="%"
                  icon={<SpeedIcon color="primary" />}
                  color={data.metrics.cpu_usage > 80 ? 'error' : 'textPrimary'}
                />
              </Grid>

              {/* Memory Usage */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Memory Usage"
                  value={data.metrics.memory_usage.toFixed(1)}
                  unit="%"
                  icon={<MemoryIcon color="primary" />}
                  color={data.metrics.memory_usage > 80 ? 'error' : 'textPrimary'}
                />
              </Grid>

              {/* Error Rate */}
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Error Rate"
                  value={data.metrics.error_rate.toFixed(2)}
                  unit="%"
                  icon={<BugReportIcon color="primary" />}
                  color={data.metrics.error_rate > 5 ? 'error' : 'textPrimary'}
                />
              </Grid>
            </Grid>
          </Card>
        </Grid>

        {/* Active Agents */}
        <Grid item xs={12}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Active Agents
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {data.agents.map((agent) => (
                <Chip
                  key={agent}
                  label={agent}
                  color="primary"
                  variant="outlined"
                  sx={{ m: 0.5 }}
                />
              ))}
            </Box>
          </Card>
        </Grid>

        {/* System Notifications */}
        {data.notifications && data.notifications.length > 0 && (
          <Grid item xs={12}>
            <Card sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                System Notifications
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {data.notifications.map((notification, index) => (
                  <Chip
                    key={index}
                    label={notification.message}
                    color={notification.severity === 'error' ? 'error' : 'warning'}
                    sx={{ maxWidth: '100%', height: 'auto', '& .MuiChip-label': { whiteSpace: 'normal' } }}
                  />
                ))}
              </Box>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default SystemHealth;