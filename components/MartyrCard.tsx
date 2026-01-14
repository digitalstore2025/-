
import React from 'react';
import { Martyr, VerificationStatus } from '../types';

interface MartyrCardProps {
  martyr: Martyr;
  onClick: (martyr: Martyr) => void;
}

const MartyrCard: React.FC<MartyrCardProps> = ({ martyr, onClick }) => {
  const getVerificationColor = (status: VerificationStatus) => {
    switch (status) {
      case VerificationStatus.VERIFIED: return 'bg-green-100 text-green-800 border-green-200';
      case VerificationStatus.PARTIAL: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div 
      onClick={() => onClick(martyr)}
      className="bg-white rounded-lg shadow-sm border border-stone-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer group"
    >
      <div className="relative aspect-[4/5] overflow-hidden">
        <img 
          src={martyr.imageUrl} 
          alt={martyr.fullName} 
          className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
        />
        <div className="absolute top-2 right-2 flex flex-col gap-1">
          <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getVerificationColor(martyr.verificationStatus)}`}>
            {martyr.verificationStatus}
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-stone-800/60 text-white backdrop-blur-sm">
            {martyr.category}
          </span>
        </div>
      </div>
      <div className="p-4 text-right">
        <h3 className="text-xl font-bold text-stone-900 mb-1">{martyr.fullName}</h3>
        <p className="text-sm text-stone-600 mb-2">{martyr.age} عاماً • {martyr.residence}</p>
        <p className="text-xs text-stone-500 line-clamp-2 leading-relaxed">
          {martyr.bio}
        </p>
      </div>
    </div>
  );
};

export default MartyrCard;
