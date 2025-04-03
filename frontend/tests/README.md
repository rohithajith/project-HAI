# Frontend Testing Guide

## Overview
This directory contains the testing suite for the Hotel AI Frontend. We use Jest as our primary testing framework, with additional tools for comprehensive test coverage.

## Testing Strategy
- **Unit Testing**: Focus on testing individual components and utilities
- **Mocking**: Extensive use of mocks to isolate components
- **Coverage**: Aim for 80%+ coverage across branches, functions, and lines

## Key Testing Components

### 1. WebSocket Client Tests
- Verify WebSocket connection establishment
- Test event listener registration
- Validate message emission and reception
- Check error handling and reconnection logic

### 2. Notification Service Tests
- Test notification addition and removal
- Verify unique notification handling
- Check notification categorization and prioritization
- Validate event listener functionality

## Running Tests

### Install Dependencies
```bash
npm install
```

### Run Tests
```bash
# Run all tests
npm test

# Run tests with watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

## Test Configuration

### Jest Configuration (`jest.config.js`)
- Uses `jsdom` as test environment
- Configures coverage reporting
- Sets up module name mapping
- Defines coverage thresholds

### Test Setup (`jest.setup.js`)
- Mocks Socket.IO client
- Provides mock implementations for browser APIs
- Adds custom test matchers
- Resets mocks before each test

## Writing New Tests
1. Create test files with `.test.js` extension
2. Place tests in the appropriate subdirectory
3. Use descriptive test names
4. Cover various scenarios (happy path, edge cases, error conditions)

## Best Practices
- Keep tests small and focused
- Use meaningful assertions
- Mock external dependencies
- Avoid testing implementation details
- Aim for readability

## Debugging Tests
- Use `console.log()` or `console.debug()` for debugging
- Run specific test files: `npm test -- path/to/specific/test.js`
- Use `--verbose` flag for detailed output

## Continuous Integration
Tests are automatically run on:
- Pull Request creation
- Merge to main branch
- Scheduled intervals

## Troubleshooting
- Ensure all dependencies are installed
- Check Node.js and npm versions
- Clear Jest cache: `npm test -- --clearCache`

## Custom Matchers
- `toBeValidWebSocketMessage`: Validates WebSocket message structure

## Contributing
1. Write tests for new features
2. Ensure 80%+ coverage
3. Run tests before submitting PR
4. Update this README if testing infrastructure changes