import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';

const swaggerDocument = {
  openapi: '3.0.0',
  info: {
    title: 'KAVACH AI API Gateway',
    version: '1.0.0',
    description: 'API documentation for KAVACH AI Gateway & Auth Service',
  },
  tags: [
    { name: 'Authentication' },
    { name: 'Users' },
    { name: 'Profile' },
    { name: 'Health' },
    { name: 'Gateway' },
    { name: 'Metrics' }
  ],
  components: {
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
      },
    },
  },
  security: [{ bearerAuth: [] }],
  paths: {
    '/api/v1/auth/login': {
      post: {
        tags: ['Authentication'],
        summary: 'Login user',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  email: { type: 'string' },
                  password: { type: 'string' },
                }
              }
            }
          }
        },
        responses: {
          200: { description: 'Successful login' },
          401: { description: 'Unauthorized' }
        }
      }
    },
    '/health': {
      get: {
        tags: ['Health'],
        summary: 'Get system health',
        responses: {
          200: { description: 'System is UP' }
        }
      }
    }
  }
};

export const setupSwagger = (app: Express) => {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
};
