import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().default('4000').transform(Number),
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'http', 'verbose', 'debug', 'silly']).default('info'),
  SWAGGER_ENABLED: z.string().default('true').transform((val) => val === 'true'),

  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),

  JWT_SECRET: z.string().min(10),
  JWT_REFRESH_SECRET: z.string().min(10),

  CORE_SERVICE_URL: z.string().url().default('http://localhost:4001'),
  AI_SERVICE_URL: z.string().url().default('http://localhost:4002'),
  GRAPH_SERVICE_URL: z.string().url().default('http://localhost:4003'),
  EVIDENCE_SERVICE_URL: z.string().url().default('http://localhost:4004'),
  NOTIFICATION_SERVICE_URL: z.string().url().default('http://localhost:4005'),
});

const _env = envSchema.safeParse(process.env);

if (!_env.success) {
  console.error('❌ Invalid environment variables:', _env.error.format());
  process.exit(1);
}

export const env = _env.data;
