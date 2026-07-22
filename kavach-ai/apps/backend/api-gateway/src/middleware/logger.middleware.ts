import morgan from 'morgan';
import { Request } from 'express';
import { logger } from '../config/logger';

export const morganMiddleware = morgan(
  (tokens, req, res) => {
    const expressReq = req as Request;
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      requestId: expressReq.headers['x-request-id'],
      correlationId: expressReq.headers['x-correlation-id'],
      method: tokens.method(req, res),
      endpoint: tokens.url(req, res),
      status: Number(tokens.status(req, res)),
      latency: Number(tokens['response-time'](req, res)),
      userAgent: tokens['user-agent'](req, res),
      ip: expressReq.ip,
    });
  },
  {
    stream: {
      write: (message: string) => {
        const data = JSON.parse(message);
        logger.http(`HTTP ${data.method} ${data.endpoint}`, data);
      },
    },
  }
);
