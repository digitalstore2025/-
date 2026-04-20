import { describe, it, expect, vi, beforeEach } from 'vitest';

const { mockGenerateContent } = vi.hoisted(() => ({
  mockGenerateContent: vi.fn(),
}));

// Mock the @google/genai module before importing geminiService
vi.mock('@google/genai', () => {
  return {
    GoogleGenAI: function () {
      return { models: { generateContent: mockGenerateContent } };
    },
  };
});

import { humanizeLegacy } from '../../geminiService';

describe('geminiService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns generated text on success', async () => {
    mockGenerateContent.mockResolvedValueOnce({ text: 'Generated human story' });
    const result = await humanizeLegacy('يحب الرسم', ['زيارة القدس']);
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
    expect(result).toBe('Generated human story');
  });

  it('returns fallback text when API throws', async () => {
    mockGenerateContent.mockRejectedValueOnce(new Error('Network error'));
    const result = await humanizeLegacy('bio text', ['dream one']);
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
    // Should not throw; returns fallback
    expect(result).not.toContain('Error');
  });

  it('returns fallback text when response.text is an empty string', async () => {
    mockGenerateContent.mockResolvedValueOnce({ text: '' });
    const result = await humanizeLegacy('bio', []);
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
  });

  it('passes bio and dreams to the AI model', async () => {
    mockGenerateContent.mockResolvedValueOnce({ text: 'Some story' });
    await humanizeLegacy('نبذة تجريبية', ['حلم أول', 'حلم ثانٍ']);
    expect(mockGenerateContent).toHaveBeenCalledTimes(1);
    const callArg = mockGenerateContent.mock.calls[0][0];
    expect(callArg.contents).toContain('نبذة تجريبية');
    expect(callArg.contents).toContain('حلم أول');
  });
});
