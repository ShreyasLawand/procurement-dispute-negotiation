import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { ValidatedDoc } from './schema';

interface UploadedDataContextValue {
  doc: ValidatedDoc | null;
  setDoc: (doc: ValidatedDoc) => void;
  clear: () => void;
}

const UploadedDataContext = createContext<UploadedDataContextValue | null>(null);

export function UploadedDataProvider({ children }: { children: ReactNode }) {
  const [doc, setDocState] = useState<ValidatedDoc | null>(null);

  const value = useMemo<UploadedDataContextValue>(
    () => ({
      doc,
      setDoc: (d) => setDocState(d),
      clear: () => setDocState(null),
    }),
    [doc]
  );

  return <UploadedDataContext.Provider value={value}>{children}</UploadedDataContext.Provider>;
}

export function useUploadedData(): UploadedDataContextValue {
  const ctx = useContext(UploadedDataContext);
  if (!ctx) {
    throw new Error('useUploadedData must be used within an UploadedDataProvider');
  }
  return ctx;
}
