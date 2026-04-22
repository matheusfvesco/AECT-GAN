'use client';

import React from 'react';

interface BrandIconProps {
  Icon: React.ComponentType<any>;
  className?: string;
  stroke?: number;
  'aria-hidden'?: boolean;
}

export default function BrandIcon({
  Icon,
  className = '',
  stroke = 2,
  'aria-hidden': ariaHidden = true,
}: BrandIconProps) {
  return (
    // Icon components from lucide-react are client components; keep this file a client
    <Icon className={`w-12 h-12 ${className}`} strokeWidth={stroke} aria-hidden={ariaHidden} />
  );
}
