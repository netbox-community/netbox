import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';

export default defineConfig(
  { ignores: ['dist/', 'node_modules/'] },
  js.configs.recommended,
  tseslint.configs.recommended,
  {
    // Build tooling runs under Node.js
    files: ['*.mjs', 'eslint.config.js'],
    languageOptions: {
      globals: { console: 'readonly', process: 'readonly' },
    },
  },
);
