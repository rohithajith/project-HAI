import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormGroup,
  FormControlLabel,
  Switch,
  Button,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Divider
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Component for managing user consent preferences for data collection
 */
const ConsentManager = ({ onClose }) => {
  const { currentUser } = useAuth();
  const [consentPreferences, setConsentPreferences] = useState({
    serviceImprovement: false,
    modelTraining: false,
    analytics: false,
    marketing: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Fetch current consent preferences
  useEffect(() => {
    const fetchConsentPreferences = async () => {
      try {
        setLoading(true);
        setError('');
        
        const response = await axios.get(`${API_URL}/chatbot/consent`);
        
        if (response.data.success) {
          setConsentPreferences({
            serviceImprovement: response.data.consent?.service_improvement || false,
            modelTraining: response.data.consent?.model_training || false,
            analytics: response.data.consent?.analytics || false,
            marketing: response.data.consent?.marketing || false
          });
        }
      } catch (error) {
        console.error('Error fetching consent preferences:', error);
        setError('Failed to load your consent preferences. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchConsentPreferences();
    } else {
      setLoading(false);
    }
  }, [currentUser]);

  // Handle consent preference changes
  const handleConsentChange = (event) => {
    setConsentPreferences({
      ...consentPreferences,
      [event.target.name]: event.target.checked
    });
  };

  // Save consent preferences
  const handleSaveConsent = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      const response = await axios.post(`${API_URL}/chatbot/consent`, consentPreferences);
      
      if (response.data.success) {
        setSuccess('Your consent preferences have been saved successfully.');
      }
    } catch (error) {
      console.error('Error saving consent preferences:', error);
      setError('Failed to save your consent preferences. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // Delete conversation history
  const handleDeleteHistory = async () => {
    try {
      setDeleteLoading(true);
      setError('');
      
      const response = await axios.delete(`${API_URL}/chatbot/history`);
      
      if (response.data.success) {
        setSuccess('Your conversation history has been deleted successfully.');
        setShowDeleteDialog(false);
      }
    } catch (error) {
      console.error('Error deleting conversation history:', error);
      setError('Failed to delete your conversation history. Please try again.');
    } finally {
      setDeleteLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Data Privacy Settings
      </Typography>
      
      <Typography variant="body1" paragraph>
        Control how your data is collected and used when interacting with our hotel AI assistant.
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      <FormGroup>
        <FormControlLabel
          control={
            <Switch
              checked={consentPreferences.serviceImprovement}
              onChange={handleConsentChange}
              name="serviceImprovement"
              color="primary"
            />
          }
          label="Service Improvement"
        />
        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
          Allow us to collect and analyze your conversations to improve our AI assistant's responses and fix issues.
        </Typography>
        
        <FormControlLabel
          control={
            <Switch
              checked={consentPreferences.modelTraining}
              onChange={handleConsentChange}
              name="modelTraining"
              color="primary"
            />
          }
          label="AI Model Training"
        />
        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
          Allow us to use anonymized conversations to train our AI models to better understand and respond to guest needs.
        </Typography>
        
        <FormControlLabel
          control={
            <Switch
              checked={consentPreferences.analytics}
              onChange={handleConsentChange}
              name="analytics"
              color="primary"
            />
          }
          label="Analytics"
        />
        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
          Allow us to analyze usage patterns to understand how guests interact with our AI assistant.
        </Typography>
        
        <FormControlLabel
          control={
            <Switch
              checked={consentPreferences.marketing}
              onChange={handleConsentChange}
              name="marketing"
              color="primary"
            />
          }
          label="Marketing"
        />
        <Typography variant="caption" color="text.secondary" sx={{ ml: 4, mb: 2 }}>
          Allow us to use your preferences to personalize marketing communications and offers.
        </Typography>
      </FormGroup>
      
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveConsent}
          disabled={saving}
        >
          {saving ? <CircularProgress size={24} /> : 'Save Preferences'}
        </Button>
        
        <Button
          variant="outlined"
          color="secondary"
          onClick={() => setShowDeleteDialog(true)}
        >
          Delete My Conversation History
        </Button>
      </Box>
      
      <Divider sx={{ my: 3 }} />
      
      <Typography variant="h6" gutterBottom>
        Your Data Rights
      </Typography>
      
      <Typography variant="body2" paragraph>
        Under data protection laws, you have the right to:
      </Typography>
      
      <ul>
        <Typography component="li" variant="body2">
          Access your personal data
        </Typography>
        <Typography component="li" variant="body2">
          Correct inaccurate personal data
        </Typography>
        <Typography component="li" variant="body2">
          Request deletion of your personal data
        </Typography>
        <Typography component="li" variant="body2">
          Restrict processing of your personal data
        </Typography>
        <Typography component="li" variant="body2">
          Request transfer of your personal data
        </Typography>
        <Typography component="li" variant="body2">
          Object to processing of your personal data
        </Typography>
      </ul>
      
      <Typography variant="body2" paragraph>
        To exercise any of these rights, please contact our data protection officer at privacy@hotel.com.
      </Typography>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
      >
        <DialogTitle>Delete Conversation History</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete all your conversation history with our AI assistant? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setShowDeleteDialog(false)} 
            color="primary"
            disabled={deleteLoading}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteHistory} 
            color="error" 
            variant="contained"
            disabled={deleteLoading}
          >
            {deleteLoading ? <CircularProgress size={24} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ConsentManager;