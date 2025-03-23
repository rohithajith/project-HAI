import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Collapse,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Tooltip,
  Badge
} from '@mui/material';
import {
  BugReport as BugIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  Timer as TimerIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Styled components
const DebugContainer = styled(Paper)(({ theme }) => ({
  position: 'absolute',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
  width: 350,
  maxWidth: 'calc(100% - 32px)',
  zIndex: 1000,
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  opacity: 0.95,
  '&:hover': {
    opacity: 1,
    boxShadow: theme.shadows[8]
  }
}));

const DebugHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1, 2),
  backgroundColor: theme.palette.grey[900],
  color: theme.palette.common.white,
  cursor: 'pointer'
}));

const DebugContent = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  maxHeight: 400,
  overflowY: 'auto'
}));

const StatusChip = styled(Chip)(({ theme, status }) => {
  let color;
  switch (status) {
    case 'success':
      color = theme.palette.success.main;
      break;
    case 'error':
      color = theme.palette.error.main;
      break;
    case 'pending':
      color = theme.palette.warning.main;
      break;
    default:
      color = theme.palette.grey[500];
  }
  
  return {
    backgroundColor: color,
    color: theme.palette.getContrastText(color),
    fontWeight: 'bold',
    fontSize: '0.7rem'
  };
});

/**
 * DebugPanel component for displaying debugging information for the chatbot
 * 
 * @param {Object} props - Component props
 * @param {Object} props.debugInfo - Debug information object
 * @param {boolean} props.hasErrors - Whether there are any errors
 * @param {function} props.onClear - Function to clear debug information
 */
const DebugPanel = ({ debugInfo, hasErrors = false, onClear }) => {
  const [expanded, setExpanded] = useState(false);
  
  // Toggle panel expansion
  const toggleExpand = () => {
    setExpanded(!expanded);
  };
  
  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3
    });
  };
  
  // Calculate time difference in ms
  const getTimeDiff = (start, end) => {
    if (!start || !end) return 'N/A';
    return `${(new Date(end) - new Date(start)).toFixed(0)}ms`;
  };

  return (
    <DebugContainer elevation={4}>
      <DebugHeader onClick={toggleExpand}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Badge 
            color="error" 
            variant="dot" 
            invisible={!hasErrors}
            sx={{ mr: 1 }}
          >
            <BugIcon fontSize="small" />
          </Badge>
          <Typography variant="subtitle2">
            Debug Panel
          </Typography>
        </Box>
        
        <Box>
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </Box>
      </DebugHeader>
      
      <Collapse in={expanded}>
        <DebugContent>
          {debugInfo.apiCalls && debugInfo.apiCalls.length > 0 ? (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="subtitle2">API Calls</Typography>
                <Tooltip title="Clear logs">
                  <IconButton 
                    size="small" 
                    onClick={onClear}
                    sx={{ p: 0.5 }}
                  >
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <List dense disablePadding>
                {debugInfo.apiCalls.map((call, index) => (
                  <React.Fragment key={index}>
                    <ListItem 
                      alignItems="flex-start" 
                      sx={{ 
                        px: 1, 
                        py: 0.5,
                        backgroundColor: index % 2 === 0 ? 'rgba(0,0,0,0.03)' : 'transparent'
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body2" component="span">
                              {call.type || 'API Call'}
                            </Typography>
                            <StatusChip
                              label={call.status}
                              status={
                                call.status === 'success' ? 'success' :
                                call.status === 'error' ? 'error' :
                                call.status === 'pending' ? 'pending' : 'default'
                              }
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                              <TimerIcon fontSize="inherit" sx={{ mr: 0.5, opacity: 0.7 }} />
                              <Typography variant="caption" component="span">
                                Start: {formatTime(call.startTime)}
                              </Typography>
                            </Box>
                            
                            {call.endTime && (
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                                <TimerIcon fontSize="inherit" sx={{ mr: 0.5, opacity: 0.7 }} />
                                <Typography variant="caption" component="span">
                                  Duration: {getTimeDiff(call.startTime, call.endTime)}
                                </Typography>
                              </Box>
                            )}
                            
                            {call.error && (
                              <Box sx={{ 
                                p: 1, 
                                mt: 1, 
                                backgroundColor: 'error.light',
                                borderRadius: 1
                              }}>
                                <Typography variant="caption" color="error.dark">
                                  {call.error}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < debugInfo.apiCalls.length - 1 && <Divider component="li" />}
                  </React.Fragment>
                ))}
              </List>
            </>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
              No API calls recorded yet. Start a conversation to see debug information.
            </Typography>
          )}
          
          {debugInfo.conversationState && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Conversation State
              </Typography>
              
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 1.5, 
                  backgroundColor: 'background.default',
                  maxHeight: 150,
                  overflow: 'auto'
                }}
              >
                <Typography variant="caption" component="pre" sx={{ m: 0 }}>
                  {JSON.stringify(debugInfo.conversationState, null, 2)}
                </Typography>
              </Paper>
            </>
          )}
        </DebugContent>
      </Collapse>
    </DebugContainer>
  );
};

export default DebugPanel;