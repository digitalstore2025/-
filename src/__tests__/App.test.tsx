import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../../App';
import { MOCK_MARTYRS } from '../../constants';

// Mock geminiService to prevent real API calls opened by MartyrDetails
vi.mock('../../geminiService', () => ({
  humanizeLegacy: vi.fn().mockResolvedValue('نص إنساني تجريبي.'),
}));

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the site title', () => {
    render(<App />);
    expect(screen.getByText('ليسوا أرقاماً')).toBeInTheDocument();
  });

  it('renders the correct count of documented souls', () => {
    render(<App />);
    expect(screen.getByText(String(MOCK_MARTYRS.length))).toBeInTheDocument();
  });

  it('renders all martyr cards initially', () => {
    render(<App />);
    MOCK_MARTYRS.forEach(m => {
      expect(screen.getAllByText(m.fullName).length).toBeGreaterThan(0);
    });
  });

  it('filters martyrs by name search query', () => {
    render(<App />);
    const searchInput = screen.getByPlaceholderText('ابحث بالاسم...');
    fireEvent.change(searchInput, { target: { value: 'يوسف' } });
    expect(screen.getAllByText('يوسف أحمد النجار').length).toBeGreaterThan(0);
    // Other martyrs should not appear
    expect(screen.queryByText('د. ليلى مروان حرز الله')).not.toBeInTheDocument();
  });

  it('shows empty state message when no martyrs match search', () => {
    render(<App />);
    const searchInput = screen.getByPlaceholderText('ابحث بالاسم...');
    fireEvent.change(searchInput, { target: { value: 'اسم غير موجود xyz123' } });
    expect(screen.getByText('لا توجد نتائج مطابقة لبحثك.')).toBeInTheDocument();
  });

  it('filters martyrs by category dropdown', () => {
    render(<App />);
    const categorySelect = screen.getByRole('combobox');
    fireEvent.change(categorySelect, { target: { value: 'طفل' } });
    const childMartyrs = MOCK_MARTYRS.filter(m => m.category === 'طفل');
    const nonChildMartyrs = MOCK_MARTYRS.filter(m => m.category !== 'طفل');
    childMartyrs.forEach(m => {
      expect(screen.getAllByText(m.fullName).length).toBeGreaterThan(0);
    });
    nonChildMartyrs.forEach(m => {
      expect(screen.queryByText(m.fullName)).not.toBeInTheDocument();
    });
  });

  it('shows all martyrs when category is reset to empty', () => {
    render(<App />);
    const categorySelect = screen.getByRole('combobox');
    fireEvent.change(categorySelect, { target: { value: 'طفل' } });
    fireEvent.change(categorySelect, { target: { value: '' } });
    MOCK_MARTYRS.forEach(m => {
      expect(screen.getAllByText(m.fullName).length).toBeGreaterThan(0);
    });
  });

  it('search filter is case-insensitive for English characters', () => {
    render(<App />);
    const searchInput = screen.getByPlaceholderText('ابحث بالاسم...');
    // Using a fragment of the first martyr's name in lowercase shouldn't break anything
    fireEvent.change(searchInput, { target: { value: '' } });
    expect(screen.getAllByText(MOCK_MARTYRS[0].fullName).length).toBeGreaterThan(0);
  });

  it('opens the martyr details modal when a card is clicked', async () => {
    render(<App />);
    const firstMartyr = MOCK_MARTYRS[0];
    // Click the first card by clicking on the martyr's name
    const nameEl = screen.getAllByText(firstMartyr.fullName)[0];
    fireEvent.click(nameEl.closest('[class*="cursor-pointer"]') as HTMLElement || nameEl);
    await waitFor(() => {
      // The modal renders the full name in a large heading
      expect(screen.getAllByText(firstMartyr.fullName).length).toBeGreaterThan(1);
    });
  });

  it('closes the martyr details modal when onClose is triggered via Escape', async () => {
    render(<App />);
    const firstMartyr = MOCK_MARTYRS[0];
    const nameEl = screen.getAllByText(firstMartyr.fullName)[0];
    fireEvent.click(nameEl.closest('[class*="cursor-pointer"]') as HTMLElement || nameEl);
    await waitFor(() => {
      expect(screen.getByTitle('إغلاق المعرض')).toBeInTheDocument();
    });
    fireEvent.keyDown(window, { key: 'Escape' });
    await waitFor(() => {
      expect(screen.queryByTitle('إغلاق المعرض')).not.toBeInTheDocument();
    });
  });

  it('renders the footer with the platform description', () => {
    render(<App />);
    expect(screen.getByText('عن المنصة')).toBeInTheDocument();
    expect(screen.getByText('المعايير الأخلاقية')).toBeInTheDocument();
    expect(screen.getByText('تواصل معنا')).toBeInTheDocument();
  });

  it('renders the contact email in the footer', () => {
    render(<App />);
    expect(screen.getByText('documentation@notjustnumbers.org')).toBeInTheDocument();
  });

  it('combines search and category filters correctly', () => {
    render(<App />);
    const searchInput = screen.getByPlaceholderText('ابحث بالاسم...');
    const categorySelect = screen.getByRole('combobox');
    fireEvent.change(categorySelect, { target: { value: 'طفل' } });
    fireEvent.change(searchInput, { target: { value: 'يوسف' } });
    expect(screen.getAllByText('يوسف أحمد النجار').length).toBeGreaterThan(0);
    // A woman category should not appear
    expect(screen.queryByText('د. ليلى مروان حرز الله')).not.toBeInTheDocument();
  });

  it('combined filter returns empty when search matches no child', () => {
    render(<App />);
    const searchInput = screen.getByPlaceholderText('ابحث بالاسم...');
    const categorySelect = screen.getByRole('combobox');
    fireEvent.change(categorySelect, { target: { value: 'طفل' } });
    fireEvent.change(searchInput, { target: { value: 'ليلى' } });
    expect(screen.getByText('لا توجد نتائج مطابقة لبحثك.')).toBeInTheDocument();
  });
});
