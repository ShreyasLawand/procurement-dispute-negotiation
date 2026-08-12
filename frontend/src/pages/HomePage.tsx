import { FileText, Landmark, Scale, Upload, Users } from 'lucide-react';
import type { ComponentType } from 'react';
import { Link } from 'react-router-dom';
import { PageContainer } from '../components/layout/PageContainer';
import { pillButtonClasses } from '../lib/buttonStyles';

interface FeatureItem {
  icon: ComponentType<{ className?: string }>;
  badgeClass: string;
  title: string;
  description: string;
}

const FEATURES: FeatureItem[] = [
  {
    icon: Landmark,
    badgeClass: 'bg-[#dbe9fb] text-[#1d4e89]',
    title: 'Contracting Authority',
    description:
      'Defends the procurement decision within the bounds of the Procurement Act 2023 — legally defensible, evidence-based, and procedurally correct.',
  },
  {
    icon: Users,
    badgeClass: 'bg-[#fbe3d9] text-[#8a3f1c]',
    title: 'Aggrieved Bidder',
    description:
      'Challenges the decision in good faith, seeking transparency and a fair re-evaluation — willing to accept a well-reasoned outcome, not just a win.',
  },
  {
    icon: Scale,
    badgeClass: 'bg-[#d9ead3] text-[#1e5c33]',
    title: 'Court',
    description:
      'Assesses process compliance only — never who "deserves" to win — mirroring real UK judicial review of procurement decisions under s12 of the Act.',
  },
  {
    icon: FileText,
    badgeClass: 'bg-[#fdf0c8] text-[#7a5c05]',
    title: 'Summary',
    description:
      'A neutral, non-negotiating observer that explains the outcome in plain English — sticking points, concessions, and the reasoning behind the result.',
  },
];

const STEPS = [
  {
    title: 'Upload the case documents',
    description: 'Framework documents, evaluation reports, complaint letters — whatever describes the dispute.',
  },
  {
    title: 'Agents negotiate, live',
    description: 'The Contracting Authority and Bidder negotiate in rounds; the Court reviews compliance after each one.',
  },
  {
    title: 'See the outcome and why',
    description: 'A resolved outcome or an escalation to formal proceedings, with a plain-English summary throughout.',
  },
];

export function HomePage() {
  return (
    <div>
      <section className="bg-brand-soft">
        <PageContainer className="py-16 sm:py-20">
          <div className="max-w-2xl">
            <span className="inline-block rounded-full bg-white/60 px-3 py-1 text-xs font-bold uppercase tracking-wide text-brand-dark">
              Procurement with Purpose
            </span>
            <h1 className="mt-4 text-4xl font-black leading-tight text-ink sm:text-5xl">
              Multi-agent AI negotiation for procurement disputes
            </h1>
            <p className="mt-4 text-base leading-relaxed text-ink-secondary sm:text-lg">
              Upload a real dispute and watch a Contracting Authority, an Aggrieved Bidder, and a Court agent
              negotiate it round by round — grounded in the UK Procurement Act 2023 and modelled on the Technology
              and Construction Court.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/negotiate" className={pillButtonClasses('primary')}>
                <Upload className="h-4 w-4" />
                Run a live negotiation
              </Link>
              <Link to="/cases" className={pillButtonClasses('outline')}>
                Explore real case studies
              </Link>
            </div>
          </div>
        </PageContainer>
      </section>

      <PageContainer className="py-16">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">How it works</h2>
        <div className="mt-4 grid gap-6 sm:grid-cols-3">
          {STEPS.map((step, i) => (
            <div key={step.title} className="flex flex-col gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand text-sm font-black text-white">
                {i + 1}
              </span>
              <p className="font-semibold text-ink">{step.title}</p>
              <p className="text-sm leading-relaxed text-ink-secondary">{step.description}</p>
            </div>
          ))}
        </div>
      </PageContainer>

      <PageContainer className="pb-16">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">The four agents</h2>
        <div className="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="flex flex-col items-start gap-3">
              <span className={`flex h-12 w-12 items-center justify-center rounded-full ${feature.badgeClass}`}>
                <feature.icon className="h-5 w-5" />
              </span>
              <p className="font-semibold text-ink">{feature.title}</p>
              <p className="text-sm leading-relaxed text-ink-secondary">{feature.description}</p>
            </div>
          ))}
        </div>
      </PageContainer>

      <section className="border-t border-hairline bg-surface">
        <PageContainer className="py-12">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-muted">Grounded in real practice</h2>
          <p className="mt-3 max-w-3xl text-sm leading-relaxed text-ink-secondary">
            The simulation is built on the UK Procurement Act 2023 (value for money, public benefit, transparency,
            and integrity under s12), the 10-day standstill period and 30-day challenge window, and Fisher &amp;
            Ury's <em>Getting to Yes</em> negotiation framework — interests over positions, BATNA, and the zone of
            possible agreement. Case studies on the Cases tab are drawn from real UK procurement judgments,
            including the first-ever reported decision under the Procurement Act 2023.
          </p>
        </PageContainer>
      </section>
    </div>
  );
}
