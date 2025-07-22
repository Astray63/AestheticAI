import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Setup server with mocked API handlers
export const server = setupServer(...handlers);
