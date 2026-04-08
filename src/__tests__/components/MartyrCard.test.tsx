import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import MartyrCard from '../../../components/MartyrCard';
import { Martyr, VerificationStatus } from '../../../types';

const baseMartyr: Martyr = {
  id: 'test-1',
  fullName: 'يوسف أحمد النجار',
  age: 7,
  residence: 'خانيونس',
  profession: 'طالب',
  bio: 'كان يحب الرسم وجمع الطوابع الملونة.',
  dateOfMartyrdom: '2023-11-15',
  placeOfMartyrdom: 'خانيونس',
  circumstances: 'استشهد إثر استهداف مربع سكني.',
  sources: ['سجل العائلة'],
  story: 'قصة يوسف المؤثرة.',
  imageUrl: 'https://example.com/image.jpg',
  verificationStatus: VerificationStatus.VERIFIED,
  category: 'طفل',
};

describe('MartyrCard', () => {
  it('renders the martyr full name', () => {
    render(<MartyrCard martyr={baseMartyr} onClick={vi.fn()} />);
    expect(screen.getByText('يوسف أحمد النجار')).toBeInTheDocument();
  });

  it('renders age and residence', () => {
    render(<MartyrCard martyr={baseMartyr} onClick={vi.fn()} />);
    expect(screen.getByText(/7 عاماً/)).toBeInTheDocument();
    expect(screen.getByText(/خانيونس/)).toBeInTheDocument();
  });

  it('renders the bio text', () => {
    render(<MartyrCard martyr={baseMartyr} onClick={vi.fn()} />);
    expect(screen.getByText('كان يحب الرسم وجمع الطوابع الملونة.')).toBeInTheDocument();
  });

  it('renders the verification status badge', () => {
    render(<MartyrCard martyr={baseMartyr} onClick={vi.fn()} />);
    expect(screen.getByText(VerificationStatus.VERIFIED)).toBeInTheDocument();
  });

  it('renders the category badge', () => {
    render(<MartyrCard martyr={baseMartyr} onClick={vi.fn()} />);
    expect(screen.getByText('طفل')).toBeInTheDocument();
  });

  it('renders the image with correct alt text', () => {
    render(<MartyrCard martyr={baseMartyr} onClick={vi.fn()} />);
    expect(screen.getByAltText('يوسف أحمد النجار')).toBeInTheDocument();
  });

  it('calls onClick with the martyr when clicked', () => {
    const onClick = vi.fn();
    render(<MartyrCard martyr={baseMartyr} onClick={onClick} />);
    fireEvent.click(screen.getByText('يوسف أحمد النجار'));
    expect(onClick).toHaveBeenCalledTimes(1);
    expect(onClick).toHaveBeenCalledWith(baseMartyr);
  });

  it('applies green classes for VERIFIED status', () => {
    render(<MartyrCard martyr={baseMartyr} onClick={vi.fn()} />);
    const badge = screen.getByText(VerificationStatus.VERIFIED);
    expect(badge.className).toContain('green');
  });

  it('applies yellow classes for PARTIAL status', () => {
    const partialMartyr = { ...baseMartyr, verificationStatus: VerificationStatus.PARTIAL };
    render(<MartyrCard martyr={partialMartyr} onClick={vi.fn()} />);
    const badge = screen.getByText(VerificationStatus.PARTIAL);
    expect(badge.className).toContain('yellow');
  });

  it('applies gray classes for UNDER_REVIEW status', () => {
    const reviewMartyr = { ...baseMartyr, verificationStatus: VerificationStatus.UNDER_REVIEW };
    render(<MartyrCard martyr={reviewMartyr} onClick={vi.fn()} />);
    const badge = screen.getByText(VerificationStatus.UNDER_REVIEW);
    expect(badge.className).toContain('gray');
  });

  it('renders a woman category correctly', () => {
    const womanMartyr = { ...baseMartyr, category: 'امرأة' as const };
    render(<MartyrCard martyr={womanMartyr} onClick={vi.fn()} />);
    expect(screen.getByText('امرأة')).toBeInTheDocument();
  });

  it('renders an elder category correctly', () => {
    const elderMartyr = { ...baseMartyr, category: 'مسن' as const, age: 68 };
    render(<MartyrCard martyr={elderMartyr} onClick={vi.fn()} />);
    expect(screen.getByText('مسن')).toBeInTheDocument();
    expect(screen.getByText(/68 عاماً/)).toBeInTheDocument();
  });
});
