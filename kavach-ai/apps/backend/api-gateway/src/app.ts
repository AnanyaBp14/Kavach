import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import { rateLimit } from 'express-rate-limit';
import promClient from 'prom-client';
import { createProxyMiddleware } from 'http-proxy-middleware';

import { env } from './config/env';
import { requestIdMiddleware } from './middleware/requestId.middleware';
import { morganMiddleware } from './middleware/logger.middleware';
import { metricsMiddleware } from './middleware/metrics.middleware';
import { errorHandler } from './middleware/errorHandler.middleware';
import { authenticate } from './middleware/auth.middleware';

import { authRouter } from './routes/auth.routes';
import { healthRouter } from './routes/health.routes';

import { userRouter } from './routes/user.routes';
import { profileRouter } from './routes/profile.routes';
import { setupSwagger } from './docs/swagger';

export const app = express();

// Security & Utility Middlewares
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(requestIdMiddleware);
app.use(morganMiddleware);
app.use(metricsMiddleware);

// Setup Swagger Docs
setupSwagger(app);

// Rate Limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', limiter);

// Prometheus Metrics Endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});

// Health Routes
app.use('/', healthRouter);

// Body parser for non-proxied routes
app.use(express.json());

// API Routes
app.use('/api/v1/auth', authRouter);
app.use('/api/v1/users', userRouter);
app.use('/api/v1/profile', profileRouter);

// Proxies for downstream services
const proxyOptions = {
  changeOrigin: true,
  pathRewrite: {
    '^/api/v1/core': '/api/v1',
    '^/api/v1/evidence': '/api/v1',
  },
  onProxyReq: (proxyReq: any, req: any, res: any) => {
    if (req.user) {
      proxyReq.setHeader('X-User-Id', req.user.id);
      proxyReq.setHeader('X-User-Role', req.user.role);
    }
    proxyReq.setHeader('X-Request-ID', req.headers['x-request-id']);
    proxyReq.setHeader('X-Correlation-ID', req.headers['x-correlation-id']);
  }
};

app.use('/api/v1/core', authenticate, createProxyMiddleware({ ...proxyOptions, target: env.CORE_SERVICE_URL }));
app.use('/api/v1/evidence', authenticate, createProxyMiddleware({ ...proxyOptions, target: env.EVIDENCE_SERVICE_URL }));
app.use('/api/v1/ai', authenticate, createProxyMiddleware({ ...proxyOptions, target: env.AI_SERVICE_URL }));

// Global Error Handler
app.use(errorHandler);
