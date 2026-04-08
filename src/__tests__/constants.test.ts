import { describe, it, expect } from 'vitest';
import { MOCK_MARTYRS } from '../../constants';
import { VerificationStatus } from '../../types';

describe('MOCK_MARTYRS', () => {
  it('is a non-empty array', () => {
    expect(Array.isArray(MOCK_MARTYRS)).toBe(true);
    expect(MOCK_MARTYRS.length).toBeGreaterThan(0);
  });

  it('every martyr has a unique id', () => {
    const ids = MOCK_MARTYRS.map(m => m.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(MOCK_MARTYRS.length);
  });

  it('every martyr has required string fields', () => {
    MOCK_MARTYRS.forEach(m => {
      expect(typeof m.fullName).toBe('string');
      expect(m.fullName.length).toBeGreaterThan(0);
      expect(typeof m.residence).toBe('string');
      expect(typeof m.profession).toBe('string');
      expect(typeof m.bio).toBe('string');
      expect(typeof m.circumstances).toBe('string');
      expect(typeof m.story).toBe('string');
      expect(typeof m.imageUrl).toBe('string');
    });
  });

  it('every martyr has a positive numeric age', () => {
    MOCK_MARTYRS.forEach(m => {
      expect(typeof m.age).toBe('number');
      expect(m.age).toBeGreaterThan(0);
    });
  });

  it('every martyr has a valid verificationStatus', () => {
    const validStatuses = Object.values(VerificationStatus) as string[];
    MOCK_MARTYRS.forEach(m => {
      expect(validStatuses).toContain(m.verificationStatus);
    });
  });

  it('every martyr has a valid category', () => {
    const validCategories = ['طفل', 'امرأة', 'رجل', 'مسن'];
    MOCK_MARTYRS.forEach(m => {
      expect(validCategories).toContain(m.category);
    });
  });

  it('every martyr has a sources array with at least one entry', () => {
    MOCK_MARTYRS.forEach(m => {
      expect(Array.isArray(m.sources)).toBe(true);
      expect(m.sources.length).toBeGreaterThan(0);
    });
  });

  it('every martyr has a non-empty imageUrl', () => {
    MOCK_MARTYRS.forEach(m => {
      expect(m.imageUrl.length).toBeGreaterThan(0);
    });
  });

  it('covers multiple categories', () => {
    const categories = new Set(MOCK_MARTYRS.map(m => m.category));
    expect(categories.size).toBeGreaterThan(1);
  });

  it('dateOfMartyrdom follows YYYY-MM-DD pattern', () => {
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    MOCK_MARTYRS.forEach(m => {
      expect(m.dateOfMartyrdom).toMatch(datePattern);
    });
  });

  it('optional fields are the correct type when present', () => {
    MOCK_MARTYRS.forEach(m => {
      if (m.dateOfBirth !== undefined) expect(typeof m.dateOfBirth).toBe('string');
      if (m.placeOfBirth !== undefined) expect(typeof m.placeOfBirth).toBe('string');
      if (m.socialStatus !== undefined) expect(typeof m.socialStatus).toBe('string');
      if (m.testimonials !== undefined) expect(Array.isArray(m.testimonials)).toBe(true);
      if (m.dreams !== undefined) expect(Array.isArray(m.dreams)).toBe(true);
      if (m.media !== undefined) expect(Array.isArray(m.media)).toBe(true);
    });
  });
});
