
import { Martyr, VerificationStatus } from './types';

export const MOCK_MARTYRS: Martyr[] = [
  {
    id: '1',
    fullName: 'يوسف أحمد النجار',
    age: 7,
    dateOfBirth: '2016-05-12',
    placeOfBirth: 'غزة، حي الرمال',
    residence: 'خانيونس',
    socialStatus: 'طفل',
    profession: 'طالب في الصف الأول',
    bio: 'كان يحب الرسم وجمع الطوابع الملونة. حلمه كان أن يصبح مهندساً ليبني بيوتاً لا تسقط.',
    dateOfMartyrdom: '2023-11-15',
    placeOfMartyrdom: 'خانيونس - وسط المدينة',
    circumstances: 'استشهد إثر استهداف مربع سكني مجاور لمنزل عائلته.',
    sources: ['سجل العائلة', 'شهادة الأب المباشرة', 'وزارة الصحة'],
    story: 'يوسف لم يكن يحب الظلام، كان دائماً يترك ضوءاً صغيراً في غرفته. في ليلته الأخيرة، طلب من والدته أن تحكي له قصة عن البحر والسمك الملون. رحل يوسف وبقيت دفاتر رسمه شاهدة على أحلام لم تكتمل.',
    dreams: ['زيارة القدس للصلاة في الأقصى', 'الحصول على دراجة هوائية زرقاء'],
    imageUrl: 'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=600&h=800&fit=crop',
    media: [
      'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=600&h=800&fit=crop',
      'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?q=80&w=600&h=800&fit=crop',
      'https://www.w3schools.com/html/mov_bbb.mp4', // Sample video item
      'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf', // PDF document
      'https://picsum.photos/seed/doc1/600/800.txt' // Text document
    ],
    verificationStatus: VerificationStatus.VERIFIED,
    category: 'طفل'
  },
  {
    id: '2',
    fullName: 'د. ليلى مروان حرز الله',
    age: 34,
    dateOfBirth: '1989-08-22',
    placeOfBirth: 'غزة',
    residence: 'غزة - الرمال',
    socialStatus: 'متزوجة وأم لثلاثة أطفال',
    profession: 'طبيبة تخدير',
    bio: 'كرست حياتها لخدمة المرضى في مستشفى الشفاء. عرفت بهدوئها وقدرتها على طمأنة المرضى في أحلك الظروف.',
    dateOfMartyrdom: '2024-02-10',
    placeOfMartyrdom: 'محيط مستشفى الشفاء',
    circumstances: 'استهدفت أثناء محاولتها تقديم الإسعافات الأولية لمصابين في الشارع.',
    sources: ['نقابة الأطباء', 'شهادات الزملاء', 'تقارير إعلامية'],
    story: 'ليلى كانت ترى في مهنتها رسالة حياة. حتى في أيامها الأخيرة، رفضت مغادرة المستشفى رغم المخاطر، قائلة: "إذا غادرنا نحن، فمن سيبقى للمتألمين؟".',
    testimonials: ['"كانت ملاكاً يغطينا بالسكينة قبل الجراحة" - مريض سابق'],
    imageUrl: 'https://images.unsplash.com/photo-1559839734-2b71f1536783?q=80&w=600&h=800&fit=crop',
    media: [
      'https://images.unsplash.com/photo-1559839734-2b71f1536783?q=80&w=600&h=800&fit=crop',
      'https://images.unsplash.com/photo-1538108197017-c1346673919e?q=80&w=600&h=800&fit=crop'
    ],
    verificationStatus: VerificationStatus.VERIFIED,
    category: 'امرأة'
  },
  {
    id: '3',
    fullName: 'سامي كمال عابد',
    age: 68,
    dateOfBirth: '1955-03-10',
    placeOfBirth: 'يافا (مهجر)',
    residence: 'مخيم جباليا',
    socialStatus: 'جد لـ 15 حفيداً',
    profession: 'مدرس لغة عربية متقاعد',
    bio: 'حافظ لذاكرة النكبة، كان يروي لأحفاده قصصاً عن بيارات البرتقال في يافا التي هُجر منها والداه.',
    dateOfMartyrdom: '2023-12-05',
    placeOfMartyrdom: 'مخيم جباليا',
    circumstances: 'استشهد داخل منزله الذي رفض مغادرته.',
    sources: ['أقارب الدرجة الأولى', 'الهلال الأحمر'],
    story: 'عاش سامي حياته يحلم بالعودة، وكان يحتفظ بمفتاح حديدي قديم صدئ. كان يقول دائماً أن الذاكرة هي أقوى سلاح. استشهد وهو يحمل كتاباً في يده، وكأن المعرفة كانت رفيقه الأخير.',
    imageUrl: 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?q=80&w=600&h=800&fit=crop',
    verificationStatus: VerificationStatus.PARTIAL,
    category: 'مسن'
  }
];
