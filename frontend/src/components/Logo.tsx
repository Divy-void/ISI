import React from 'react';

export const Logo: React.FC<{ className?: string }> = ({ className = 'w-8 h-8' }) => (
  <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <rect width="36" height="36" rx="8" fill="#1D4ED8" />
    <path
      d="M10 11.5C10 10.6716 10.6716 10 11.5 10H20.5L26 15.5V24.5C26 25.3284 25.3284 26 24.5 26H11.5C10.6716 26 10 25.3284 10 24.5V11.5Z"
      stroke="white"
      strokeWidth="2"
      strokeLinejoin="round"
    />
    <path d="M20 10V16H26" stroke="white" strokeWidth="2" strokeLinejoin="round" />
    <path d="M14 20L16.5 22.5L22 17" stroke="#93C5FD" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
