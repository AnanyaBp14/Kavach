import { Request, Response, NextFunction } from 'express';
import { verifyAccessToken } from '../utils/jwt';
import { prisma } from '../config/prisma';
import { redis } from '../config/redis';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    role: string;
  };
}

export const authenticate = async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Missing or invalid token' });
    }

    const token = authHeader.split(' ')[1];
    
    // Check if token is blacklisted in Redis
    const isBlacklisted = await redis.get(`bl:${token}`);
    if (isBlacklisted) {
      return res.status(401).json({ error: 'Token revoked' });
    }

    const payload = verifyAccessToken(token);

    // Check version to invalidate all tokens on password reset
    const user = await prisma.user.findUnique({
      where: { id: payload.userId },
      select: { refreshTokenVersion: true, status: true },
    });

    if (!user || user.status !== 'ACTIVE' || user.refreshTokenVersion !== payload.version) {
      return res.status(401).json({ error: 'Session invalid or user inactive' });
    }

    req.user = {
      id: payload.userId,
      role: payload.role,
    };

    next();
  } catch (error) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
};
