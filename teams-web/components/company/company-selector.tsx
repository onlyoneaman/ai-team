'use client';

import { useState } from 'react';
import { Building2, Check } from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { CompanyBadge } from './company-badge';
import { useCompanyStore } from '@/lib/stores';
import { cn } from '@/lib/utils';

export function CompanySelector() {
  const [open, setOpen] = useState(false);
  const {
    companies,
    selectedCompanyId,
    companyDetails,
    isLoadingCompanies,
    isLoadingDetails,
    selectCompany,
  } = useCompanyStore();

  const handleSelect = async (companyId: string) => {
    if (companyId !== selectedCompanyId) {
      await selectCompany(companyId);
    }
    setOpen(false);
  };

  const currentName = companyDetails?.name || 'Select Company';

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div>
          <CompanyBadge
            name={currentName}
            isLoading={isLoadingCompanies || isLoadingDetails}
          />
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-72 p-2" align="end">
        <div className="space-y-1">
          <p className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Switch Company
          </p>
          {companies.map((company) => (
            <button
              key={company.id}
              onClick={() => handleSelect(company.id)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left',
                'hover:bg-secondary transition-colors',
                selectedCompanyId === company.id && 'bg-secondary'
              )}
            >
              <div className={cn(
                'flex items-center justify-center w-9 h-9 rounded-lg',
                selectedCompanyId === company.id
                  ? 'bg-primary/10'
                  : 'bg-muted'
              )}>
                <Building2 className={cn(
                  'w-4 h-4',
                  selectedCompanyId === company.id
                    ? 'text-primary'
                    : 'text-muted-foreground'
                )} />
              </div>
              <span className="flex-1 text-sm font-medium truncate">
                {company.name}
              </span>
              {selectedCompanyId === company.id && (
                <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                  <Check className="w-3 h-3 text-primary-foreground" />
                </div>
              )}
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
