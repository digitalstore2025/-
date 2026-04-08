import { describe, it, expect } from 'vitest';
import { VerificationStatus } from '../../types';

describe('VerificationStatus', () => {
  it('has the correct Arabic label for VERIFIED', () => {
    expect(VerificationStatus.VERIFIED).toBe('موثق');
  });

  it('has the correct Arabic label for PARTIAL', () => {
    expect(VerificationStatus.PARTIAL).toBe('جزئي');
  });

  it('has the correct Arabic label for UNDER_REVIEW', () => {
    expect(VerificationStatus.UNDER_REVIEW).toBe('قيد المراجعة');
  });

  it('contains exactly three values', () => {
    const values = Object.values(VerificationStatus);
    expect(values).toHaveLength(3);
  });

  it('all values are strings', () => {
    Object.values(VerificationStatus).forEach(v => {
      expect(typeof v).toBe('string');
    });
  });
});
