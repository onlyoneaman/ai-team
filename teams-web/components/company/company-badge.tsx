'use client';

import { Building2, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CompanyBadgeProps {
  name: string;
  isLoading?: boolean;
  onClick?: () => void;
  className?: string;
}

export function CompanyBadge({
  name,
  isLoading,
  onClick,
  className,
}: CompanyBadgeProps) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={cn(
        'flex items-center gap-2.5 px-3 py-2 rounded-lg',
        'bg-secondary/60 hover:bg-secondary transition-all',
        'text-sm font-medium text-foreground',
        'border border-transparent hover:border-border',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
    >
      <div className="flex items-center justify-center w-6 h-6 rounded-md bg-primary/10">
        <Building2 className="w-3.5 h-3.5 text-primary" />
      </div>
      <span className="max-w-[140px] truncate">{isLoading ? 'Loading...' : name}</span>
      <ChevronDown className="w-4 h-4 text-muted-foreground ml-1" />
    </button>
  );
}
