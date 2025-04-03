module.exports = {
    // Automatically clear mock calls, instances, contexts and results before every test
    clearMocks: true,

    // Indicates whether the coverage information should be collected while executing the test
    collectCoverage: true,

    // The directory where Jest should output its coverage files
    coverageDirectory: "coverage",

    // Indicates which provider should be used to instrument code for coverage
    coverageProvider: "v8",

    // A list of paths to directories that Jest should use to search for files in
    roots: [
        "<rootDir>/tests"
    ],

    // The test environment that will be used for testing
    testEnvironment: "jsdom",

    // A map from regular expressions to module names or to arrays of module names that allow to stub out resources with a single module
    moduleNameMapper: {
        "\\.(css|less|scss|sass)$": "identity-obj-proxy",
        "^@/(.*)$": "<rootDir>/src/$1"
    },

    // An array of regexp pattern strings that are matched against all test paths, matched tests are skipped
    testPathIgnorePatterns: [
        "/node_modules/",
        "/dist/"
    ],

    // Indicates whether each individual test should be reported during the run
    verbose: true,

    // Setup files to run before each test
    setupFilesAfterEnv: [
        "<rootDir>/jest.setup.js"
    ],

    // Coverage configuration
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    },

    // Collect coverage from these files
    collectCoverageFrom: [
        "src/**/*.{js,jsx}",
        "!src/**/*.test.{js,jsx}",
        "!src/**/index.js"
    ],

    // Transform files with babel
    transform: {
        "^.+\\.(js|jsx)$": "babel-jest"
    }
};