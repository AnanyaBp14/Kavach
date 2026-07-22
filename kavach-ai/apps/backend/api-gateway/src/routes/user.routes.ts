import { Router } from 'express';
import { getAllUsers, updateUserStatus, deleteUser } from '../controllers/user.controller';
import { authenticate } from '../middleware/auth.middleware';
import { authorize } from '../middleware/rbac.middleware';

export const userRouter = Router();

userRouter.use(authenticate);
userRouter.use(authorize(['ADMIN', 'SUPER_ADMIN']));

userRouter.get('/', getAllUsers);
userRouter.patch('/:id', updateUserStatus);
userRouter.delete('/:id', deleteUser);
