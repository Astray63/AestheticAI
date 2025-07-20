// Polyfill for TextEncoder/TextDecoder (needed for MSW in Jest)
import { TextEncoder, TextDecoder } from 'util';

Object.assign(global, { TextDecoder, TextEncoder });
