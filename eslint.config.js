module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: 'eslint:recommended',
  rules: {
    'no-console': 'warn', // Warns about console.log
    'semi': ['error', 'always'], // Enforces semicolons
  },
};