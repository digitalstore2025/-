'use client';

import { useState } from 'react';

interface DownloaderProps {
  mp3Url?: string;
  mp4Url?: string;
  caption?: string;
  hashtags?: string[];
  jobId: string;
}

export default function Downloader({
  mp3Url,
  mp4Url,
  caption,
  hashtags,
  jobId,
}: DownloaderProps) {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyCaption = async () => {
    if (!caption) return;

    const fullText = hashtags
      ? `${caption}\n\n${hashtags.join(' ')}`
      : caption;

    try {
      await navigator.clipboard.writeText(fullText);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="bg-primary/50 rounded-xl p-6">
      <h3 className="text-xl font-bold mb-4 text-center text-gold">
        📥 تحميل المحتوى
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Download MP3 */}
        {mp3Url && (
          <a
            href={`/api/download/mp3/${jobId}`}
            download
            className="flex flex-col items-center gap-2 p-4 bg-secondary/50 rounded-xl hover:bg-secondary transition-colors group"
          >
            <div className="w-12 h-12 bg-accent/20 rounded-full flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              🎵
            </div>
            <span className="text-white font-bold">تحميل MP3</span>
            <span className="text-gray-400 text-sm">البث الإذاعي</span>
          </a>
        )}

        {/* Download MP4 */}
        {mp4Url && (
          <a
            href={`/api/download/mp4/${jobId}`}
            download
            className="flex flex-col items-center gap-2 p-4 bg-secondary/50 rounded-xl hover:bg-secondary transition-colors group"
          >
            <div className="w-12 h-12 bg-accent/20 rounded-full flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              🎬
            </div>
            <span className="text-white font-bold">تحميل MP4</span>
            <span className="text-gray-400 text-sm">فيديو 9:16</span>
          </a>
        )}

        {/* Copy Caption */}
        {caption && (
          <button
            onClick={handleCopyCaption}
            className="flex flex-col items-center gap-2 p-4 bg-secondary/50 rounded-xl hover:bg-secondary transition-colors group"
          >
            <div className="w-12 h-12 bg-accent/20 rounded-full flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
              {copySuccess ? '✅' : '📋'}
            </div>
            <span className="text-white font-bold">
              {copySuccess ? 'تم النسخ!' : 'نسخ الكابشن'}
            </span>
            <span className="text-gray-400 text-sm">للنشر على السوشيال</span>
          </button>
        )}
      </div>

      {/* Hashtags Preview */}
      {hashtags && hashtags.length > 0 && (
        <div className="mt-4 p-4 bg-secondary/30 rounded-xl">
          <h4 className="text-sm text-gray-400 mb-2">الهاشتاقات:</h4>
          <div className="flex flex-wrap gap-2">
            {hashtags.map((tag, i) => (
              <span
                key={i}
                className="bg-accent/20 text-accent px-3 py-1 rounded-full text-sm"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
