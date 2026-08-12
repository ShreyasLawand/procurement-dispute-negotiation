import { Upload } from 'lucide-react';
import { useRef, useState, type DragEvent } from 'react';
import { cn } from '../../lib/cn';
import { parseUnknownDoc, type ValidatedDoc } from '../../lib/schema';
import { ErrorState } from '../ui/ErrorState';

interface FileDropzoneProps {
  onLoaded: (doc: ValidatedDoc) => void;
  className?: string;
}

export function FileDropzone({ onLoaded, className }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function handleFile(file: File) {
    setError(null);
    try {
      const text = await file.text();
      const json = JSON.parse(text);
      const doc = parseUnknownDoc(json);
      onLoaded(doc);
    } catch (err) {
      setError(err);
    }
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) void handleFile(file);
  }

  return (
    <div className={className}>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={cn(
          'flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed px-6 py-8 text-center transition-colors',
          isDragging ? 'border-ca bg-ca-soft' : 'border-hairline bg-surface hover:border-ink-muted'
        )}
      >
        <Upload className="h-6 w-6 text-ink-muted" />
        <p className="text-sm font-medium text-ink">Drop a negotiation log or batch_summary.json here</p>
        <p className="text-xs text-ink-muted">or click to browse — validated against the backend schema on load</p>
        <input
          ref={inputRef}
          type="file"
          accept="application/json,.json"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleFile(file);
            e.target.value = '';
          }}
        />
      </div>
      {error !== null && <ErrorState className="mt-3" title="Could not load this file" error={error} />}
    </div>
  );
}
