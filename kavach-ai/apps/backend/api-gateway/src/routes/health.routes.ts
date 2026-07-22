import { Router } from 'express';
import { prisma } from '../config/prisma';
import { redis } from '../config/redis';

export const healthRouter = Router();

healthRouter.get('/health', async (req, res) => {
  res.status(200).json({ status: 'UP' });
});

healthRouter.get('/ready', async (req, res) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    await redis.ping();
    res.status(200).json({ status: 'READY' });
  } catch (error) {
    res.status(503).json({ status: 'NOT_READY', error: (error as Error).message });
  }
});

healthRouter.get('/live', (req, res) => {
  res.status(200).json({ status: 'LIVE' });
});

healthRouter.get('/version', (req, res) => {
  res.status(200).json({ version: process.env.npm_package_version || '1.0.0' });
});
