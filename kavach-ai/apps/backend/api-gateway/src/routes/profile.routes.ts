import { Router } from 'express';
import { getProfile, updateProfile } from '../controllers/user.controller';
import { authenticate } from '../middleware/auth.middleware';

export const profileRouter = Router();

profileRouter.use(authenticate);
profileRouter.get('/', getProfile);
profileRouter.patch('/', updateProfile);
