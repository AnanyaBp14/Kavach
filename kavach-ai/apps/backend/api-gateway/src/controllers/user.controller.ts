import { Request, Response, NextFunction } from 'express';
import { prisma } from '../config/prisma';
import { AuthenticatedRequest } from '../middleware/auth.middleware';

export const getProfile = async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user!.id },
      select: {
        id: true,
        name: true,
        email: true,
        phone: true,
        role: true,
        status: true,
        avatar: true,
        department: true,
        designation: true,
        organizationId: true,
      }
    });
    
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.status(200).json(user);
  } catch (error) {
    next(error);
  }
};

export const updateProfile = async (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  try {
    const { name, phone, avatar, language } = req.body;
    
    const user = await prisma.user.update({
      where: { id: req.user!.id },
      data: { name, phone, avatar, language },
      select: { id: true, name: true, phone: true }
    });

    await prisma.auditLog.create({
      data: {
        userId: user.id,
        action: 'PROFILE_UPDATED',
        resource: 'User',
        status: 'SUCCESS',
        ipAddress: req.ip,
      }
    });

    res.status(200).json(user);
  } catch (error) {
    next(error);
  }
};

export const getAllUsers = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const users = await prisma.user.findMany({
      select: {
        id: true,
        name: true,
        email: true,
        role: true,
        status: true,
      }
    });
    res.status(200).json(users);
  } catch (error) {
    next(error);
  }
};

export const updateUserStatus = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const { status, role } = req.body;
    
    const user = await prisma.user.update({
      where: { id },
      data: { status, role },
    });

    await prisma.auditLog.create({
      data: {
        userId: (req as AuthenticatedRequest).user?.id,
        action: 'ADMIN_UPDATE_USER',
        resource: 'User',
        status: 'SUCCESS',
        ipAddress: req.ip,
      }
    });

    res.status(200).json({ message: 'User updated successfully' });
  } catch (error) {
    next(error);
  }
};

export const deleteUser = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    await prisma.user.delete({ where: { id } });

    await prisma.auditLog.create({
      data: {
        userId: (req as AuthenticatedRequest).user?.id,
        action: 'ADMIN_DELETE_USER',
        resource: 'User',
        status: 'SUCCESS',
        ipAddress: req.ip,
      }
    });

    res.status(200).json({ message: 'User deleted successfully' });
  } catch (error) {
    next(error);
  }
};
