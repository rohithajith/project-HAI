import React, { useState, useEffect } from 'react';
import { Card, Grid, Typography, Box } from '@mui/material';
import { Line } from 'react-chartjs-2';
import SystemHealth from './SystemHealth';
import AgentMetrics from './AgentMetrics';
import AlertList from './AlertList';
import MetricChart from './MetricChart';

const Dashboard = () => {
  const [systemHealth, setSystemHealth] = useState(null);
  const [metrics, setMetrics] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');

  useEffect(() => {
    // Initial data load
    fetchData();
    // Set up polling
    const interval = setInterval(fetchData, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, [selectedTimeRange]);

  const fetchData = async () => {
    try {
      // Fetch system health
      const healthResponse = await fetch('/api/monitoring/health');
      const healthData = await healthResponse.json();
      setSystemHealth(healthData);

      // Fetch metrics
      const metricsResponse = await fetch('/api/monitoring/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metrics: ['cpu_usage', 'memory_usage', 'requests_per_minute', 'error_rate'],
          start_time: getStartTime(),
          end_time: new Date().toISOString(),
          aggregation: 'avg'
        })
      });
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData.metrics);

      // Fetch alerts
      const alertsResponse = await fetch('/api/monitoring/alerts?acknowledged=false');
      const alertsData = await alertsResponse.json();
      setAlerts(alertsData.alerts);
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
    }
  };

  const getStartTime = () => {
    const now = new Date();
    switch (selectedTimeRange) {
      case '1h':
        return new Date(now - 3600000).toISOString();
      case '6h':
        return new Date(now - 21600000).toISOString();
      case '1d':
        return new Date(now - 86400000).toISOString();
      default:
        return new Date(now - 3600000).toISOString();
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Monitoring Dashboard
      </Typography>

      {/* System Health Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <SystemHealth data={systemHealth} />
        </Grid>
      </Grid>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              CPU Usage
            </Typography>
            <MetricChart
              data={metrics.cpu_usage}
              timeRange={selectedTimeRange}
              color="#2196f3"
              unit="%"
            />
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Memory Usage
            </Typography>
            <MetricChart
              data={metrics.memory_usage}
              timeRange={selectedTimeRange}
              color="#4caf50"
              unit="%"
            />
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Requests per Minute
            </Typography>
            <MetricChart
              data={metrics.requests_per_minute}
              timeRange={selectedTimeRange}
              color="#ff9800"
              unit="req/min"
            />
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Error Rate
            </Typography>
            <MetricChart
              data={metrics.error_rate}
              timeRange={selectedTimeRange}
              color="#f44336"
              unit="%"
            />
          </Card>
        </Grid>
      </Grid>

      {/* Agent Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <AgentMetrics systemHealth={systemHealth} />
        </Grid>
      </Grid>

      {/* Active Alerts */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <AlertList alerts={alerts} onUpdate={fetchData} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;