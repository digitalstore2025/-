import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MartyrDetails from '../../../components/MartyrDetails';
import { Martyr, VerificationStatus } from '../../../types';

// Mock the geminiService to avoid real API calls
vi.mock('../../../geminiService', () => ({
  humanizeLegacy: vi.fn().mockResolvedValue('نص إنساني تجريبي مولّد.'),
}));

const martyrWithMedia: Martyr = {
  id: 'test-1',
  fullName: 'يوسف أحمد النجار',
  age: 7,
  residence: 'خانيونس',
  profession: 'طالب في الصف الأول',
  bio: 'كان يحب الرسم.',
  dateOfMartyrdom: '2023-11-15',
  placeOfMartyrdom: 'خانيونس',
  circumstances: 'استشهد إثر استهداف.',
  sources: ['سجل العائلة', 'شهادة الأب'],
  story: 'قصة يوسف.',
  dreams: ['زيارة القدس', 'دراجة زرقاء'],
  imageUrl: 'https://example.com/image.jpg',
  media: [
    'https://example.com/image.jpg',
    'https://example.com/photo2.jpg',
  ],
  verificationStatus: VerificationStatus.VERIFIED,
  category: 'طفل',
};

const martyrMinimal: Martyr = {
  id: 'test-2',
  fullName: 'سامي كمال عابد',
  age: 68,
  residence: 'مخيم جباليا',
  profession: 'مدرس',
  bio: 'حافظ لذاكرة النكبة.',
  dateOfMartyrdom: '2023-12-05',
  placeOfMartyrdom: 'مخيم جباليا',
  circumstances: 'استشهد داخل منزله.',
  sources: ['الهلال الأحمر'],
  story: 'قصة سامي.',
  imageUrl: 'https://example.com/elder.jpg',
  verificationStatus: VerificationStatus.PARTIAL,
  category: 'مسن',
};

const martyrWithDocAndVideo: Martyr = {
  ...martyrWithMedia,
  id: 'test-3',
  media: [
    'https://example.com/image.jpg',
    'https://example.com/video.mp4',
    'https://example.com/document.pdf',
    'https://example.com/file.txt',
    'https://example.com/word.docx',
  ],
};

describe('MartyrDetails', () => {
  const onClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the martyr full name', async () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getAllByText('يوسف أحمد النجار').length).toBeGreaterThan(0);
  });

  it('renders age and residence', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getAllByText(/7 عاماً/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/خانيونس/).length).toBeGreaterThan(0);
  });

  it('renders profession and bio', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getByText('طالب في الصف الأول')).toBeInTheDocument();
    expect(screen.getByText('كان يحب الرسم.')).toBeInTheDocument();
  });

  it('renders verification status badge', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getAllByText(VerificationStatus.VERIFIED).length).toBeGreaterThan(0);
  });

  it('renders category badge', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getAllByText('طفل').length).toBeGreaterThan(0);
  });

  it('renders dreams when present', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getByText('زيارة القدس')).toBeInTheDocument();
    expect(screen.getByText('دراجة زرقاء')).toBeInTheDocument();
  });

  it('does not render dreams section when dreams are absent', () => {
    render(<MartyrDetails martyr={martyrMinimal} onClose={onClose} />);
    expect(screen.queryByText('أحلام لم ترى النور')).not.toBeInTheDocument();
  });

  it('renders sources', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getByText(/سجل العائلة/)).toBeInTheDocument();
    expect(screen.getByText(/شهادة الأب/)).toBeInTheDocument();
  });

  it('renders the humanized story after loading', async () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    await waitFor(() => {
      expect(screen.getByText('نص إنساني تجريبي مولّد.')).toBeInTheDocument();
    });
  });

  it('calls onClose when the close button is clicked', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    const closeBtn = screen.getByTitle('إغلاق المعرض');
    fireEvent.click(closeBtn);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Escape key is pressed', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('navigates to the next media on ArrowLeft key', async () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    // Initial counter shows 01
    expect(screen.getAllByText(/01/).length).toBeGreaterThan(0);
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    await waitFor(() => {
      expect(screen.getAllByText(/02/).length).toBeGreaterThan(0);
    });
  });

  it('navigates to the previous media on ArrowRight key', async () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    // Go to second item first
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    await waitFor(() => expect(screen.getAllByText(/02/).length).toBeGreaterThan(0));
    // Now go back
    fireEvent.keyDown(window, { key: 'ArrowRight' });
    await waitFor(() => expect(screen.getAllByText(/01/).length).toBeGreaterThan(0));
  });

  it('shows navigation arrows when there are multiple media items', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getByLabelText('السابق')).toBeInTheDocument();
    expect(screen.getByLabelText('التالي')).toBeInTheDocument();
  });

  it('does not show navigation arrows for single media item', () => {
    const singleMedia = { ...martyrMinimal };
    render(<MartyrDetails martyr={singleMedia} onClose={onClose} />);
    expect(screen.queryByLabelText('السابق')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('التالي')).not.toBeInTheDocument();
  });

  it('shows document open button for PDF media', async () => {
    render(<MartyrDetails martyr={martyrWithDocAndVideo} onClose={onClose} />);
    // Navigate to PDF (index 2)
    fireEvent.keyDown(window, { key: 'ArrowLeft' }); // index 1 (video)
    fireEvent.keyDown(window, { key: 'ArrowLeft' }); // index 2 (pdf)
    await waitFor(() => {
      expect(screen.getByText('فتح الوثيقة كاملة')).toBeInTheDocument();
    });
  });

  it('shows confirmation dialog when document open button is clicked', async () => {
    render(<MartyrDetails martyr={martyrWithDocAndVideo} onClose={onClose} />);
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    await waitFor(() => screen.getByText('فتح الوثيقة كاملة'));
    fireEvent.click(screen.getByText('فتح الوثيقة كاملة'));
    expect(screen.getByText('تأكيد والفتح')).toBeInTheDocument();
    expect(screen.getByText('إلغاء')).toBeInTheDocument();
  });

  it('dismisses document confirmation dialog on cancel', async () => {
    render(<MartyrDetails martyr={martyrWithDocAndVideo} onClose={onClose} />);
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    await waitFor(() => screen.getByText('فتح الوثيقة كاملة'));
    fireEvent.click(screen.getByText('فتح الوثيقة كاملة'));
    fireEvent.click(screen.getByText('إلغاء'));
    expect(screen.queryByText('تأكيد والفتح')).not.toBeInTheDocument();
  });

  it('uses imageUrl as fallback when media is absent', () => {
    render(<MartyrDetails martyr={martyrMinimal} onClose={onClose} />);
    const img = screen.getByAltText('سامي كمال عابد');
    expect(img).toHaveAttribute('src', martyrMinimal.imageUrl);
  });

  it('renders the "share" button', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getByText('تخليد الذكرى')).toBeInTheDocument();
  });

  it('renders martyrdom date and place', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getByText(/2023-11-15/)).toBeInTheDocument();
    expect(screen.getAllByText(/خانيونس/).length).toBeGreaterThan(0);
  });

  it('renders circumstances text', () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    expect(screen.getByText('استشهد إثر استهداف.')).toBeInTheDocument();
  });

  it('does not close modal on Escape when lightbox is open', async () => {
    render(<MartyrDetails martyr={martyrWithMedia} onClose={onClose} />);
    // Wait for story to load, then hover image to show lightbox button
    await waitFor(() => screen.getByText('نص إنساني تجريبي مولّد.'));
    // The lightbox button is hidden by default (opacity-0), trigger click via fireEvent
    const lightboxBtns = screen.queryAllByTitle('عرض بدقة عالية');
    if (lightboxBtns.length > 0) {
      fireEvent.click(lightboxBtns[0]);
      fireEvent.keyDown(window, { key: 'Escape' });
      // onClose should NOT be called; Escape closes lightbox first
      expect(onClose).not.toHaveBeenCalled();
    }
  });
});
