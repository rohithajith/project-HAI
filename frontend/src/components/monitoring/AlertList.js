import React, { useState } from 'react';
import {
  Card,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Collapse,
  Alert,
  Tooltip
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Done as DoneIcon
} from '@mui/icons-material';

const AlertList = ({ alerts, onUpdate }) => {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [acknowledgeDialogOpen, setAcknowledgeDialogOpen] = useState(false);
  const [acknowledgementNotes, setAcknowledgementNotes] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [expandedAlerts, setExpandedAlerts] = useState(new Set());

  const handleAcknowledge = async (alert) => {
    try {
      const response = await fetch(`/api/monitoring/alerts/${alert.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          acknowledged: true,
          notes: acknowledgementNotes
        })
      });

      if (!response.ok) {
        throw new Error('Failed to acknowledge alert');
      }

      setAcknowledgeDialogOpen(false);
      setSelectedAlert(null);
      setAcknowledgementNotes('');
      onUpdate();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const toggleAlertExpansion = (alertId) => {
    const newExpanded = new Set(expandedAlerts);
    if (newExpanded.has(alertId)) {
      newExpanded.delete(alertId);
    } else {
      newExpanded.add(alertId);
    }
    setExpandedAlerts(newExpanded);
  };

  const getSeverityIcon = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const filteredAlerts = alerts.filter(alert => 
    filterSeverity === 'all' || alert.severity.toLowerCase() === filterSeverity.toLowerCase()
  );

  return (
    <Card>
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" sx={{ flexGrow: 1 }}>
            Active Alerts
          </Typography>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Severity</InputLabel>
            <Select
              value={filterSeverity}
              label="Severity"
              onChange={(e) => setFilterSeverity(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="info">Info</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {filteredAlerts.length === 0 ? (
          <Alert severity="success" icon={<CheckCircleIcon />}>
            No active alerts
          </Alert>
        ) : (
          <List>
            {filteredAlerts.map((alert) => (
              <React.Fragment key={alert.id}>
                <ListItem
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    bgcolor: 'background.paper'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Tooltip title={alert.severity}>
                      <Box sx={{ mr: 2 }}>
                        {getSeverityIcon(alert.severity)}
                      </Box>
                    </Tooltip>
                    <ListItemText
                      primary={
                        <Typography variant="subtitle1">
                          {alert.message}
                        </Typography>
                      }
                      secondary={
                        <Typography variant="body2" color="text.secondary">
                          {formatTimestamp(alert.timestamp)}
                        </Typography>
                      }
                    />
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Chip
                        label={alert.metric_name}
                        size="small"
                        color={getSeverityColor(alert.severity)}
                        sx={{ mr: 1 }}
                      />
                      <IconButton
                        size="small"
                        onClick={() => toggleAlertExpansion(alert.id)}
                      >
                        {expandedAlerts.has(alert.id) ? 
                          <ExpandLessIcon /> : 
                          <ExpandMoreIcon />
                        }
                      </IconButton>
                      <Button
                        startIcon={<DoneIcon />}
                        size="small"
                        onClick={() => {
                          setSelectedAlert(alert);
                          setAcknowledgeDialogOpen(true);
                        }}
                        sx={{ ml: 1 }}
                      >
                        Acknowledge
                      </Button>
                    </Box>
                  </Box>
                </ListItem>
                <Collapse in={expandedAlerts.has(alert.id)}>
                  <Box sx={{ pl: 6, pr: 2, pb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Alert Details
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Metric:
                      </Typography>
                      <Typography variant="body2">
                        {alert.metric_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Current Value:
                      </Typography>
                      <Typography variant="body2">
                        {alert.current_value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Threshold:
                      </Typography>
                      <Typography variant="body2">
                        {alert.threshold_value}
                      </Typography>
                    </Box>
                  </Box>
                </Collapse>
              </React.Fragment>
            ))}
          </List>
        )}
      </Box>

      <Dialog
        open={acknowledgeDialogOpen}
        onClose={() => setAcknowledgeDialogOpen(false)}
      >
        <DialogTitle>Acknowledge Alert</DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            {selectedAlert?.message}
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="Acknowledgement Notes"
            fullWidth
            multiline
            rows={4}
            value={acknowledgementNotes}
            onChange={(e) => setAcknowledgementNotes(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAcknowledgeDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={() => handleAcknowledge(selectedAlert)}
            variant="contained"
          >
            Acknowledge
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default AlertList;