'use client';

import { useState, useRef, useEffect } from 'react';

interface PlayerProps {
  src: string;
  type: 'audio' | 'video';
  title?: string;
}

export default function Player({ src, type, title }: PlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const mediaRef = useRef<HTMLAudioElement | HTMLVideoElement>(null);

  useEffect(() => {
    const media = mediaRef.current;
    if (!media) return;

    const handleTimeUpdate = () => setCurrentTime(media.currentTime);
    const handleDurationChange = () => setDuration(media.duration);
    const handleEnded = () => setIsPlaying(false);

    media.addEventListener('timeupdate', handleTimeUpdate);
    media.addEventListener('durationchange', handleDurationChange);
    media.addEventListener('ended', handleEnded);

    return () => {
      media.removeEventListener('timeupdate', handleTimeUpdate);
      media.removeEventListener('durationchange', handleDurationChange);
      media.removeEventListener('ended', handleEnded);
    };
  }, []);

  const togglePlay = () => {
    const media = mediaRef.current;
    if (!media) return;

    if (isPlaying) {
      media.pause();
    } else {
      media.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const media = mediaRef.current;
    if (!media) return;
    const time = parseFloat(e.target.value);
    media.currentTime = time;
    setCurrentTime(time);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const media = mediaRef.current;
    if (!media) return;
    const vol = parseFloat(e.target.value);
    media.volume = vol;
    setVolume(vol);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (type === 'video') {
    return (
      <div className="bg-black rounded-xl overflow-hidden">
        <video
          ref={mediaRef as React.RefObject<HTMLVideoElement>}
          src={src}
          controls
          className="w-full"
          style={{ aspectRatio: '9/16', maxHeight: '500px' }}
        />
        {title && (
          <div className="p-3 text-center text-gray-400 text-sm">{title}</div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-primary/50 rounded-xl p-4">
      <audio ref={mediaRef as React.RefObject<HTMLAudioElement>} src={src} />

      {title && (
        <h3 className="text-gold font-bold mb-3 text-center">{title}</h3>
      )}

      {/* Progress */}
      <div className="mb-3">
        <input
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-accent"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4">
        {/* Volume */}
        <div className="flex items-center gap-2">
          <span className="text-gray-400">🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
            className="w-20 h-1 bg-secondary rounded-lg appearance-none cursor-pointer accent-gold"
          />
        </div>

        {/* Play/Pause */}
        <button
          onClick={togglePlay}
          className="w-12 h-12 bg-accent hover:bg-red-600 rounded-full flex items-center justify-center text-2xl transition-all duration-300 transform hover:scale-110"
        >
          {isPlaying ? '⏸️' : '▶️'}
        </button>
      </div>
    </div>
  );
}
