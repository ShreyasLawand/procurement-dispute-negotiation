import { Loader2, Zap } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { API_BASE, describeFetchError } from '../../lib/api-config';
import { cn } from '../../lib/cn';

interface SystemStatus {
  ollama_host: string;
  reachable: boolean;
  using_gpu_tunnel: boolean;
}

interface ConnectResult {
  success: boolean;
  already_connected: boolean;
  message: string;
}

// Polls rather than fetching once: OLLAMA_HOST itself is fixed for the API server's
// whole lifetime unless "Connect to GPU" below changes it, but *reachability* of whatever
// host is configured can change while this page stays open (a tunnel dropping, a local
// Ollama restart), and re-polling is the only way to reflect that without a page refresh.
const POLL_INTERVAL_MS = 20_000;

export function GpuStatusBanner() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [connectMessage, setConnectMessage] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/system-status`);
      if (!res.ok) return;
      const data = (await res.json()) as SystemStatus;
      setStatus(data);
    } catch {
      // API server not reachable at all — say nothing rather than show a confusing
      // status about Ollama specifically when the real problem is the API itself.
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  async function handleConnect() {
    setConnecting(true);
    setConnectMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/connect-gpu`, { method: 'POST' });
      const data = (await res.json()) as ConnectResult;
      setConnectMessage(data.message);
    } catch (err) {
      setConnectMessage(describeFetchError(err).message);
    } finally {
      setConnecting(false);
      fetchStatus();
    }
  }

  if (!status) return null;

  const connected = status.using_gpu_tunnel && status.reachable;

  if (connected) {
    return (
      <div className="flex w-fit animate-fade-in-up items-center gap-1.5 rounded-full border border-good/20 bg-good-soft px-3 py-1 text-xs font-semibold text-good">
        <Zap className="h-3.5 w-3.5" />
        GPU connected — fast mode
      </div>
    );
  }

  const message = status.using_gpu_tunnel
    ? "The GPU tunnel is configured but not responding right now — it's likely dropped (laptop sleep, network blip). Reconnect below, or check the Ronin connection and reload this page."
    : "Not connected to the Ronin GPU — extraction and negotiation will run on local hardware, which is much slower. Connect below for faster results.";

  return (
    <div
      className={cn(
        'flex animate-fade-in-up flex-col gap-2 rounded-xl border border-warning/30 bg-warning-soft px-4 py-3 text-sm text-ink'
      )}
    >
      <div className="flex items-start gap-2.5">
        <Zap className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
        <div className="flex-1">
          <p>{message}</p>
          <p className="mt-1 font-mono text-xs text-ink-secondary">
            Backend is currently pointed at: {status.ollama_host}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-3 pl-[26px]">
        <button
          type="button"
          onClick={handleConnect}
          disabled={connecting}
          className="inline-flex items-center gap-1.5 rounded-full border border-warning/40 bg-white px-3 py-1 text-xs font-semibold text-ink transition hover:bg-warning-soft disabled:cursor-not-allowed disabled:opacity-60"
        >
          {connecting ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Connecting… (up to 20s)
            </>
          ) : (
            <>
              <Zap className="h-3.5 w-3.5" />
              Connect to GPU
            </>
          )}
        </button>
        {connectMessage && !connecting && <span className="text-xs text-ink-secondary">{connectMessage}</span>}
      </div>
    </div>
  );
}
