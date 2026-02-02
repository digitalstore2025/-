'use client';

import { useState, useEffect, useRef } from 'react';

interface JobResult {
  id: string;
  stage: string;
  progress: number;
  error: string | null;
  outputs: {
    script?: {
      intro: string;
      body: string;
      fullScript: string;
      caption: string;
      hashtags: string[];
    };
    radioUrl?: string;
    videoUrl?: string;
  };
}

export default function Home() {
  const [newsText, setNewsText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const pollInterval = useRef<NodeJS.Timeout | null>(null);

  // Poll for job status
  useEffect(() => {
    if (jobId && isProcessing) {
      pollInterval.current = setInterval(async () => {
        try {
          const response = await fetch(`/api/job/${jobId}`);
          const data = await response.json();

          if (data.stage === 'completed') {
            setResult(data);
            setIsProcessing(false);
            clearInterval(pollInterval.current!);
            showToast('تم الإنتاج بنجاح!');
          } else if (data.stage === 'error') {
            setError(data.error);
            setIsProcessing(false);
            clearInterval(pollInterval.current!);
          } else {
            setResult(data);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 2000);

      return () => {
        if (pollInterval.current) {
          clearInterval(pollInterval.current);
        }
      };
    }
  }, [jobId, isProcessing]);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  const handleGenerate = async () => {
    if (!newsText.trim() || newsText.length < 10) {
      showToast('يرجى إدخال نص الخبر (10 أحرف على الأقل)');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ newsText }),
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setJobId(data.jobId);
    } catch (err: any) {
      setError(err.message || 'حدث خطأ أثناء المعالجة');
      setIsProcessing(false);
    }
  };

  const handleCopyCaption = () => {
    if (result?.outputs?.script?.caption) {
      const fullCaption = `${result.outputs.script.caption}\n\n${result.outputs.script.hashtags.join(' ')}`;
      navigator.clipboard.writeText(fullCaption);
      showToast('تم نسخ الكابشن!');
    }
  };

  const getStageText = (stage: string) => {
    const stages: Record<string, string> = {
      init: 'جاري التحضير...',
      script: 'كتابة السكربت الإخباري...',
      voice: 'توليد الصوت...',
      radio: 'إنتاج MP3 الإذاعي...',
      video: 'إنتاج الفيديو...',
      completed: 'اكتمل الإنتاج!',
      error: 'حدث خطأ',
    };
    return stages[stage] || stage;
  };

  return (
    <main className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <header className="text-center mb-8">
        <div className="inline-flex items-center gap-3 mb-4">
          <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center text-3xl animate-pulse-glow">
            📻
          </div>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-2">
          <span className="text-accent">Quds</span>
          <span className="text-gold">Cast</span>
          <span className="text-white"> AI</span>
        </h1>
        <p className="text-gray-400 text-lg">
          منصة إعلامية عربية لأتمتة إنتاج الأخبار
        </p>
      </header>

      <div className="max-w-4xl mx-auto">
        {/* Input Section */}
        <div className="card mb-6 animate-slide-up">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="text-accent">📰</span>
            أدخل الخبر
          </h2>
          <textarea
            value={newsText}
            onChange={(e) => setNewsText(e.target.value)}
            placeholder="أدخل نص الخبر هنا... (مثال: أعلنت وزارة التربية والتعليم اليوم عن بدء العام الدراسي الجديد...)"
            className="w-full h-40 bg-primary/50 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 resize-none focus:border-accent focus:outline-none transition-colors"
            disabled={isProcessing}
          />
          <div className="flex justify-between items-center mt-4">
            <span className="text-gray-500 text-sm">
              {newsText.length} حرف
            </span>
            <button
              onClick={handleGenerate}
              disabled={isProcessing || newsText.length < 10}
              className={`btn-primary flex items-center gap-2 ${
                isProcessing ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isProcessing ? (
                <>
                  <div className="spinner w-5 h-5"></div>
                  جاري الإنتاج...
                </>
              ) : (
                <>
                  <span>🎬</span>
                  إنتاج المحتوى
                </>
              )}
            </button>
          </div>
        </div>

        {/* Progress Section */}
        {isProcessing && result && (
          <div className="card mb-6 animate-slide-up">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <span className="text-accent">⚙️</span>
              حالة الإنتاج
            </h2>
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <span className="text-gold">{getStageText(result.stage)}</span>
                <span className="text-accent">{result.progress}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${result.progress}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="card mb-6 border-red-500/50 animate-slide-up">
            <h2 className="text-xl font-bold mb-2 text-red-400 flex items-center gap-2">
              <span>❌</span>
              خطأ
            </h2>
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {result?.stage === 'completed' && (
          <div className="space-y-6 animate-slide-up">
            {/* Script Card */}
            {result.outputs.script && (
              <div className="card">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="text-accent">📝</span>
                  السكربت الإخباري
                </h2>
                <div className="bg-primary/50 rounded-xl p-4 mb-4">
                  <p className="text-gray-300 leading-relaxed whitespace-pre-line">
                    {result.outputs.script.fullScript}
                  </p>
                </div>
                <div className="bg-primary/50 rounded-xl p-4 mb-4">
                  <h3 className="text-gold font-bold mb-2">📌 الكابشن:</h3>
                  <p className="text-gray-300">{result.outputs.script.caption}</p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {result.outputs.script.hashtags.map((tag, i) => (
                      <span
                        key={i}
                        className="bg-accent/20 text-accent px-3 py-1 rounded-full text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <button onClick={handleCopyCaption} className="btn-secondary">
                  📋 نسخ الكابشن
                </button>
              </div>
            )}

            {/* Audio Player */}
            {result.outputs.radioUrl && (
              <div className="card">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="text-accent">🎙️</span>
                  البث الإذاعي MP3
                </h2>
                <audio
                  controls
                  src={result.outputs.radioUrl}
                  className="w-full mb-4"
                />
                <a
                  href={`/api/download/mp3/${result.id}`}
                  download
                  className="btn-primary inline-flex items-center gap-2"
                >
                  <span>⬇️</span>
                  تحميل MP3
                </a>
              </div>
            )}

            {/* Video Player */}
            {result.outputs.videoUrl && (
              <div className="card">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="text-accent">🎬</span>
                  الفيديو (9:16)
                </h2>
                <div className="bg-black rounded-xl overflow-hidden mb-4 max-w-sm mx-auto">
                  <video
                    controls
                    src={result.outputs.videoUrl}
                    className="w-full"
                    style={{ aspectRatio: '9/16' }}
                  />
                </div>
                <div className="text-center">
                  <a
                    href={`/api/download/mp4/${result.id}`}
                    download
                    className="btn-primary inline-flex items-center gap-2"
                  >
                    <span>⬇️</span>
                    تحميل MP4
                  </a>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <footer className="text-center mt-12 text-gray-500 text-sm">
          <p>QudsCast AI - منصة إعلامية عربية</p>
          <p className="mt-1">جميع الحقوق محفوظة © 2024</p>
        </footer>
      </div>

      {/* Toast Notification */}
      {toast && <div className="toast">{toast}</div>}
    </main>
  );
}
