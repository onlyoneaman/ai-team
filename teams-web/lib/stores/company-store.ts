import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Company, CompanyDetails, AgentHierarchy, SuggestedPrompt } from '../types';
import * as api from '../api';

interface CompanyState {
  // Data
  companies: Company[];
  selectedCompanyId: string | null;
  companyDetails: CompanyDetails | null;
  agents: AgentHierarchy | null;
  suggestedPrompts: SuggestedPrompt[];

  // Loading states
  isLoadingCompanies: boolean;
  isLoadingDetails: boolean;

  // Actions
  fetchCompanies: () => Promise<void>;
  selectCompany: (companyId: string) => Promise<void>;
  refreshCompanyData: () => Promise<void>;
}

export const useCompanyStore = create<CompanyState>()(
  persist(
    (set, get) => ({
      // Initial state
      companies: [],
      selectedCompanyId: null,
      companyDetails: null,
      agents: null,
      suggestedPrompts: [],
      isLoadingCompanies: false,
      isLoadingDetails: false,

      // Fetch all companies
      fetchCompanies: async () => {
        set({ isLoadingCompanies: true });
        try {
          const companies = await api.getCompanies();
          set({ companies, isLoadingCompanies: false });

          // Auto-select first company if none selected
          const { selectedCompanyId } = get();
          if (!selectedCompanyId && companies.length > 0) {
            await get().selectCompany(companies[0].id);
          } else if (selectedCompanyId) {
            // Refresh data for currently selected company
            await get().refreshCompanyData();
          }
        } catch (error) {
          console.error('Failed to fetch companies:', error);
          set({ isLoadingCompanies: false });
        }
      },

      // Select a company and load its data
      selectCompany: async (companyId: string) => {
        set({ selectedCompanyId: companyId, isLoadingDetails: true });
        try {
          const [companyDetails, agents, suggestedPrompts] = await Promise.all([
            api.getCompany(companyId),
            api.getAgents(companyId),
            api.getSuggestedPrompts(companyId),
          ]);
          set({
            companyDetails,
            agents,
            suggestedPrompts,
            isLoadingDetails: false,
          });
        } catch (error) {
          console.error('Failed to load company data:', error);
          set({ isLoadingDetails: false });
        }
      },

      // Refresh current company data
      refreshCompanyData: async () => {
        const { selectedCompanyId } = get();
        if (selectedCompanyId) {
          await get().selectCompany(selectedCompanyId);
        }
      },
    }),
    {
      name: 'teams-ai-company',
      partialize: (state) => ({ selectedCompanyId: state.selectedCompanyId }),
    }
  )
);
