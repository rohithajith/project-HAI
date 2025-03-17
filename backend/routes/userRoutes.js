const express = require('express');
const userController = require('../controllers/userController');
const { protect, restrictTo, hasPermission } = require('../middleware/authMiddleware');

const router = express.Router();

// All routes are protected
router.use(protect);

// Routes accessible by admin and manager
router.get('/', 
  restrictTo('admin', 'manager'), 
  userController.getAllUsers
);

// Get user by ID (accessible by admin, manager, or the user themselves)
router.get('/:id', userController.getUserById);

// Routes accessible by admin only
router.post('/',
  restrictTo('admin'),
  userController.createUser
);

router.put('/:id',
  userController.updateUser
);

router.delete('/:id',
  restrictTo('admin'),
  userController.deleteUser
);

// User roles management (admin only)
router.get('/:id/roles',
  restrictTo('admin'),
  userController.getUserRoles
);

router.put('/:id/roles',
  restrictTo('admin'),
  userController.updateUserRoles
);

module.exports = router;