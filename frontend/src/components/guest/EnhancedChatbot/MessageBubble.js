import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Fade, Grow } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';

// Define animations
const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`;

const slideInUser = keyframes`
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

const slideInAssistant = keyframes`
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

// Styled components for message bubbles
const MessageContainer = styled(Box)(({ theme, isUser }) => ({
  display: 'flex',
  justifyContent: isUser ? 'flex-end' : 'flex-start',
  marginBottom: theme.spacing(1.5),
  width: '100%',
}));

const MessageBubbleWrapper = styled(Paper)(({ theme, isUser, isSystem, isError }) => ({
  padding: theme.spacing(2),
  maxWidth: '80%',
  borderRadius: isUser 
    ? '20px 20px 5px 20px' 
    : '20px 20px 20px 5px',
  backgroundColor: isError 
    ? theme.palette.error.light 
    : isSystem 
      ? theme.palette.grey[100] 
      : isUser 
        ? theme.palette.primary.light 
        : theme.palette.background.paper,
  color: isUser ? theme.palette.primary.contrastText : theme.palette.text.primary,
  boxShadow: theme.shadows[2],
  animation: `${isUser ? slideInUser : slideInAssistant} 0.3s ease-out`,
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    boxShadow: theme.shadows[3],
    transform: 'scale(1.01)',
  },
  position: 'relative',
  '&::after': isUser ? {
    content: '""',
    position: 'absolute',
    bottom: 0,
    right: -8,
    width: 15,
    height: 15,
    backgroundColor: theme.palette.primary.light,
    borderBottomLeftRadius: 15,
  } : isSystem ? {} : {
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

const MessageSender = styled(Typography)(({ theme, isUser, isSystem, isError }) => ({
  fontWeight: 'bold',
  marginBottom: theme.spacing(0.5),
  color: isError 
    ? theme.palette.error.dark 
    : isSystem 
      ? theme.palette.grey[700] 
      : isUser 
        ? theme.palette.primary.contrastText 
        : theme.palette.primary.main,
}));

const MessageContent = styled(Typography)(({ theme, isUser }) => ({
  color: isUser ? theme.palette.primary.contrastText : theme.palette.text.primary,
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
}));

const MessageTime = styled(Typography)(({ theme, isUser }) => ({
  fontSize: '0.7rem',
  color: isUser ? 'rgba(255, 255, 255, 0.7)' : theme.palette.text.secondary,
  marginTop: theme.spacing(1),
  textAlign: 'right',
}));

/**
 * MessageBubble component for displaying chat messages with animations
 * 
 * @param {Object} props - Component props
 * @param {string} props.role - Message role ('user', 'assistant', or 'system')
 * @param {string} props.content - Message content
 * @param {string} props.timestamp - Message timestamp (optional)
 * @param {boolean} props.isError - Whether the message is an error (optional)
 * @param {boolean} props.isNew - Whether the message is new (for animations)
 * @param {Object} props.status - Message status information (optional)
 */
const MessageBubble = ({ 
  role, 
  content, 
  timestamp, 
  isError = false, 
  isNew = false,
  status = null
}) => {
  const [show, setShow] = useState(!isNew);
  
  // Format message content with line breaks
  const formatMessageContent = (content) => {
    return content.split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        {i < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  // Get sender name based on role
  const getSenderName = () => {
    switch (role) {
      case 'user':
        return 'You';
      case 'system':
        return 'Hotel AI';
      case 'assistant':
        return 'Hotel AI';
      default:
        return 'Unknown';
    }
  };

  // Format timestamp if provided
  const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  }) : '';

  // Animation effect for new messages
  useEffect(() => {
    if (isNew) {
      const timer = setTimeout(() => setShow(true), 100);
      return () => clearTimeout(timer);
    }
  }, [isNew]);

  const isUser = role === 'user';
  const isSystem = role === 'system';

  return (
    <Grow in={show} timeout={isNew ? 500 : 0}>
      <MessageContainer isUser={isUser}>
        <MessageBubbleWrapper 
          isUser={isUser} 
          isSystem={isSystem}
          isError={isError}
          elevation={2}
        >
          <MessageSender 
            variant="body2" 
            isUser={isUser}
            isSystem={isSystem}
            isError={isError}
          >
            {getSenderName()}
          </MessageSender>
          
          <MessageContent 
            variant="body1" 
            isUser={isUser}
          >
            {formatMessageContent(content)}
          </MessageContent>
          
          {timestamp && (
            <MessageTime isUser={isUser}>
              {formattedTime}
            </MessageTime>
          )}
          
          {status && (
            <Box 
              sx={{ 
                mt: 1, 
                pt: 1, 
                borderTop: '1px solid', 
                borderColor: isUser ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)' 
              }}
            >
              <Typography 
                variant="caption" 
                sx={{ 
                  color: isUser ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                  display: 'block'
                }}
              >
                {status.text}
              </Typography>
            </Box>
          )}
        </MessageBubbleWrapper>
      </MessageContainer>
    </Grow>
  );
};

export default MessageBubble;