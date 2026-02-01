'use client';

import { useEffect } from 'react';
import { Header } from '@/components/header';
import { Sidebar } from '@/components/sidebar/sidebar';
import { ChatArea } from '@/components/workspace/chat-area';
import { CompanyProfile } from '@/components/company/company-profile';
import { useCompanyStore, useUIStore } from '@/lib/stores';

export default function Home() {
  const { fetchCompanies } = useCompanyStore();
  const { currentView } = useUIStore();

  // Initialize: fetch companies on mount
  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  const isWorkspace = currentView === 'workspace';

  return (
    <div className="h-screen flex flex-col bg-gradient-subtle">
      <Header />

      {/* Main Content */}
      <main className="flex-1 flex min-h-0">
        {/* Sidebar - only show in workspace view */}
        {isWorkspace && <Sidebar />}

        {/* Content area */}
        <div className="flex-1 flex flex-col min-h-0">
          {isWorkspace ? <ChatArea /> : <CompanyProfile />}
        </div>
      </main>
    </div>
  );
}
