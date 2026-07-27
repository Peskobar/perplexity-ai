import React from 'react';
import OknoCzatu from '@/components/chat/OknoCzatu';
import { cn } from '@/lib/utils';

interface GlownaZawartoscProps extends React.HTMLAttributes<HTMLElement> {}

const GlownaZawartosc: React.FC<GlownaZawartoscProps> = ({ className, ...props }) => (
  <main className={cn('container mx-auto flex-grow p-4', className)} {...props}>
    <OknoCzatu />
  </main>
);

export default GlownaZawartosc;
