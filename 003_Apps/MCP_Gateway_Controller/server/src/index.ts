import express from 'express';
import { fileURLToPath } from 'url';
import path from 'path';
import { loadConfig } from './config.js';
import apiRouter from './routes/api.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dashboardDist = path.resolve(__dirname, '../../dashboard/dist');

const app = express();

app.use(express.json());
app.use('/api', apiRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Static files for dashboard (in production)
app.use(express.static(dashboardDist));

// Fallback to index.html for SPA routing
app.get('/', (req, res) => {
  res.sendFile(path.join(dashboardDist, 'index.html'));
});

// Error handler middleware
app.use((err: any, req: any, res: any, next: any) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

let config;
try {
  config = loadConfig();
} catch (error) {
  console.error('Failed to load config:', error instanceof Error ? error.message : String(error));
  process.exit(1);
}

const PORT = config.port || 3003;

app.listen(PORT, () => {
  console.log(`MCP Gateway Server running on http://localhost:${PORT}`);
});
