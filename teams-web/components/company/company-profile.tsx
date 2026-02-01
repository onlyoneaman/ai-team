'use client';

import { motion } from 'framer-motion';
import {
  Building2,
  Megaphone,
  Users,
  Package,
  Sparkles,
  CheckCircle,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useCompanyStore } from '@/lib/stores';

function ProfileCard({
  icon: Icon,
  title,
  children,
  delay = 0,
}: {
  icon: React.ElementType;
  title: string;
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <Card className="h-full border-border/60 hover:border-primary/20 transition-colors">
        <CardContent className="p-5">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-secondary">
              <Icon className="w-4 h-4 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-foreground mb-1.5">{title}</h3>
              {children}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
      <div className="flex items-center gap-5">
        <Skeleton className="w-20 h-20 rounded-2xl" />
        <div className="space-y-3">
          <Skeleton className="h-8 w-56" />
          <Skeleton className="h-5 w-80" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-36 rounded-xl" />
        ))}
      </div>
    </div>
  );
}

export function CompanyProfile() {
  const { companyDetails, isLoadingDetails } = useCompanyStore();

  if (isLoadingDetails || !companyDetails) {
    return <LoadingSkeleton />;
  }

  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-4xl mx-auto px-6 py-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start gap-5 mb-10"
        >
          <div className="w-20 h-20 rounded-2xl bg-gradient-brand flex items-center justify-center shadow-lg">
            <Building2 className="w-10 h-10 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-1">
              {companyDetails.name}
            </h1>
            {companyDetails.mission && (
              <p className="text-lg text-muted-foreground">{companyDetails.mission}</p>
            )}
          </div>
        </motion.div>

        {/* Profile Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {/* Brand Voice */}
          {companyDetails.brand_voice && (
            <ProfileCard icon={Megaphone} title="Brand Voice" delay={0.1}>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {companyDetails.brand_voice}
              </p>
            </ProfileCard>
          )}

          {/* Target Audience */}
          {companyDetails.target_audience && (
            <ProfileCard icon={Users} title="Target Audience" delay={0.15}>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {companyDetails.target_audience}
              </p>
            </ProfileCard>
          )}

          {/* Philosophy */}
          {companyDetails.philosophy && (
            <ProfileCard icon={Sparkles} title="Philosophy" delay={0.2}>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {companyDetails.philosophy}
              </p>
            </ProfileCard>
          )}

          {/* Products */}
          {companyDetails.products && companyDetails.products.length > 0 && (
            <ProfileCard icon={Package} title="Products & Services" delay={0.25}>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {companyDetails.products.map((product, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="text-xs font-normal bg-secondary/80"
                  >
                    {product}
                  </Badge>
                ))}
              </div>
            </ProfileCard>
          )}
        </div>

        {/* Context Note */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="p-5 rounded-2xl bg-secondary/50 border border-border/60"
        >
          <div className="flex items-start gap-4">
            <div className="p-2.5 rounded-xl bg-primary/10">
              <CheckCircle className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-1">Context Loaded</h3>
              <p className="text-sm text-muted-foreground">
                This company profile provides context for the AI workforce. All agents
                have access to brand voice, products, and target audience to ensure
                aligned deliverables.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
