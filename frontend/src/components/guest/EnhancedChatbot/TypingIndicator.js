import React from 'react';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';

// Define animations for the typing dots
const bounce = keyframes`
  0%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-5px);
  }
`;

// Styled components
const IndicatorContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'flex-start',
  marginBottom: theme.spacing(1.5),
  width: '100%',
}));

const IndicatorBubble = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(1.5),
  maxWidth: '80%',
  borderRadius: '20px 20px 20px 5px',
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[1],
  display: 'flex',
  alignItems: 'center',
  position: 'relative',
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: 0,
    left: -8,
    width: 15,
    height: 15,
    backgroundColor: theme.palette.background.paper,
    borderBottomRightRadius: 15,
  }
}));

const TypingDot = styled('span')(({ theme, delay }) => ({
  width: 8,
  height: 8,
  backgroundColor: theme.palette.primary.main,
  borderRadius: '50%',
  display: 'inline-block',
  margin: '0 2px',
  animation: `${bounce} 1.4s infinite ease-in-out both`,
  animationDelay: `${delay}s`,
}));

/**
 * TypingIndicator component that shows when the AI is processing a response
 * 
 * @param {Object} props - Component props
 * @param {string} props.message - Optional message to display alongside the indicator
 * @param {string} props.status - Status message (e.g., "Sending...", "Processing...")
 */
const TypingIndicator = ({ message = "Hotel AI is typing", status = null }) => {
  return (
    <IndicatorContainer>
      <IndicatorBubble elevation={1}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {status === 'sending' ? (
            <CircularProgress size={16} sx={{ mr: 1.5 }} />
          ) : (
            <Box sx={{ display: 'flex', mx: 1 }}>
              <TypingDot delay={0} />
              <TypingDot delay={0.2} />
              <TypingDot delay={0.4} />
            </Box>
          )}
          
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{ ml: 0.5 }}
          >
            {status === 'sending' ? 'Sending message...' : message}
          </Typography>
        </Box>
      </IndicatorBubble>
    </IndicatorContainer>
  );
};

export default TypingIndicator;