import React from 'react';

const PraktikaLanding: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-cyan-50 to-white">
      {/* Search Bar - Top of page on mobile */}
      <div className="px-4 pt-4 pb-2 bg-white lg:hidden">
        <div className="bg-gray-200 rounded-full px-6 py-3 text-gray-600 text-base">
          englishlab.ai
        </div>
      </div>

      {/* Header */}
      <header className="px-4 sm:px-6 lg:px-8 py-4 bg-white sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* Flask/Lab Container */}
              <circle cx="22" cy="22" r="20" fill="#0D9488"/>
              <path d="M16 10h12v6l-3 6c-1 2-1 4 0 6l3 6H16l3-6c1-2 1-4 0-6l-3-6v-6z" fill="#14B8A6"/>
              {/* Letter E */}
              <path d="M19 18h6M19 22h5M19 26h6" stroke="white" strokeWidth="2" strokeLinecap="round"/>
              {/* Bubbles */}
              <circle cx="26" cy="15" r="2" fill="#5EEAD4" opacity="0.8"/>
              <circle cx="29" cy="19" r="1.5" fill="#5EEAD4" opacity="0.6"/>
            </svg>
            <span className="text-2xl sm:text-3xl font-bold text-[#0D9488]">English Lab</span>
          </div>

          {/* Hamburger Menu */}
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" aria-label="Menu">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
        </div>

        {/* Search Bar - Desktop */}
        <div className="max-w-7xl mx-auto mt-4 hidden lg:block">
          <div className="bg-gray-200 rounded-full px-6 py-3 text-gray-600 text-base">
            englishlab.ai
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-br from-[#0D9488] via-[#14B8A6] to-[#2DD4BF] rounded-[2rem] lg:rounded-[3rem] overflow-hidden shadow-2xl">
            <div className="px-4 sm:px-8 lg:px-12 pt-10 lg:pt-16 pb-0">
              {/* Main Heading */}
              <h1 className="text-white text-[2.5rem] sm:text-5xl lg:text-6xl font-bold text-center leading-[1.15] mb-10 lg:mb-12 tracking-tight">
                Learn a new language<br />with AI tutors
              </h1>

              {/* Stats Badges */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-12 lg:gap-16 mb-12 lg:mb-16">
                {/* Rating Badge */}
                <div className="flex items-center gap-2 sm:gap-3">
                  {/* Left Laurel */}
                  <svg width="32" height="64" viewBox="0 0 32 64" fill="none" className="opacity-30 hidden sm:block">
                    <path d="M6 12c2.5 4 4 8 5 13 0.5 5 0.5 10 -0.5 15M10 17c2 3.5 2.5 7 3 11 0 4.5 -0.5 9 -1.5 13M14 22c1 2.5 1.5 5.5 1.5 9 0 3.5 -1 7 -2 10" stroke="#CCFBF1" strokeWidth="2" strokeLinecap="round"/>
                  </svg>

                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-0.5">
                      <span className="text-[2.5rem] sm:text-5xl leading-none">⭐</span>
                      <span className="text-white text-[2.5rem] sm:text-5xl lg:text-6xl font-bold leading-none">4.9</span>
                    </div>
                    <p className="text-white text-xs sm:text-sm font-medium opacity-90 mt-1">900k+ ratings</p>
                  </div>

                  {/* Right Laurel */}
                  <svg width="32" height="64" viewBox="0 0 32 64" fill="none" className="opacity-30 scale-x-[-1] hidden sm:block">
                    <path d="M6 12c2.5 4 4 8 5 13 0.5 5 0.5 10 -0.5 15M10 17c2 3.5 2.5 7 3 11 0 4.5 -0.5 9 -1.5 13M14 22c1 2.5 1.5 5.5 1.5 9 0 3.5 -1 7 -2 10" stroke="#CCFBF1" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>

                {/* Learners Badge */}
                <div className="flex items-center gap-2 sm:gap-3">
                  {/* Left Laurel */}
                  <svg width="32" height="64" viewBox="0 0 32 64" fill="none" className="opacity-30 hidden sm:block">
                    <path d="M6 12c2.5 4 4 8 5 13 0.5 5 0.5 10 -0.5 15M10 17c2 3.5 2.5 7 3 11 0 4.5 -0.5 9 -1.5 13M14 22c1 2.5 1.5 5.5 1.5 9 0 3.5 -1 7 -2 10" stroke="#CCFBF1" strokeWidth="2" strokeLinecap="round"/>
                  </svg>

                  <div className="text-center">
                    <p className="text-white text-[2.5rem] sm:text-5xl lg:text-6xl font-bold leading-none">20M+</p>
                    <p className="text-white text-xs sm:text-sm font-medium opacity-90 mt-1">learners</p>
                  </div>

                  {/* Right Laurel */}
                  <svg width="32" height="64" viewBox="0 0 32 64" fill="none" className="opacity-30 scale-x-[-1] hidden sm:block">
                    <path d="M6 12c2.5 4 4 8 5 13 0.5 5 0.5 10 -0.5 15M10 17c2 3.5 2.5 7 3 11 0 4.5 -0.5 9 -1.5 13M14 22c1 2.5 1.5 5.5 1.5 9 0 3.5 -1 7 -2 10" stroke="#CCFBF1" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>
              </div>

              {/* iPhone Mockup */}
              <div className="relative max-w-sm mx-auto pb-8 lg:pb-12">
                {/* iPhone Frame */}
                <div className="relative mx-auto w-full max-w-[340px]">
                  {/* Phone Container */}
                  <div className="relative bg-black rounded-[3rem] p-[0.4rem] shadow-[0_20px_60px_rgba(0,0,0,0.4)]" style={{ aspectRatio: '9/19.5' }}>
                    {/* Screen */}
                    <div className="relative bg-gradient-to-b from-[#E5E5E5] to-[#D4D4D4] rounded-[2.7rem] overflow-hidden h-full">
                      {/* Status Bar */}
                      <div className="absolute top-0 left-0 right-0 px-8 py-3 flex items-center justify-between text-xs z-10">
                        <span className="text-gray-700 font-medium">12:25</span>
                        <div className="flex items-center gap-1">
                          <svg width="16" height="12" viewBox="0 0 16 12" fill="none">
                            <rect width="1.5" height="5" rx="0.5" fill="#374151"/>
                            <rect x="3" width="1.5" height="8" rx="0.5" fill="#374151"/>
                            <rect x="6" width="1.5" height="11" rx="0.5" fill="#374151"/>
                            <rect x="9" width="1.5" height="9" rx="0.5" fill="#374151"/>
                          </svg>
                          <svg width="16" height="12" viewBox="0 0 16 12" fill="none">
                            <path d="M1 6c0-1.5 1-2.5 2.5-2.5h9c1.5 0 2.5 1 2.5 2.5s-1 2.5-2.5 2.5h-9C2 8.5 1 7.5 1 6z" fill="#374151"/>
                            <circle cx="8" cy="6" r="2" fill="white"/>
                          </svg>
                          <svg width="20" height="12" viewBox="0 0 20 12" fill="none">
                            <rect width="18" height="11" rx="2" stroke="#374151" strokeWidth="1.5" fill="none"/>
                            <rect x="19" y="4" width="1.5" height="3" rx="0.5" fill="#374151"/>
                          </svg>
                        </div>
                      </div>

                      {/* Dynamic Island */}
                      <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black rounded-full px-6 py-2 flex items-center gap-2 z-20">
                        <div className="flex gap-1">
                          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                        </div>
                        <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                            <path d="M9 3L4.5 7.5L3 6" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                          </svg>
                        </div>
                      </div>

                      {/* App Content */}
                      <div className="relative h-full pt-14 px-4 pb-4">
                        {/* Tutor Name */}
                        <div className="flex items-center gap-1.5 mb-3">
                          <span className="text-gray-700 font-medium text-sm">Alex</span>
                          <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
                            <path d="M5 6L1 0h8l-4 6z" fill="#6B7280"/>
                          </svg>
                        </div>

                        {/* 3D Character Avatar */}
                        <div className="relative w-full aspect-square rounded-[1.5rem] overflow-hidden mb-4 bg-gradient-to-br from-[#D1FAE5] via-[#A7F3D0] to-[#6EE7B7] shadow-sm">
                          {/* Placeholder for character - in production, this would be an actual image */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center">
                              <div className="text-7xl mb-2 drop-shadow-sm">👨🏽‍🏫</div>
                              <div className="text-[9px] text-gray-700 font-medium">AI Tutor Avatar</div>
                            </div>
                          </div>
                        </div>

                        {/* Chat Bubbles */}
                        <div className="space-y-2.5 mb-16">
                          {/* User Message */}
                          <div className="flex justify-end">
                            <div className="bg-white rounded-[1.2rem] rounded-tr-md px-3.5 py-2.5 max-w-[88%] shadow-sm border border-gray-200">
                              <span className="text-black text-[13px] leading-tight">I'm bad </span>
                              <span className="bg-[#F97316] text-white px-2 py-0.5 rounded-md text-[13px] font-medium leading-tight">to speak</span>
                              <span className="text-black text-[13px] leading-tight"> English</span>
                            </div>
                          </div>

                          {/* AI Correction */}
                          <div className="flex justify-start">
                            <div className="bg-[#14B8A6] rounded-[1.2rem] rounded-tl-md px-3.5 py-2.5 max-w-[92%] shadow-md">
                              <span className="text-white text-[13px] leading-tight">Do you mean «I'm bad </span>
                              <span className="bg-[#10B981] text-white px-2 py-0.5 rounded-md text-[13px] font-semibold leading-tight">at speaking</span>
                              <span className="text-white text-[13px] leading-tight"> English»?</span>
                            </div>
                          </div>
                        </div>

                        {/* Microphone Button */}
                        <div className="absolute bottom-5 left-1/2 -translate-x-1/2">
                          <button className="w-16 h-16 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.15)] flex items-center justify-center hover:scale-105 active:scale-95 transition-transform">
                            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                              <rect x="11" y="4" width="6" height="10" rx="3" fill="#14B8A6"/>
                              <path d="M8 12v2c0 3.3 2.7 6 6 6s6-2.7 6-6v-2M14 20v4M10 24h8" stroke="#14B8A6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Notch */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-7 bg-black rounded-b-3xl"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Section with Partners */}
            <div className="bg-white px-4 sm:px-8 lg:px-12 py-10 lg:py-12">
              {/* Partner Logos */}
              <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-10 lg:gap-12 mb-12">
                {/* GESS Awards */}
                <div className="flex items-center gap-3 grayscale hover:grayscale-0 transition-all">
                  <div className="w-14 h-14 bg-gradient-to-br from-gray-800 to-gray-900 rounded-full flex items-center justify-center shadow-md">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                      <circle cx="16" cy="16" r="11" stroke="white" strokeWidth="1.5"/>
                      <circle cx="16" cy="16" r="7" stroke="white" strokeWidth="1.5"/>
                      <path d="M16 9l2 5 5 0.5-3.5 3.5 1 5-4.5-2.5-4.5 2.5 1-5-3.5-3.5 5-0.5 2-5z" fill="white"/>
                    </svg>
                  </div>
                  <div className="text-left leading-none">
                    <div className="text-base font-bold text-gray-900">GESS</div>
                    <div className="text-[9px] text-gray-600 uppercase tracking-wide">Education</div>
                    <div className="text-[9px] text-gray-600 uppercase tracking-wide">Awards 2024</div>
                  </div>
                </div>

                {/* OpenAI Strategic Partner */}
                <div className="text-center grayscale hover:grayscale-0 transition-all">
                  <div className="text-2xl font-bold text-gray-900 mb-0.5">OpenAI</div>
                  <div className="text-[9px] text-gray-600 uppercase tracking-wider">Strategic Partner</div>
                </div>

                {/* Forbes */}
                <div className="grayscale hover:grayscale-0 transition-all">
                  <div className="text-3xl sm:text-4xl font-serif font-bold text-gray-900" style={{ fontFamily: 'Georgia, serif' }}>Forbes</div>
                </div>

                {/* TechCrunch */}
                <div className="grayscale hover:grayscale-0 transition-all">
                  <div className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">
                    <span className="text-[#0A9E32]">Tech</span>Crunch
                  </div>
                </div>
              </div>

              {/* Features Section Heading */}
              <div className="text-center border-t border-gray-200 pt-10">
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-wider">FEATURES</h2>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PraktikaLanding;
