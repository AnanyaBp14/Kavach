import { hashPassword, verifyPassword } from '../../src/utils/hash';

describe('Auth Utils', () => {
  it('should hash and verify a password', async () => {
    const password = 'TestPassword123!';
    const hash = await hashPassword(password);
    
    expect(hash).toBeDefined();
    expect(hash).not.toBe(password);
    
    const isValid = await verifyPassword(password, hash);
    expect(isValid).toBe(true);
  });
});
