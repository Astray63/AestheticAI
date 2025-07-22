// Setup for Jest tests - executed before each test file
import 'whatwg-fetch';
import { server } from './mocks/server';

// Polyfill TextEncoder/TextDecoder for Node.js environment - CRITICAL for MSW
const { TextEncoder, TextDecoder } = require('util');

(global as any).TextEncoder = TextEncoder;
(global as any).TextDecoder = TextDecoder;

// Establish API mocking before all tests.
beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests.
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished.
afterAll(() => server.close());

// Mock pour window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock pour window.URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mocked-url');
global.URL.revokeObjectURL = jest.fn();
