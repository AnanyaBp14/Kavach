import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

export const requestIdMiddleware = (req: Request, res: Response, next: NextFunction) => {
  req.headers['x-request-id'] = req.headers['x-request-id'] || uuidv4();
  req.headers['x-correlation-id'] = req.headers['x-correlation-id'] || uuidv4();
  
  res.setHeader('X-Request-ID', req.headers['x-request-id'] as string);
  res.setHeader('X-Correlation-ID', req.headers['x-correlation-id'] as string);
  next();
};
