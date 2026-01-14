
import React, { useState, useMemo } from 'react';
import { MOCK_MARTYRS } from './constants';
import { Martyr, FilterOptions } from './types';
import MartyrCard from './components/MartyrCard';
import MartyrDetails from './components/MartyrDetails';

const App: React.FC = () => {
  const [filters, setFilters] = useState<FilterOptions>({
    searchQuery: '',
    category: '',
    residence: ''
  });
  const [selectedMartyr, setSelectedMartyr] = useState<Martyr | null>(null);

  const filteredMartyrs = useMemo(() => {
    return MOCK_MARTYRS.filter(m => {
      const matchesSearch = m.fullName.toLowerCase().includes(filters.searchQuery.toLowerCase());
      const matchesCategory = filters.category === '' || m.category === filters.category;
      const matchesResidence = filters.residence === '' || m.residence === filters.residence;
      return matchesSearch && matchesCategory && matchesResidence;
    });
  }, [filters]);

  const residences = Array.from(new Set(MOCK_MARTYRS.map(m => m.residence)));
  const categories = Array.from(new Set(MOCK_MARTYRS.map(m => m.category)));

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-right">
            <h1 className="text-3xl font-bold text-stone-900 leading-tight">ليسوا أرقاماً</h1>
            <p className="text-sm text-stone-500 font-serif">توثيق حياة شهداء غزة (2023 - 2025)</p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <input 
              type="text"
              placeholder="ابحث بالاسم..."
              className="px-4 py-2 border border-stone-300 rounded-lg text-sm text-right focus:outline-none focus:ring-2 focus:ring-stone-200 transition-all w-full md:w-64"
              value={filters.searchQuery}
              onChange={(e) => setFilters(prev => ({ ...prev, searchQuery: e.target.value }))}
            />
            <select 
              className="px-4 py-2 border border-stone-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-stone-200 bg-white"
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
            >
              <option value="">كل الفئات</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>
      </header>

      {/* Hero / Vision Section */}
      <section className="bg-stone-100 py-12 px-4 border-b border-stone-200">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <p className="text-stone-700 leading-relaxed text-lg font-serif">
            "خلف كل إحصائية تمر في الأخبار، هناك حياة كاملة، ضحكة كان من المفترض أن تكتمل، وحلم كان ينتظر الصباح. نحن هنا لنعيد لكل شهيد اسمه، ولنوثق للعالم أنهم بشرٌ أحبوا الحياة ما استطاعوا إليها سبيلاً."
          </p>
          <div className="flex justify-center gap-8 text-sm text-stone-500">
             <div className="text-center">
               <span className="block text-2xl font-bold text-stone-800">{MOCK_MARTYRS.length}</span>
               <span>أرواح موثقة</span>
             </div>
             <div className="text-center">
               <span className="block text-2xl font-bold text-stone-800">100%</span>
               <span>هدف التغطية</span>
             </div>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full">
        {filteredMartyrs.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {filteredMartyrs.map(martyr => (
              <MartyrCard 
                key={martyr.id} 
                martyr={martyr} 
                onClick={setSelectedMartyr} 
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 text-stone-400">
            <p className="text-xl">لا توجد نتائج مطابقة لبحثك.</p>
          </div>
        )}
      </main>

      {/* Details Modal */}
      {selectedMartyr && (
        <MartyrDetails 
          martyr={selectedMartyr} 
          onClose={() => setSelectedMartyr(null)} 
        />
      )}

      {/* Footer */}
      <footer className="bg-stone-900 text-stone-400 py-12 px-4">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 text-right" dir="rtl">
          <div>
            <h4 className="text-white font-bold mb-4">عن المنصة</h4>
            <p className="text-xs leading-relaxed">
              جهد تطوعي لتوثيق الجوانب الإنسانية لشهداء غزة. نعتمد على مصادر مفتوحة وبلاغات الأهالي الموثقة لضمان دقة الأرشفة التاريخية.
            </p>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">المعايير الأخلاقية</h4>
            <ul className="text-xs space-y-2">
              <li>• احترام خصوصية العائلات والذوي.</li>
              <li>• تجنب نشر الصور الصادمة أو العنيفة.</li>
              <li>• التوثيق بلغة إنسانية محايدة.</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">تواصل معنا</h4>
            <p className="text-xs">
              لإضافة بيانات أو تعديل معلومة، يرجى مراسلتنا عبر البريد الإلكتروني:<br/>
              <span className="text-stone-300">documentation@notjustnumbers.org</span>
            </p>
          </div>
        </div>
        <div className="max-w-7xl mx-auto mt-8 pt-8 border-t border-stone-800 text-center text-[10px]">
          © 2024 مبادرة ليسوا أرقاماً. جميع الحقوق محفوظة للذاكرة الجماعية.
        </div>
      </footer>
    </div>
  );
};

export default App;
