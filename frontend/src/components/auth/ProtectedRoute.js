import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';

/**
 * ProtectedRoute component to handle route protection based on authentication and roles
 * 
 * @param {Object} props
 * @param {string[]} [props.allowedRoles] - Array of roles allowed to access the route
 * @param {string[]} [props.allowedPermissions] - Array of permissions allowed to access the route
 * @param {string} [props.redirectPath='/login'] - Path to redirect to if access is denied
 */
const ProtectedRoute = ({ 
  allowedRoles, 
  allowedPermissions,
  redirectPath = '/login'
}) => {
  const { currentUser, loading, hasRole, hasPermission } = useAuth();
  const location = useLocation();

  // Show loading spinner while auth state is being determined
  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh' 
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // If not authenticated, redirect to login
  if (!currentUser) {
    return <Navigate to={redirectPath} state={{ from: location }} replace />;
  }

  // Check role-based access if roles are specified
  if (allowedRoles && allowedRoles.length > 0) {
    const hasAllowedRole = allowedRoles.some(role => hasRole(role));
    if (!hasAllowedRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // Check permission-based access if permissions are specified
  if (allowedPermissions && allowedPermissions.length > 0) {
    const hasAllowedPermission = allowedPermissions.some(permission => {
      const [resource, action] = permission.split(':');
      return hasPermission(resource, action);
    });
    
    if (!hasAllowedPermission) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // If all checks pass, render the protected content
  return <Outlet />;
};

export default ProtectedRoute;