import { FileText, Upload, X } from 'lucide-react';
import { useRef, useState, type DragEvent } from 'react';
import { cn } from '../../lib/cn';

const ACCEPTED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.md'];

interface MultiFileDropzoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  className?: string;
}

// Visually modeled on FileDropzone's dashed-border styling, but a distinct
// component: this accepts multiple PDF/DOCX/TXT documents that get POSTed
// to /api/extract for LLM synthesis, not a single JSON file validated
// client-side against NegotiationState/BatchSummary — different accept
// types and validation semantics, sharing only the look.
export function MultiFileDropzone({ files, onFilesChange, className }: MultiFileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  function addFiles(newFiles: FileList | File[]) {
    const existingNames = new Set(files.map((f) => f.name));
    const toAdd = Array.from(newFiles).filter((f) => !existingNames.has(f.name));
    if (toAdd.length) onFilesChange([...files, ...toAdd]);
  }

  function removeFile(name: string) {
    onFilesChange(files.filter((f) => f.name !== name));
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
        onDrop={(e: DragEvent<HTMLDivElement>) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
        }}
        className={cn(
          'flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed px-6 py-8 text-center transition-colors',
          isDragging ? 'border-brand bg-brand-soft' : 'border-hairline bg-surface hover:border-ink-muted'
        )}
      >
        <Upload className="h-6 w-6 text-ink-muted" />
        <p className="text-sm font-medium text-ink">Drop the case documents here</p>
        <p className="text-xs text-ink-muted">
          Framework documents, evaluation reports, complaint letters — {ACCEPTED_EXTENSIONS.join(', ')}. Add as many
          as you have.
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED_EXTENSIONS.join(',')}
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.length) addFiles(e.target.files);
            e.target.value = '';
          }}
        />
      </div>

      {files.length > 0 && (
        <ul className="mt-3 flex flex-col gap-1.5">
          {files.map((file) => (
            <li
              key={file.name}
              className="flex items-center gap-2 rounded-md border border-hairline bg-surface px-3 py-2 text-sm"
            >
              <FileText className="h-4 w-4 shrink-0 text-ink-muted" />
              <span className="min-w-0 flex-1 truncate text-ink">{file.name}</span>
              <span className="shrink-0 text-xs text-ink-muted">{(file.size / 1024).toFixed(0)} KB</span>
              <button
                type="button"
                onClick={() => removeFile(file.name)}
                className="shrink-0 rounded p-0.5 text-ink-muted hover:bg-page hover:text-critical"
                aria-label={`Remove ${file.name}`}
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
