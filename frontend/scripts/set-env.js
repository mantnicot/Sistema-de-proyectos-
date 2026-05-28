/**
 * Genera environment.prod.ts antes del build.
 * En Vercel/Railway: definir variable API_URL (ej. https://tu-api.up.railway.app/api/v1)
 */
const fs = require('fs');
const path = require('path');

const apiUrl = (process.env.API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
const target = path.join(__dirname, '../src/environments/environment.prod.ts');

const content = `export const environment = {
  production: true,
  apiUrl: '${apiUrl.replace(/'/g, "\\'")}',
};
`;

fs.writeFileSync(target, content, 'utf8');
console.log('[set-env] apiUrl:', apiUrl);
