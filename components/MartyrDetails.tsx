
import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Martyr } from '../types';
import { humanizeLegacy } from '../geminiService';

interface MartyrDetailsProps {
  martyr: Martyr;
  onClose: () => void;
}

const MartyrDetails: React.FC<MartyrDetailsProps> = ({ martyr, onClose }) => {
  const [humanizedStory, setHumanizedStory] = useState<string>('');
  const [loadingStory, setLoadingStory] = useState(false);
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0);
  const [copied, setCopied] = useState(false);
  const [isImageLoading, setIsImageLoading] = useState(true);
  const [showVideoControls, setShowVideoControls] = useState(false);
  const [showLightbox, setShowLightbox] = useState(false);
  const [isConfirmingOpen, setIsConfirmingOpen] = useState(false);
  
  // Gallery Zoom and Pan state
  const [zoom, setZoom] = useState({ scale: 1, x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });
  
  // Lightbox Zoom and Pan state
  const [lbZoom, setLbZoom] = useState({ scale: 1, x: 0, y: 0 });
  const [lbIsDragging, setLbIsDragging] = useState(false);
  const lbDragStart = useRef({ x: 0, y: 0 });

  const thumbnailRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const videoRef = useRef<HTMLVideoElement>(null);
  const galleryContainerRef = useRef<HTMLDivElement>(null);
  const lbContainerRef = useRef<HTMLDivElement>(null);

  const mediaList = martyr.media && martyr.media.length > 0 ? martyr.media : [martyr.imageUrl];

  const resetGalleryState = useCallback(() => {
    setZoom({ scale: 1, x: 0, y: 0 });
    setIsDragging(false);
    setShowVideoControls(false);
    setIsConfirmingOpen(false);
  }, []);

  const nextMedia = useCallback(() => {
    if (mediaList.length <= 1) return;
    setIsImageLoading(true);
    setCurrentMediaIndex((prev) => (prev + 1) % mediaList.length);
    resetGalleryState();
  }, [mediaList.length, resetGalleryState]);

  const prevMedia = useCallback(() => {
    if (mediaList.length <= 1) return;
    setIsImageLoading(true);
    setCurrentMediaIndex((prev) => (prev - 1 + mediaList.length) % mediaList.length);
    resetGalleryState();
  }, [mediaList.length, resetGalleryState]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (showLightbox) {
        if (e.key === 'Escape') setShowLightbox(false);
        return;
      }
      if (e.key === 'ArrowLeft') nextMedia();
      if (e.key === 'ArrowRight') prevMedia();
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [nextMedia, prevMedia, onClose, showLightbox]);

  useEffect(() => {
    const fetchHumanizedStory = async () => {
      setLoadingStory(true);
      const text = await humanizeLegacy(martyr.bio, martyr.dreams || []);
      setHumanizedStory(text);
      setLoadingStory(false);
    };
    fetchHumanizedStory();
    setCurrentMediaIndex(0);
    resetGalleryState();
  }, [martyr, resetGalleryState]);

  const getFileType = (url: string) => {
    const ext = url.split('.').pop()?.toLowerCase() || '';
    if (['pdf'].includes(ext)) return 'pdf';
    if (['txt', 'rtf', 'pages'].includes(ext)) return 'text';
    if (['doc', 'docx'].includes(ext)) return 'word';
    return 'generic';
  };

  const isDocument = (url: string) => {
    const docExtensions = ['.pdf', '.doc', '.docx', '.txt', '.pages', '.rtf'];
    return docExtensions.some(ext => url.toLowerCase().endsWith(ext));
  };

  const isVideo = (url: string) => {
    const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov'];
    return videoExtensions.some(ext => url.toLowerCase().endsWith(ext));
  };

  const handleShare = async () => {
    const shareText = `ليسوا أرقاماً - لنتذكر قصة الشهيد ${martyr.fullName}: ${martyr.bio}`;
    const shareUrl = window.location.href;

    if (navigator.share) {
      try {
        await navigator.share({
          title: `ليسوا أرقاماً - ${martyr.fullName}`,
          text: shareText,
          url: shareUrl,
        });
      } catch (err) {
        console.error('Error sharing:', err);
      }
    } else {
      try {
        await navigator.clipboard.writeText(`${shareText}\n${shareUrl}`);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    }
  };

  const handleStartVideo = () => {
    if (videoRef.current) {
      videoRef.current.muted = false;
      videoRef.current.play();
      setShowVideoControls(true);
    }
  };

  // Main Gallery Pan logic
  const handlePointerDown = (e: React.PointerEvent) => {
    if (zoom.scale <= 1) return;
    setIsDragging(true);
    dragStart.current = { x: e.clientX - zoom.x, y: e.clientY - zoom.y };
    (e.currentTarget as HTMLDivElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging) return;
    const bounds = 500 * zoom.scale;
    const newX = e.clientX - dragStart.current.x;
    const newY = e.clientY - dragStart.current.y;
    setZoom(prev => ({
      ...prev,
      x: Math.abs(newX) < bounds ? newX : prev.x,
      y: Math.abs(newY) < bounds ? newY : prev.y
    }));
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    setIsDragging(false);
  };

  // Lightbox Pan logic
  const handleLbPointerDown = (e: React.PointerEvent) => {
    if (lbZoom.scale <= 1) return;
    setLbIsDragging(true);
    lbDragStart.current = { x: e.clientX - lbZoom.x, y: e.clientY - lbZoom.y };
    (e.currentTarget as HTMLDivElement).setPointerCapture(e.pointerId);
  };

  const handleLbPointerMove = (e: React.PointerEvent) => {
    if (!lbIsDragging) return;
    const bounds = 1000 * lbZoom.scale;
    const newX = e.clientX - lbDragStart.current.x;
    const newY = e.clientY - lbDragStart.current.y;
    setLbZoom(prev => ({
      ...prev,
      x: Math.abs(newX) < bounds ? newX : prev.x,
      y: Math.abs(newY) < bounds ? newY : prev.y
    }));
  };

  const handleLbPointerUp = () => {
    setLbIsDragging(false);
  };

  // Zoom logic
  const handleWheel = (e: React.WheelEvent) => {
    if (isDocument(mediaList[currentMediaIndex]) || isVideo(mediaList[currentMediaIndex])) return;
    const delta = e.deltaY * -0.005;
    const newScale = Math.min(Math.max(zoom.scale + delta, 1), 5);
    setZoom(prev => ({
      ...prev,
      scale: newScale,
      x: newScale === 1 ? 0 : prev.x,
      y: newScale === 1 ? 0 : prev.y
    }));
  };

  const handleLbWheel = (e: React.WheelEvent) => {
    const delta = e.deltaY * -0.005;
    const newScale = Math.min(Math.max(lbZoom.scale + delta, 1), 10);
    setLbZoom(prev => ({
      ...prev,
      scale: newScale,
      x: newScale === 1 ? 0 : prev.x,
      y: newScale === 1 ? 0 : prev.y
    }));
  };

  const adjustLbZoom = (factor: number) => {
    setLbZoom(prev => {
      const newScale = Math.min(Math.max(prev.scale + factor, 1), 10);
      return {
        ...prev,
        scale: newScale,
        x: newScale === 1 ? 0 : prev.x,
        y: newScale === 1 ? 0 : prev.y
      };
    });
  };

  const resetLbZoom = () => setLbZoom({ scale: 1, x: 0, y: 0 });

  const renderDocumentIcon = (type: string, size: string = 'w-32 h-32') => {
    let icon;
    let colorClass = 'text-amber-500';
    let bgColorClass = 'bg-amber-500/10';
    let label = 'DOC';

    switch (type) {
      case 'pdf':
        colorClass = 'text-red-500';
        bgColorClass = 'bg-red-500/10';
        label = 'PDF';
        icon = (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2zM9 11h6m-6 4h6" />
        );
        break;
      case 'word':
        colorClass = 'text-blue-600';
        bgColorClass = 'bg-blue-600/10';
        label = 'DOCX';
        icon = (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        );
        break;
      case 'text':
        colorClass = 'text-stone-400';
        bgColorClass = 'bg-stone-400/10';
        label = 'TXT';
        icon = (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 6h16M4 12h16M4 18h7" />
        );
        break;
      default:
        icon = (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        );
    }

    return (
      <div className={`${size} ${colorClass} drop-shadow-2xl transition-all duration-500 group-hover/doc:scale-105 flex flex-col items-center justify-center ${bgColorClass} rounded-3xl p-6 border border-white/10 relative overflow-hidden`}>
        <svg xmlns="http://www.w3.org/2000/svg" className="w-full h-full" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {icon}
        </svg>
        <span className="absolute bottom-2 font-mono text-[10px] font-black opacity-40">{label}</span>
      </div>
    );
  };

  const handleOpenDocument = (url: string) => {
    window.open(url, '_blank');
    setIsConfirmingOpen(false);
  };

  const renderMediaContent = (url: string) => {
    if (isDocument(url)) {
      const type = getFileType(url);
      const fileName = url.split('/').pop() || 'وثيقة أرشيفية';
      
      return (
        <div 
          className="flex flex-col items-center justify-center gap-8 p-12 bg-stone-900 h-full w-full select-none group/doc transition-all"
        >
          <div className="relative">
            <div className="absolute inset-0 bg-white/5 blur-3xl rounded-full scale-150 group-hover/doc:scale-175 transition-transform duration-1000"></div>
            {renderDocumentIcon(type, 'w-48 h-48 sm:w-64 sm:h-64')}
          </div>
          
          <div className="text-center z-10 max-w-md">
            <h5 className="text-white text-2xl font-black mb-3">
              {type === 'pdf' ? 'وثيقة PDF موثقة' : type === 'word' ? 'مستند نصي مرجع' : type === 'text' ? 'شهادة نصية' : 'وثيقة أرشيفية'}
            </h5>
            <p className="text-stone-400 text-sm mb-10 overflow-hidden text-ellipsis whitespace-nowrap px-4 font-mono opacity-60">
              {fileName}
            </p>

            <div className="relative overflow-hidden min-h-[100px] flex items-center justify-center">
              {!isConfirmingOpen ? (
                <button 
                  onClick={() => setIsConfirmingOpen(true)}
                  className="px-10 py-4 bg-white/10 hover:bg-white/20 text-white rounded-2xl font-bold text-base transition-all flex items-center gap-3 shadow-2xl active:scale-95 border border-white/10 backdrop-blur-md animate-in fade-in slide-in-from-bottom-2"
                >
                  <span>فتح الوثيقة كاملة</span>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </button>
              ) : (
                <div className="flex flex-col gap-5 animate-in fade-in zoom-in duration-300 text-center">
                  <p className="text-amber-400 text-sm font-bold">هل تود مغادرة الصفحة الحالية لفتح الوثيقة؟</p>
                  <div className="flex gap-4 justify-center">
                    <button 
                      onClick={() => handleOpenDocument(url)}
                      className="px-10 py-3 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-bold text-sm transition-all shadow-xl active:scale-95"
                    >
                      تأكيد والفتح
                    </button>
                    <button 
                      onClick={() => setIsConfirmingOpen(false)}
                      className="px-10 py-3 bg-white/5 hover:bg-white/10 text-stone-300 rounded-xl font-bold text-sm transition-all active:scale-95 border border-white/5"
                    >
                      إلغاء
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    if (isVideo(url)) {
      return (
        <div className="w-full h-full flex items-center justify-center bg-black relative group/video">
           <video
            key={url}
            ref={videoRef}
            src={url}
            autoPlay
            muted={!showVideoControls}
            controls={showVideoControls}
            playsInline
            loop={!showVideoControls}
            className="max-w-full max-h-full object-contain"
          />
          {!showVideoControls && (
            <div 
              onClick={handleStartVideo}
              className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover/video:bg-black/40 transition-colors cursor-pointer z-20"
            >
              <div className="w-24 h-24 flex items-center justify-center bg-white/10 backdrop-blur-md rounded-full border border-white/30 scale-90 group-hover/video:scale-100 opacity-0 group-hover/video:opacity-100 transition-all duration-300 shadow-2xl">
                <svg className="w-10 h-10 text-white translate-x-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.333-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                </svg>
              </div>
            </div>
          )}
        </div>
      );
    }

    return (
      <div 
        ref={galleryContainerRef}
        className="w-full h-full flex items-center justify-center overflow-hidden relative group/image touch-none"
        onWheel={handleWheel}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        style={{ cursor: zoom.scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in' }}
      >
        {isImageLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-stone-950/40 backdrop-blur-xl z-10 transition-opacity">
            <div className="w-16 h-16 border-4 border-white/5 border-t-amber-500 rounded-full animate-spin shadow-2xl"></div>
          </div>
        )}
        <img 
          key={url}
          src={url} 
          alt={martyr.fullName} 
          onLoad={() => setIsImageLoading(false)}
          className={`max-w-full max-h-full object-contain select-none pointer-events-none transition-[opacity,filter,transform] duration-700 ${isImageLoading ? 'opacity-0 scale-95 blur-2xl' : 'opacity-100 scale-100 blur-0'}`}
          style={{ 
            transform: `translate(${zoom.x}px, ${zoom.y}px) scale(${zoom.scale})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1), opacity 0.7s ease, filter 0.7s ease'
          }}
        />
        
        <div className="absolute bottom-6 right-6 flex gap-2">
            <button 
                onClick={(e) => { e.stopPropagation(); resetLbZoom(); setShowLightbox(true); }}
                className="p-3 rounded-xl bg-black/60 backdrop-blur-md text-white border border-white/10 opacity-0 group-hover/image:opacity-100 transition-opacity hover:bg-black/80 shadow-2xl"
                title="عرض بدقة عالية"
            >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                </svg>
            </button>
        </div>

        <div className={`absolute bottom-6 left-6 p-4 rounded-2xl bg-black/60 backdrop-blur-md text-white/60 text-[10px] font-mono transition-opacity pointer-events-none ${zoom.scale > 1 || isDragging ? 'opacity-100' : 'opacity-0 group-hover/image:opacity-100'}`}>
          {zoom.scale > 1 ? 'اسحب للتحريك • استخدم عجلة الفأرة للتصغير' : 'انقر للزوم • استخدم عجلة الفأرة للتقريب'}
        </div>
      </div>
    );
  };

  const renderThumbnail = (url: string, idx: number) => {
    if (isDocument(url)) {
      const type = getFileType(url);
      return (
        <div className="flex items-center justify-center w-full h-full bg-stone-800 border border-white/5">
          {renderDocumentIcon(type, 'w-10 h-10')}
        </div>
      );
    }
    if (isVideo(url)) {
      return (
        <div className="w-full h-full relative group/thumb flex items-center justify-center bg-stone-900">
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <svg className="w-8 h-8 text-white/80 drop-shadow-lg" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.333-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
            </svg>
          </div>
          <div className="absolute inset-0 bg-black/40 group-hover/thumb:bg-black/20 transition-colors"></div>
        </div>
      );
    }
    return (
      <div className="w-full h-full relative group/thumb">
        <img src={url} className="w-full h-full object-cover transition-transform group-hover/thumb:scale-110" alt={`thumbnail ${idx}`} />
        <div className="absolute inset-0 bg-black/20 group-hover/thumb:bg-transparent transition-colors"></div>
      </div>
    );
  };

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-0 sm:p-6 bg-stone-950/95 backdrop-blur-2xl animate-in fade-in zoom-in duration-500">
        <div className="bg-white w-full max-w-7xl max-h-full sm:max-h-[95vh] sm:rounded-[3rem] shadow-[0_0_120px_rgba(0,0,0,0.7)] relative flex flex-col lg:flex-row overflow-hidden border border-white/5">
          
          {/* Gallery Carousel Section */}
          <div className="lg:w-3/5 xl:w-2/3 relative bg-stone-950 flex flex-col h-[50vh] lg:h-auto group">
            
            {/* Carousel Controls Overlay */}
            <div className="absolute top-0 inset-x-0 p-8 flex justify-between items-start z-40 pointer-events-none">
              <div className="flex gap-4 pointer-events-auto">
                <button 
                  onClick={onClose}
                  className="p-4 rounded-2xl bg-white/10 hover:bg-white/25 text-white backdrop-blur-2xl transition-all shadow-2xl active:scale-90 border border-white/10 group/close"
                  title="إغلاق المعرض"
                >
                  <svg className="h-6 w-6 transition-transform group-hover/close:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
                <button 
                  onClick={handleShare}
                  className="p-4 rounded-2xl bg-white/10 hover:bg-white/25 text-white backdrop-blur-2xl transition-all flex items-center gap-3 px-6 shadow-2xl active:scale-90 border border-white/10"
                >
                  {copied ? <span className="text-xs font-bold uppercase tracking-widest text-amber-400">تم الحفظ</span> : <><svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg><span className="hidden sm:inline text-xs font-bold uppercase tracking-[0.2em]">تخليد الذكرى</span></>}
                </button>
              </div>
              <div className="px-6 py-3 rounded-2xl bg-black/60 backdrop-blur-2xl border border-white/10 text-amber-500 text-sm font-mono tracking-widest shadow-2xl pointer-events-auto select-none">
                {String(currentMediaIndex + 1).padStart(2, '0')} <span className="text-white/20 mx-2">/</span> {String(mediaList.length).padStart(2, '0')}
              </div>
            </div>

            {/* Carousel Viewport */}
            <div className="flex-grow flex items-center justify-center relative overflow-hidden bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-stone-900 to-stone-950">
              {renderMediaContent(mediaList[currentMediaIndex])}
              
              {mediaList.length > 1 && (
                <>
                  {/* Navigation Arrows */}
                  <button 
                    onClick={prevMedia}
                    className="absolute right-4 sm:right-8 top-1/2 -translate-y-1/2 p-5 sm:p-7 rounded-full bg-white/5 hover:bg-white/15 text-white transition-all backdrop-blur-3xl z-40 border border-white/10 shadow-[0_0_40px_rgba(0,0,0,0.5)] active:scale-90"
                    aria-label="السابق"
                  >
                    <svg className="h-6 w-6 sm:h-8 sm:w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path d="M9 5l7 7-7 7"/></svg>
                  </button>
                  <button 
                    onClick={nextMedia}
                    className="absolute left-4 sm:left-8 top-1/2 -translate-y-1/2 p-5 sm:p-7 rounded-full bg-white/5 hover:bg-white/15 text-white transition-all backdrop-blur-3xl z-40 border border-white/10 shadow-[0_0_40px_rgba(0,0,0,0.5)] active:scale-90"
                    aria-label="التالي"
                  >
                    <svg className="h-6 w-6 sm:h-8 sm:w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path d="M15 19l-7-7 7-7"/></svg>
                  </button>

                  {/* Dot Indicators */}
                  <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex gap-3 z-40">
                    {mediaList.map((_, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          if (idx !== currentMediaIndex) setIsImageLoading(true);
                          setCurrentMediaIndex(idx);
                          resetGalleryState();
                        }}
                        className={`h-1.5 rounded-full transition-all duration-500 ${idx === currentMediaIndex ? 'w-10 bg-amber-500' : 'w-2 bg-white/20 hover:bg-white/40'}`}
                        aria-label={`انتقال إلى ${idx + 1}`}
                      />
                    ))}
                  </div>
                </>
              )}

              {/* Quick Jump Thumbnails */}
              {mediaList.length > 1 && (
                <div className="absolute bottom-20 inset-x-0 hidden sm:flex justify-center px-8 z-30 pointer-events-none">
                  <div className="flex gap-4 p-4 bg-black/40 backdrop-blur-3xl rounded-[2.5rem] border border-white/10 pointer-events-auto overflow-x-auto no-scrollbar max-w-full shadow-2xl opacity-0 group-hover:opacity-100 transition-opacity">
                    {mediaList.map((url, idx) => (
                      <button
                        key={idx}
                        ref={el => { thumbnailRefs.current[idx] = el; }}
                        onClick={() => {
                          if (idx !== currentMediaIndex) setIsImageLoading(true);
                          setCurrentMediaIndex(idx);
                          resetGalleryState();
                        }}
                        className={`relative flex-shrink-0 w-20 h-20 rounded-2xl overflow-hidden transition-all duration-500 ${
                          idx === currentMediaIndex 
                            ? 'ring-4 ring-amber-500 scale-110 opacity-100 shadow-[0_0_30px_rgba(245,158,11,0.4)]' 
                            : 'opacity-30 hover:opacity-100 grayscale hover:grayscale-0'
                        }`}
                      >
                        {renderThumbnail(url, idx)}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar Info Section */}
          <div className="lg:w-2/5 xl:w-1/3 flex flex-col bg-white overflow-y-auto h-[50vh] lg:h-auto border-r border-stone-100 shadow-[-20px_0_60px_rgba(0,0,0,0.05)]" dir="rtl">
            <div className="p-10 lg:p-14 space-y-12">
              <div className="space-y-6">
                <div className="flex flex-wrap gap-3">
                  <span className="text-[10px] px-4 py-1.5 bg-stone-100 text-stone-600 font-black rounded-full border border-stone-200 tracking-widest uppercase">
                    {martyr.verificationStatus}
                  </span>
                  <span className="text-[10px] px-4 py-1.5 bg-amber-100 text-amber-900 font-black rounded-full tracking-widest uppercase shadow-sm">
                    {martyr.category}
                  </span>
                </div>
                <h2 className="text-5xl lg:text-6xl font-black text-stone-900 leading-[1.1] tracking-tight">{martyr.fullName}</h2>
                <p className="text-2xl text-stone-400 font-serif italic border-r-4 border-amber-500/20 pr-4">
                  {martyr.age} عاماً • {martyr.residence}
                </p>
              </div>

              {/* Narrative Text */}
              <div className="space-y-8">
                <div className="flex items-center gap-6">
                  <h4 className="text-stone-400 text-[10px] font-black uppercase tracking-[0.3em] whitespace-nowrap">القصة الإنسانية</h4>
                  <div className="h-[2px] bg-stone-100 w-full rounded-full"></div>
                </div>

                {loadingStory ? (
                  <div className="space-y-5 animate-pulse py-2">
                    <div className="h-4 bg-stone-50 rounded-2xl w-full"></div>
                    <div className="h-4 bg-stone-50 rounded-2xl w-[94%]"></div>
                  </div>
                ) : (
                  <div className="bg-stone-50 rounded-[2.5rem] p-10 border border-stone-100 relative group/story overflow-hidden transition-all hover:shadow-xl hover:shadow-stone-200/50">
                    <div className="absolute top-0 right-0 w-2 h-full bg-amber-500/10"></div>
                    <p className="text-stone-800 text-2xl font-serif italic leading-[1.9] text-justify relative z-10">
                      {humanizedStory}
                    </p>
                    <svg className="absolute -bottom-4 -left-4 w-32 h-32 text-stone-200/20 z-0 pointer-events-none" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21L14.017 18C14.017 16.8954 14.9124 16 16.017 16H19.017C19.5693 16 20.017 15.5523 20.017 15V9C20.017 8.44772 19.5693 8 19.017 8H16.017C14.9124 8 14.017 7.10457 14.017 6V5C14.017 3.89543 14.9124 3 16.017 3H21.017C22.1216 3 23.017 3.89543 23.017 5V15C23.017 18.3137 20.3307 21 17.017 21H14.017ZM1.017 21L1.017 18C1.017 16.8954 1.91243 16 3.017 16H6.017C6.56928 16 7.017 15.5523 7.017 15V9C7.017 8.44772 6.56928 8 6.017 8H3.017C1.91243 8 1.017 7.10457 1.017 6V5C1.017 3.89543 1.91243 3 3.017 3H8.017C9.12157 3 10.017 3.89543 10.017 5V15C10.017 18.3137 7.33072 21 4.017 21H1.017Z"/></svg>
                  </div>
                )}
              </div>

              {/* Data Sections */}
              <div className="grid grid-cols-1 gap-12">
                <section className="space-y-4">
                  <h4 className="text-stone-400 text-[10px] font-black uppercase tracking-[0.3em]">المسار الحياتي</h4>
                  <div className="bg-white p-8 rounded-[2rem] border border-stone-100 shadow-sm transition-shadow hover:shadow-md">
                    <p className="text-stone-900 font-black text-xl mb-3">{martyr.profession}</p>
                    <p className="text-stone-600 text-base leading-relaxed">{martyr.bio}</p>
                  </div>
                </section>

                {martyr.dreams && martyr.dreams.length > 0 && (
                  <section className="space-y-6">
                    <h4 className="text-stone-400 text-[10px] font-black uppercase tracking-[0.3em]">أحلام لم ترى النور</h4>
                    <div className="flex flex-wrap gap-3">
                      {martyr.dreams.map((dream, i) => (
                        <span key={i} className="text-sm px-6 py-3 bg-stone-900 text-white rounded-[1.25rem] shadow-xl font-bold tracking-tight transition-transform hover:scale-105 active:scale-95">
                          {dream}
                        </span>
                      ))}
                    </div>
                  </section>
                )}

                <section className="bg-stone-50 p-10 rounded-[3rem] text-stone-900 relative border border-stone-100 overflow-hidden group/facts transition-colors hover:bg-stone-100/50">
                  <div className="absolute top-0 left-0 w-2 h-full bg-stone-200"></div>
                  <h4 className="text-stone-400 text-[10px] font-black uppercase mb-8 tracking-[0.3em]">وقائع التوثيق</h4>
                  <div className="space-y-8">
                    <div className="flex justify-between items-center border-b border-stone-200/50 pb-5 transition-transform group-hover/facts:translate-x-1">
                      <span className="text-stone-500 text-sm font-bold">تاريخ الارتقاء</span>
                      <span className="font-black text-stone-900 text-lg">{martyr.dateOfMartyrdom}</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-stone-200/50 pb-5 transition-transform group-hover/facts:translate-x-1">
                      <span className="text-stone-500 text-sm font-bold">الموقع الموثق</span>
                      <span className="font-black text-stone-900 text-lg">{martyr.placeOfMartyrdom}</span>
                    </div>
                    <div className="space-y-3 transition-transform group-hover/facts:translate-x-1">
                      <span className="text-stone-500 text-sm font-bold block">ظروف الاستشهاد</span>
                      <p className="text-stone-700 text-base leading-relaxed font-medium">{martyr.circumstances}</p>
                    </div>
                  </div>
                </section>

                <section className="pt-4 pb-12">
                  <h4 className="text-stone-400 text-[10px] font-black uppercase mb-6 tracking-[0.3em]">سجل المصادر</h4>
                  <div className="flex flex-wrap gap-3">
                    {martyr.sources.map((source, i) => (
                      <span key={i} className="text-[11px] px-4 py-2 bg-stone-50 text-stone-500 rounded-xl border border-stone-100 font-bold transition-colors hover:bg-stone-200 hover:text-stone-700">{source}</span>
                    ))}
                  </div>
                </section>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Full-Screen Lightbox for Images */}
      {showLightbox && !isVideo(mediaList[currentMediaIndex]) && !isDocument(mediaList[currentMediaIndex]) && (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-3xl flex flex-col animate-in fade-in duration-300">
            <div className="flex justify-between items-center p-8 z-20">
                <div className="flex flex-col text-right" dir="rtl">
                    <h3 className="text-white text-2xl font-black">{martyr.fullName}</h3>
                    <p className="text-stone-400 text-sm">معاينة عالية الدقة</p>
                </div>
                <button 
                    onClick={() => setShowLightbox(false)}
                    className="p-5 rounded-full bg-white/10 hover:bg-white/20 text-white transition-all active:scale-90 border border-white/10 group"
                >
                    <svg className="w-8 h-8 group-hover:rotate-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <div 
                ref={lbContainerRef}
                className="flex-grow relative overflow-hidden flex items-center justify-center touch-none select-none"
                onWheel={handleLbWheel}
                onPointerDown={handleLbPointerDown}
                onPointerMove={handleLbPointerMove}
                onPointerUp={handleLbPointerUp}
                style={{ cursor: lbZoom.scale > 1 ? (lbIsDragging ? 'grabbing' : 'grab') : 'zoom-in' }}
            >
                <img 
                    src={mediaList[currentMediaIndex]} 
                    alt={martyr.fullName}
                    className="max-w-full max-h-full object-contain pointer-events-none"
                    style={{ 
                        transform: `translate(${lbZoom.x}px, ${lbZoom.y}px) scale(${lbZoom.scale})`,
                        transformOrigin: 'center center',
                        transition: lbIsDragging ? 'none' : 'transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1)'
                    }}
                />
            </div>

            <div className="p-10 flex flex-col items-center gap-6 z-20">
                <div className="flex items-center gap-6 p-4 rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 shadow-2xl">
                    <button 
                        onClick={() => adjustLbZoom(-0.5)}
                        className="p-4 rounded-2xl hover:bg-white/10 text-white transition-colors"
                        title="تصغير"
                    >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M20 12H4"/></svg>
                    </button>
                    <div className="w-20 text-center font-mono text-amber-500 font-bold text-lg">
                        {Math.round(lbZoom.scale * 100)}%
                    </div>
                    <button 
                        onClick={() => adjustLbZoom(0.5)}
                        className="p-4 rounded-2xl hover:bg-white/10 text-white transition-colors"
                        title="تكبير"
                    >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M12 4v16m8-8H4"/></svg>
                    </button>
                    <div className="h-8 w-px bg-white/10 mx-2"></div>
                    <button 
                        onClick={resetLbZoom}
                        className="p-4 rounded-2xl hover:bg-white/10 text-stone-400 hover:text-white transition-all flex items-center gap-2 font-bold text-sm"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                        <span>إعادة الضبط</span>
                    </button>
                </div>
                <p className="text-white/30 text-[10px] font-mono tracking-widest uppercase" dir="rtl">
                    استخدم عجلة الفأرة أو اللمس للتحكم الدقيق بالتكبير
                </p>
            </div>
        </div>
      )}
    </>
  );
};

export default MartyrDetails;
