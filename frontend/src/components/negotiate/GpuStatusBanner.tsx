import { Zap } from 'lucide-react';
import { useEffect, useState } from 'react';
import { API_BASE } from '../../lib/api-config';
import { cn } from '../../lib/cn';

interface SystemStatus {
  ollama_host: string;
  reachable: boolean;
  using_gpu_tunnel: boolean;
}

// Polls rather than fetching once: OLLAMA_HOST itself is fixed for the API server's
// whole lifetime (resolved once at startup — see src/utils/ollama_connection.py), but
// *reachability* of whatever host is configured can change while this page stays open
// (a tunnel dropping, a local Ollama restart), and re-polling is the only way to reflect
// that without asking the user to refresh.
const POLL_INTERVAL_MS = 20_000;

export function GpuStatusBanner() {
  const [status, setStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const res = await fetch(`${API_BASE}/api/system-status`);
        if (!res.ok) return;
        const data = (await res.json()) as SystemStatus;
        if (!cancelled) setStatus(data);
      } catch {
        // API server not reachable at all — say nothing rather than show a confusing
        // status about Ollama specifically when the real problem is the API itself.
      }
    }

    poll();
    const interval = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  if (!status) return null;

  if (status.using_gpu_tunnel && status.reachable) {
    return (
      <div className="flex w-fit animate-fade-in-up items-center gap-1.5 rounded-full border border-good/20 bg-good-soft px-3 py-1 text-xs font-semibold text-good">
        <Zap className="h-3.5 w-3.5" />
        GPU connected — fast mode
      </div>
    );
  }

  const message = status.using_gpu_tunnel
    ? 'The GPU tunnel is configured but not responding right now. Check the Ronin connection, then reload this page.'
    : 'Not connected to the Ronin GPU — extraction and negotiation will be much slower on local hardware. Start the tunnel, then restart the API server, to use it.';

  return (
    <div
      className={cn(
        'flex animate-fade-in-up items-start gap-2.5 rounded-xl border border-warning/30 bg-warning-soft px-4 py-3 text-sm text-ink'
      )}
    >
      <Zap className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
      <p>{message}</p>
    </div>
  );
}
