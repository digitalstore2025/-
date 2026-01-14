
export enum VerificationStatus {
  VERIFIED = 'موثق',
  PARTIAL = 'جزئي',
  UNDER_REVIEW = 'قيد المراجعة'
}

export interface Martyr {
  id: string;
  fullName: string;
  age: number;
  dateOfBirth?: string;
  placeOfBirth?: string;
  residence: string;
  socialStatus?: string;
  profession: string;
  bio: string;
  dateOfMartyrdom: string;
  placeOfMartyrdom: string;
  circumstances: string;
  sources: string[];
  story: string;
  testimonials?: string[];
  dreams?: string[];
  imageUrl: string; // Primary image
  media?: string[]; // Additional images or documents
  verificationStatus: VerificationStatus;
  category: 'طفل' | 'امرأة' | 'رجل' | 'مسن';
}

export interface FilterOptions {
  searchQuery: string;
  category: string;
  residence: string;
}
