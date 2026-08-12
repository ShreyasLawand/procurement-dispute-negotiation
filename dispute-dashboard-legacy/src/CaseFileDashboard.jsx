import React, { useState, useMemo, useRef } from "react";
import {
  Scale, Gavel, Building2, Users, Handshake, FileText, Upload, FolderOpen,
  BarChart3, Clock, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2,
  XCircle, ChevronRight, ChevronDown, X, ScrollText, Minus,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell,
} from "recharts";

/* ============================== DESIGN TOKENS ============================== */

const C = {
  appBg: "#D9D0B4",
  paper: "#FBF8F0",
  paperDim: "#F2ECDC",
  ink: "#241F18",
  inkMuted: "#7C7160",
  hairline: "#D3C79E",
  navy: "#2C4A63",
  navySoft: "#E1E8ED",
  ochre: "#93641F",
  ochreSoft: "#F1E4C8",
  oxblood: "#7A2A30",
  oxbloodSoft: "#F2DEDD",
  forest: "#3E6B49",
  forestSoft: "#DFEBDF",
};

const TONE = {
  navy: { fg: C.navy, soft: C.navySoft },
  ochre: { fg: C.ochre, soft: C.ochreSoft },
  oxblood: { fg: C.oxblood, soft: C.oxbloodSoft },
  forest: { fg: C.forest, soft: C.forestSoft },
  ink: { fg: C.ink, soft: C.paperDim },
};

const FONT_IMPORT =
  "@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');";

const displayFont = "'Newsreader', Georgia, serif";
const bodyFont = "'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif";
const monoFont = "'IBM Plex Mono', ui-monospace, Menlo, monospace";

/* ============================== DEMO DATA ============================== */
/* Real output pulled from the project's own negotiation_log_001.json and
   two of its batch_results runs (F21-002, before/after the Court verification fix). */

const DEMO_CASE = {"scenario": {"dispute_id": "F21-001", "title": "Scoring Methodology Challenge \u2014 Construction Framework", "description": "BuildRight Ltd submitted a bid for a \u00a32m construction framework and was ranked second, narrowly missing the framework by 1.2 points overall. \n\nDISPUTED CRITERION: Quality Criterion Q4 - 'Social Value: Community Benefit'\n- BuildRight Ltd's submission: 14 pages, including a detailed local employment plan, 3 named subcontractor partnerships, and a 5-year community investment schedule. Score awarded: 62/100.\n- Winning bidder (Ironclad Construction): 4 pages, general commitments to 'support local employment' with no named partnerships or schedule. Score awarded: 88/100.\n\nBuildRight Ltd alleges this scoring gap is a manifest error, since the published evaluation criteria (Framework Document, Section 4.3) state that Social Value scoring should be based on 'specificity, evidence, and named commitments.' BuildRight Ltd has formally requested the evaluator's scoring notes for Q4 for both bids.", "contract_value_gbp": 2000000.0, "dispute_type": "scoring_challenge", "procedural_stage": "standstill", "contracting_authority_name": "Fusion21", "bidder_name": "BuildRight Ltd"}, "round_number": 0, "max_rounds": 3, "ca_pre_negotiation": {"role": "contracting_authority", "interests": ["Legal defensibility", "Service continuity", "Reputational protection", "Cost efficiency", "Public value"], "goals": ["Defend the procurement decision within legal boundaries", "Ensure the best outcome for the public purse"], "batna": "Defending the procurement decision in the Technology and Construction Court (TCC) at a cost of \u00a350k+ in legal fees", "opening_position": "We acknowledge BuildRight Ltd's concerns regarding the scoring methodology for Q4, but we must ensure that our evaluation process is fair, transparent, and compliant with the Procurement Act 2023.", "legal_basis": ["Procurement Act 2023", "Regulation 32(1) - Evaluation criteria", "Regulation 33(2) - Scoring methodology"], "confidence_score": 0.8}, "bidder_pre_negotiation": {"role": "aggrieved_bidder", "interests": ["Winning the contract or securing a fair re-evaluation", "Transparency \u2014 understanding exactly why we scored as we did"], "goals": ["Re-evaluate Q4 scoring for BuildRight Ltd's bid, considering specificity, evidence, and named commitments", "Secure detailed feedback on evaluator's scoring notes for both bids"], "batna": "Pursuing a damages claim or formal proceedings in the Technology and Construction Court (TCC) if no agreement is reached", "opening_position": "We believe there was a manifest error in Q4 scoring, as our submission met all published criteria while Ironclad's did not. We request re-evaluation and detailed feedback on evaluator's notes.", "legal_basis": ["Public Contracts Regulations 2015 (PCR 2015), Regulation 72(2) - Standstill Period", "Framework Document, Section 4.3 - Social Value scoring criteria"], "confidence_score": 0.8}, "messages": [{"round_number": 1, "sender_role": "contracting_authority", "message": "BuildRight Ltd has alleged that the scoring gap for Quality Criterion Q4 - 'Social Value: Community Benefit' is a manifest error. I'd like to clarify whether BuildRight Ltd is contesting the specific evaluation criteria used in Section 4.3 of the Framework Document, or if they are questioning the application of those criteria to their own submission.", "proposal": null, "concession_made": null}, {"round_number": 1, "sender_role": "aggrieved_bidder", "message": "I'd like to clarify whether the Contracting Authority is suggesting that BuildRight Ltd's challenge is limited to the application of the criteria rather than the specific criteria used in Section 4.3 of the Framework Document. If so, I'd appreciate clarification on how the winning bidder's submission was deemed to meet the 'specificity, evidence, and named commitments' requirement when our own submission provided significantly more detail and evidence.", "proposal": null, "concession_made": null}, {"round_number": 2, "sender_role": "contracting_authority", "message": "I acknowledge BuildRight Ltd's concern regarding the scoring disparity for Quality Criterion Q4. To address their specific point, I'd like to clarify that while Ironclad Construction's submission may not have included named partnerships or a community investment schedule, it did provide evidence of past social value contributions and commitments to support local employment initiatives. However, upon reviewing our evaluation process, we can offer additional feedback on BuildRight Ltd's submission, highlighting areas where their detailed plan and named subcontractor partnerships demonstrate strong social value commitments.", "proposal": null, "concession_made": "We will provide a more detailed explanation of the evaluation rationale for both bids, including specific examples from each submission that support our scoring decisions."}, {"round_number": 2, "sender_role": "aggrieved_bidder", "message": "I appreciate the Contracting Authority's clarification on their evaluation process. However, I still have concerns regarding the scoring disparity for Quality Criterion Q4. It appears that the winning bidder's submission was awarded a higher score despite lacking specific evidence and named commitments as required by Section 4.3 of the Framework Document. In contrast, BuildRight Ltd provided extensive detail and evidence in our submission, including a 5-year community investment schedule and 3 named subcontractor partnerships. I would like to request that the Contracting Authority provide more information on how they interpreted 'general commitments' as meeting the 'specificity, evidence, and named commitments' requirement. Furthermore, I would appreciate it if the Contracting Authority could clarify why our submission was awarded a lower score despite providing significantly more detail and evidence than the winning bidder's submission.", "proposal": null, "concession_made": null}], "compliance_checks": [{"round_number": 1, "process_followed": true, "manifest_error_found": false, "applicable_provisions": ["Section 4.3 of the Framework Document", "Procurement Act 2023 s12"], "reasoning": "At this stage, it appears that both parties are seeking clarification on the evaluation criteria and its application. The Contracting Authority has not yet provided evidence of a manifest error or a deviation from the published methodology.", "recommended_action": "continue negotiation", "deadlock": false}, {"round_number": 2, "process_followed": false, "manifest_error_found": true, "applicable_provisions": ["Section 4.3 of the Framework Document"], "reasoning": "The Contracting Authority's evaluation process appears to have been inconsistent in its application, as evidenced by the scoring disparity for Quality Criterion Q4. The winning bidder's submission was awarded a higher score despite lacking specific evidence and named commitments, while BuildRight Ltd's submission provided extensive detail and evidence.", "recommended_action": "re-evaluation", "deadlock": false}], "resolved": true, "resolution_outcome": "re-evaluation", "adjudicated": true, "ca_win_statement": null, "bidder_win_statement": null, "summary": {"key_sticking_points": ["Scoring disparity for Quality Criterion Q4: Social Value - Community Benefit", "Application of evaluation criteria in Section 4.3 of the Framework Document"], "concessions_summary": "The Contracting Authority offered to provide a more detailed explanation of their evaluation rationale, including specific examples from each submission that support their scoring decisions.", "court_reasoning_summary": "The Court concluded that there was a manifest error in the Contracting Authority's evaluation process due to the inconsistent application of criteria. The winning bidder's submission received a higher score despite lacking required evidence and commitments, while BuildRight Ltd's submission provided more detail and evidence.", "likely_next_steps": "Re-evaluation of both bids is recommended by the Court, as the current scoring disparity appears to be unjustified.", "plain_english_summary": "The dispute centered on how the Contracting Authority evaluated the bidders' social value commitments. The Court found that the evaluation process was inconsistent and resulted in an unfair advantage for the winning bidder. As a result, the Court recommended re-evaluating both bids to ensure fairness."}};

const DEMO_BATCH_BEFORE = {"scenario_id": "F21-002", "scenario_title": "Mathematical Scoring Error \u2014 Facilities Management Contract", "n_runs_requested": 8, "n_runs_successful": 8, "n_runs_failed": 0, "max_rounds": 5, "timestamp": "20260726_163753", "metrics": {"agreement_rate": 0.625, "deadlock_rate": 0.375, "manifest_error_detection_rate": 0.625, "average_rounds_to_conclusion": 2.88, "average_duration_seconds": 38.1, "outcome_distribution": {"deadlock - max rounds reached, escalate to formal proceedings": 3, "re-evaluation": 5}}, "individual_runs": [{"run_number": 1, "resolved": false, "outcome": "deadlock - max rounds reached, escalate to formal proceedings", "rounds_taken": 5, "manifest_error_found_any_round": false, "manifest_error_rounds": [], "process_not_followed_any_round": false, "duration_seconds": 58.2, "error": null}, {"run_number": 2, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 22.7, "error": null}, {"run_number": 3, "resolved": false, "outcome": "deadlock - max rounds reached, escalate to formal proceedings", "rounds_taken": 5, "manifest_error_found_any_round": false, "manifest_error_rounds": [], "process_not_followed_any_round": false, "duration_seconds": 54.0, "error": null}, {"run_number": 4, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 2, "manifest_error_found_any_round": true, "manifest_error_rounds": [2], "process_not_followed_any_round": false, "duration_seconds": 31.5, "error": null}, {"run_number": 5, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 2, "manifest_error_found_any_round": true, "manifest_error_rounds": [2], "process_not_followed_any_round": false, "duration_seconds": 29.4, "error": null}, {"run_number": 6, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 21.4, "error": null}, {"run_number": 7, "resolved": false, "outcome": "deadlock - max rounds reached, escalate to formal proceedings", "rounds_taken": 5, "manifest_error_found_any_round": false, "manifest_error_rounds": [], "process_not_followed_any_round": false, "duration_seconds": 57.9, "error": null}, {"run_number": 8, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 2, "manifest_error_found_any_round": true, "manifest_error_rounds": [2], "process_not_followed_any_round": false, "duration_seconds": 29.6, "error": null}]};

const DEMO_BATCH_AFTER = {"scenario_id": "F21-002", "scenario_title": "Mathematical Scoring Error \u2014 Facilities Management Contract", "n_runs_requested": 8, "n_runs_successful": 8, "n_runs_failed": 0, "max_rounds": 5, "timestamp": "20260726_155725", "metrics": {"agreement_rate": 1.0, "deadlock_rate": 0.0, "manifest_error_detection_rate": 1.0, "average_rounds_to_conclusion": 1.25, "average_duration_seconds": 29.1, "outcome_distribution": {"re-evaluation": 8}}, "individual_runs": [{"run_number": 1, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 2, "manifest_error_found_any_round": true, "manifest_error_rounds": [2], "process_not_followed_any_round": true, "duration_seconds": 71.1, "error": null}, {"run_number": 2, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 22.6, "error": null}, {"run_number": 3, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 22.8, "error": null}, {"run_number": 4, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 22.8, "error": null}, {"run_number": 5, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 21.7, "error": null}, {"run_number": 6, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 21.1, "error": null}, {"run_number": 7, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 1, "manifest_error_found_any_round": true, "manifest_error_rounds": [1], "process_not_followed_any_round": true, "duration_seconds": 21.7, "error": null}, {"run_number": 8, "resolved": true, "outcome": "re-evaluation", "rounds_taken": 2, "manifest_error_found_any_round": true, "manifest_error_rounds": [2], "process_not_followed_any_round": false, "duration_seconds": 28.9, "error": null}]};

/* ============================== HELPERS ============================== */

const fmtGBP = (n) =>
  "£" + Number(n).toLocaleString("en-GB", { maximumFractionDigits: 0 });

const fmtPct = (x) => Math.round(x * 100) + "%";

const ROLE_META = {
  contracting_authority: { label: "Contracting Authority", icon: Building2, tone: "navy" },
  aggrieved_bidder: { label: "Aggrieved Bidder", icon: Users, tone: "ochre" },
  court: { label: "Court", icon: Scale, tone: "oxblood" },
};

function actionTone(action) {
  const a = (action || "").toLowerCase();
  if (a.includes("deadlock")) return "oxblood";
  if (a.includes("continue")) return "ochre";
  return "forest";
}

function shortOutcome(outcome) {
  const o = (outcome || "").toLowerCase();
  if (o.includes("deadlock")) return "Deadlock — Escalate to TCC";
  if (o.includes("re-evaluation")) return "Re-evaluation Ordered";
  if (o.includes("no remedy")) return "No Remedy — Decision Stands";
  if (o.includes("damages")) return "Damages Awarded";
  return outcome || "Unresolved";
}

function fmtBatchTimestamp(ts) {
  if (!ts || ts.length < 15) return ts || "—";
  const y = ts.slice(0, 4), mo = ts.slice(4, 6), d = ts.slice(6, 8);
  const h = ts.slice(9, 11), mi = ts.slice(11, 13);
  const months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${d} ${months[parseInt(mo, 10)] || mo} ${y}, ${h}:${mi}`;
}

/* ============================== PRIMITIVES ============================== */

function Chip({ children, tone = "ink", prefix }) {
  const t = TONE[tone] || TONE.ink;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        fontFamily: monoFont,
        fontSize: 11,
        letterSpacing: "0.02em",
        color: t.fg,
        background: t.soft,
        border: `1px solid ${t.fg}33`,
        borderRadius: 999,
        padding: "3px 10px",
        lineHeight: 1.4,
      }}
    >
      {prefix ? <span style={{ opacity: 0.6 }}>{prefix}</span> : null}
      {children}
    </span>
  );
}

function SectionEyebrow({ children, tone = "ink" }) {
  const t = TONE[tone] || TONE.ink;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "6px 0 18px" }}>
      <div style={{ flex: 1, height: 1, background: C.hairline }} />
      <span
        style={{
          fontFamily: monoFont,
          fontSize: 11,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: t.fg,
          fontWeight: 600,
          whiteSpace: "nowrap",
        }}
      >
        {children}
      </span>
      <div style={{ flex: 1, height: 1, background: C.hairline }} />
    </div>
  );
}

function Stamp({ children, tone = "oxblood", rotate = -3, size = 13 }) {
  const t = TONE[tone] || TONE.oxblood;
  return (
    <span
      style={{
        display: "inline-block",
        transform: `rotate(${rotate}deg)`,
        border: `2.5px solid ${t.fg}`,
        outline: `1px solid ${t.fg}`,
        outlineOffset: 2,
        borderRadius: 6,
        padding: "5px 12px",
        fontFamily: monoFont,
        fontWeight: 700,
        fontSize: size,
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        color: t.fg,
        textShadow: `0 0 1px ${t.fg}55`,
        background: `${t.fg}0d`,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
  );
}

function ConfidenceMeter({ value, tone }) {
  const t = TONE[tone] || TONE.ink;
  const pct = Math.round(value * 100);
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontFamily: monoFont, fontSize: 10.5, letterSpacing: "0.1em", textTransform: "uppercase", color: C.inkMuted }}>
          Stated confidence
        </span>
        <span style={{ fontFamily: monoFont, fontSize: 11.5, fontWeight: 600, color: t.fg }}>{pct}%</span>
      </div>
      <div style={{ height: 6, borderRadius: 999, background: `${t.fg}22`, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: t.fg, borderRadius: 999 }} />
      </div>
    </div>
  );
}

/* Folder-tab navigation */
function FolderTab({ active, onClick, icon: Icon, children }) {
  return (
    <button
      onClick={onClick}
      style={{
        position: "relative",
        border: "none",
        cursor: "pointer",
        fontFamily: monoFont,
        fontSize: 12.5,
        fontWeight: 600,
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        padding: "12px 26px 14px",
        clipPath: "polygon(6% 0%, 94% 0%, 100% 100%, 0% 100%)",
        background: active ? C.paper : C.paperDim,
        color: active ? C.ink : C.inkMuted,
        marginRight: -14,
        zIndex: active ? 2 : 1,
        boxShadow: active ? "0 -2px 6px rgba(0,0,0,0.06)" : "none",
        transition: "color 0.15s ease",
        display: "flex",
        alignItems: "center",
        gap: 7,
      }}
    >
      <Icon size={14} strokeWidth={2.25} />
      {children}
    </button>
  );
}

/* ============================== CASE FILE VIEW ============================== */

function PreNegotiationCard({ statement, orgName, tone, roleKey }) {
  const meta = ROLE_META[roleKey];
  const Icon = meta.icon;
  const t = TONE[tone];
  return (
    <div
      style={{
        background: C.paper,
        border: `1px solid ${C.hairline}`,
        borderTop: `4px solid ${t.fg}`,
        borderRadius: "4px 4px 10px 10px",
        padding: 20,
        flex: 1,
        minWidth: 280,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
        <Icon size={17} color={t.fg} strokeWidth={2.25} />
        <div>
          <div style={{ fontFamily: displayFont, fontSize: 17, fontWeight: 600, color: C.ink, lineHeight: 1.2 }}>
            {meta.label}
          </div>
          <div style={{ fontFamily: monoFont, fontSize: 10.5, color: C.inkMuted, letterSpacing: "0.04em" }}>
            {orgName}
          </div>
        </div>
      </div>

      <div style={{ fontFamily: bodyFont, fontSize: 13.5, color: C.ink, lineHeight: 1.55, marginBottom: 14, fontStyle: "italic" }}>
        “{statement.opening_position}”
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontFamily: monoFont, fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", color: C.inkMuted, marginBottom: 5 }}>
          BATNA
        </div>
        <div style={{ fontFamily: bodyFont, fontSize: 12.5, color: C.ink, lineHeight: 1.4 }}>{statement.batna}</div>
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontFamily: monoFont, fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", color: C.inkMuted, marginBottom: 6 }}>
          Interests
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
          {statement.interests.map((it, i) => (
            <Chip key={i} tone={tone}>{it}</Chip>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontFamily: monoFont, fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", color: C.inkMuted, marginBottom: 6 }}>
          Legal basis
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {statement.legal_basis.map((lb, i) => (
            <div key={i} style={{ fontFamily: bodyFont, fontSize: 12, color: C.ink, display: "flex", gap: 6 }}>
              <span style={{ color: t.fg, fontFamily: monoFont }}>§</span>
              <span>{lb}</span>
            </div>
          ))}
        </div>
      </div>

      <ConfidenceMeter value={statement.confidence_score} tone={tone} />
    </div>
  );
}

function MessageBubble({ msg, side, tone, speaker }) {
  const t = TONE[tone];
  return (
    <div style={{ display: "flex", justifyContent: side === "left" ? "flex-start" : "flex-end", marginBottom: 10 }}>
      <div
        style={{
          maxWidth: "78%",
          background: C.paper,
          borderRadius: 10,
          padding: "14px 16px",
          borderLeft: side === "left" ? `4px solid ${t.fg}` : `1px solid ${C.hairline}`,
          borderRight: side === "right" ? `4px solid ${t.fg}` : `1px solid ${C.hairline}`,
          borderTop: `1px solid ${C.hairline}`,
          borderBottom: `1px solid ${C.hairline}`,
        }}
      >
        <div
          style={{
            fontFamily: monoFont,
            fontSize: 10.5,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: t.fg,
            fontWeight: 600,
            marginBottom: 6,
          }}
        >
          {speaker}
        </div>
        <div style={{ fontFamily: bodyFont, fontSize: 13.5, color: C.ink, lineHeight: 1.55 }}>{msg.message}</div>

        {(msg.proposal || msg.concession_made) && (
          <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 6 }}>
            {msg.proposal && (
              <div style={{ display: "flex", gap: 6, fontSize: 12, alignItems: "flex-start" }}>
                <FileText size={13} color={t.fg} style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ fontFamily: bodyFont, color: C.ink }}>
                  <b style={{ fontFamily: monoFont, fontSize: 10.5, textTransform: "uppercase", color: t.fg }}>Proposal — </b>
                  <i>{msg.proposal}</i>
                </span>
              </div>
            )}
            {msg.concession_made && (
              <div style={{ display: "flex", gap: 6, fontSize: 12, alignItems: "flex-start" }}>
                <Handshake size={13} color={t.fg} style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ fontFamily: bodyFont, color: C.ink }}>
                  <b style={{ fontFamily: monoFont, fontSize: 10.5, textTransform: "uppercase", color: t.fg }}>Concession — </b>
                  <i>{msg.concession_made}</i>
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function CourtCard({ assessment }) {
  return (
    <div
      style={{
        background: C.paper,
        border: `1px solid ${C.hairline}`,
        borderRadius: 10,
        padding: "16px 20px",
        margin: "6px auto 22px",
        maxWidth: "92%",
        boxShadow: "0 1px 0 rgba(0,0,0,0.03)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <Scale size={16} color={C.oxblood} strokeWidth={2.25} />
        <span style={{ fontFamily: monoFont, fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", color: C.oxblood, fontWeight: 700 }}>
          Court Assessment — Round {assessment.round_number}
        </span>
      </div>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 12 }}>
        <Stamp tone={assessment.process_followed ? "forest" : "oxblood"} rotate={-2}>
          Process {assessment.process_followed ? "Followed" : "Not Followed"}
        </Stamp>
        <Stamp tone={assessment.manifest_error_found ? "oxblood" : "forest"} rotate={2}>
          Manifest Error {assessment.manifest_error_found ? "Found" : "Not Found"}
        </Stamp>
      </div>

      <p style={{ fontFamily: bodyFont, fontSize: 13, color: C.ink, lineHeight: 1.6, margin: "0 0 12px" }}>
        {assessment.reasoning}
      </p>

      {assessment.applicable_provisions?.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
          {assessment.applicable_provisions.map((p, i) => (
            <Chip key={i} tone="ink" prefix="§">{p}</Chip>
          ))}
        </div>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8, borderTop: `1px dashed ${C.hairline}`, paddingTop: 10 }}>
        <span style={{ fontFamily: monoFont, fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", color: C.inkMuted }}>
          Recommended action
        </span>
        <span
          style={{
            fontFamily: displayFont,
            fontWeight: 600,
            fontSize: 14.5,
            color: TONE[actionTone(assessment.recommended_action)].fg,
            textTransform: "capitalize",
          }}
        >
          {assessment.recommended_action}
        </span>
      </div>
    </div>
  );
}

function OutcomeRibbon({ resolved, outcome }) {
  const tone = resolved ? (outcome || "").toLowerCase().includes("deadlock") ? "oxblood" : "forest" : "oxblood";
  const t = TONE[tone];
  return (
    <div
      style={{
        margin: "8px 0 32px",
        padding: "18px 24px",
        textAlign: "center",
        background: t.soft,
        border: `1px solid ${t.fg}44`,
        borderRadius: 8,
      }}
    >
      <div style={{ fontFamily: monoFont, fontSize: 10.5, letterSpacing: "0.14em", textTransform: "uppercase", color: t.fg, marginBottom: 6 }}>
        {resolved ? "Case Resolved" : "No Agreement Reached"}
      </div>
      <div style={{ fontFamily: displayFont, fontSize: 24, fontWeight: 600, color: C.ink }}>
        {shortOutcome(outcome)}
      </div>
    </div>
  );
}

function WinCard({ ws, tone, roleKey }) {
  const meta = ROLE_META[roleKey];
  const Icon = meta.icon;
  const t = TONE[tone];
  return (
    <div style={{ flex: 1, minWidth: 260, background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: 18 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 10 }}>
        <Icon size={15} color={t.fg} />
        <span style={{ fontFamily: monoFont, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.06em", color: t.fg, fontWeight: 700 }}>
          {meta.label}
        </span>
      </div>
      <div style={{ fontFamily: bodyFont, fontStyle: "italic", fontSize: 13, color: C.ink, lineHeight: 1.5, marginBottom: 10 }}>
        “{ws.win_statement}”
      </div>
      <Chip tone={tone}>{ws.outcome_relative_to_batna}</Chip>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 10 }}>
        {ws.what_was_achieved.map((a, i) => (
          <span key={i} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, fontFamily: bodyFont, color: C.ink }}>
            <CheckCircle2 size={12} color={C.forest} /> {a}
          </span>
        ))}
      </div>
    </div>
  );
}

function CaseFileView() {
  const [data, setData] = useState(DEMO_CASE);
  const [error, setError] = useState(null);
  const fileRef = useRef(null);

  const rounds = useMemo(() => {
    if (!data) return [];
    const nums = [...new Set(data.messages.map((m) => m.round_number))].sort((a, b) => a - b);
    return nums.map((n) => ({
      number: n,
      messages: data.messages.filter((m) => m.round_number === n),
      check: data.compliance_checks.find((c) => c.round_number === n),
    }));
  }, [data]);

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target.result);
        if (!parsed.scenario || !parsed.messages) {
          if (parsed.metrics && parsed.individual_runs) {
            setError("This looks like a batch summary file, not a case file. Switch to the Docket Analytics tab to load it there.");
          } else {
            setError("This JSON doesn't match a negotiation case file — it should have 'scenario' and 'messages' fields.");
          }
          return;
        }
        setData(parsed);
        setError(null);
      } catch {
        setError("Couldn't parse that file as JSON. Check it's a valid negotiation log.");
      }
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  const scenario = data?.scenario;

  return (
    <div>
      {/* Upload bar */}
      <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginBottom: 18, flexWrap: "wrap" }}>
        <button
          onClick={() => fileRef.current?.click()}
          style={btnStyle(false)}
        >
          <Upload size={13} /> Load case file (.json)
        </button>
        <button onClick={() => { setData(DEMO_CASE); setError(null); }} style={btnStyle(true)}>
          <FolderOpen size={13} /> Sample case
        </button>
        <input ref={fileRef} type="file" accept=".json,application/json" onChange={handleFile} style={{ display: "none" }} />
      </div>

      {error && (
        <div style={{ marginBottom: 18, padding: "12px 16px", background: C.oxbloodSoft, border: `1px solid ${C.oxblood}44`, borderRadius: 8, display: "flex", gap: 8, alignItems: "flex-start" }}>
          <AlertTriangle size={15} color={C.oxblood} style={{ marginTop: 1, flexShrink: 0 }} />
          <span style={{ fontFamily: bodyFont, fontSize: 13, color: C.ink }}>{error}</span>
        </div>
      )}

      {!scenario ? (
        <EmptyState
          icon={ScrollText}
          title="No case file loaded"
          body="Upload a negotiation_log JSON produced by the orchestrator, or load the sample case to see the format."
        />
      ) : (
        <>
          {/* Case header */}
          <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: "20px 24px", marginBottom: 26 }}>
            <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 12, marginBottom: 10 }}>
              <div style={{ fontFamily: monoFont, fontSize: 11.5, letterSpacing: "0.06em", color: C.inkMuted }}>
                CASE {scenario.dispute_id} · {scenario.procedural_stage?.toUpperCase()}
              </div>
              <Chip tone="ink">{scenario.dispute_type.replace(/_/g, " ")}</Chip>
            </div>
            <h1 style={{ fontFamily: displayFont, fontWeight: 600, fontSize: 28, color: C.ink, margin: "0 0 12px", lineHeight: 1.15 }}>
              {scenario.title}
            </h1>
            <p style={{ fontFamily: bodyFont, fontSize: 13.5, color: C.ink, lineHeight: 1.6, margin: "0 0 14px", whiteSpace: "pre-line" }}>
              {scenario.description}
            </p>
            <div style={{ display: "flex", gap: 22, flexWrap: "wrap", borderTop: `1px dashed ${C.hairline}`, paddingTop: 12 }}>
              <MetaField label="Contract value" value={fmtGBP(scenario.contract_value_gbp)} />
              <MetaField label="Contracting authority" value={scenario.contracting_authority_name} />
              <MetaField label="Aggrieved bidder" value={scenario.bidder_name} />
              <MetaField label="Rounds" value={`${rounds.length} of max ${data.max_rounds}`} />
            </div>
          </div>

          {/* Pre-negotiation */}
          <SectionEyebrow>Pre-Negotiation Positions</SectionEyebrow>
          <div style={{ display: "flex", gap: 18, flexWrap: "wrap", marginBottom: 34 }}>
            {data.ca_pre_negotiation && (
              <PreNegotiationCard
                statement={data.ca_pre_negotiation}
                orgName={scenario.contracting_authority_name}
                tone="navy"
                roleKey="contracting_authority"
              />
            )}
            {data.bidder_pre_negotiation && (
              <PreNegotiationCard
                statement={data.bidder_pre_negotiation}
                orgName={scenario.bidder_name}
                tone="ochre"
                roleKey="aggrieved_bidder"
              />
            )}
          </div>

          {/* Transcript */}
          <SectionEyebrow>Negotiation Transcript</SectionEyebrow>
          {rounds.map((r) => (
            <div key={r.number} style={{ marginBottom: 8 }}>
              <div style={{ textAlign: "center", margin: "18px 0 14px" }}>
                <span style={{ fontFamily: monoFont, fontSize: 11, letterSpacing: "0.18em", textTransform: "uppercase", color: C.inkMuted }}>
                  — Round {r.number} of {data.max_rounds} —
                </span>
              </div>
              {r.messages.map((m, i) => {
                const meta = ROLE_META[m.sender_role];
                const side = m.sender_role === "contracting_authority" ? "left" : "right";
                return (
                  <MessageBubble
                    key={i}
                    msg={m}
                    side={side}
                    tone={meta.tone}
                    speaker={`${meta.label} · ${side === "left" ? scenario.contracting_authority_name : scenario.bidder_name}`}
                  />
                );
              })}
              {r.check && <CourtCard assessment={r.check} />}
            </div>
          ))}

          <OutcomeRibbon resolved={data.resolved} outcome={data.resolution_outcome} />

          {/* Summary */}
          {data.summary && (
            <>
              <SectionEyebrow>Post-Negotiation Summary</SectionEyebrow>
              <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: 24, marginBottom: 28 }}>
                <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
                  <span style={{ fontFamily: displayFont, fontSize: 34, color: C.oxblood, lineHeight: 0.6, opacity: 0.35 }}>“</span>
                  <p style={{ fontFamily: displayFont, fontStyle: "italic", fontSize: 17, color: C.ink, lineHeight: 1.55, margin: 0 }}>
                    {data.summary.plain_english_summary}
                  </p>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                  <div>
                    <div style={labelStyle}>Key sticking points</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 6 }}>
                      {data.summary.key_sticking_points.map((p, i) => (
                        <div key={i} style={{ display: "flex", gap: 8, fontFamily: bodyFont, fontSize: 13, color: C.ink, lineHeight: 1.45 }}>
                          <span style={{ color: C.oxblood }}>—</span>
                          <span>{p}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    <div>
                      <div style={labelStyle}>Concessions</div>
                      <p style={valueStyle}>{data.summary.concessions_summary}</p>
                    </div>
                    <div>
                      <div style={labelStyle}>Court reasoning</div>
                      <p style={valueStyle}>{data.summary.court_reasoning_summary}</p>
                    </div>
                    <div>
                      <div style={labelStyle}>Likely next steps</div>
                      <p style={valueStyle}>{data.summary.likely_next_steps}</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {(data.ca_win_statement || data.bidder_win_statement) && (
            <>
              <SectionEyebrow>Reflections</SectionEyebrow>
              <div style={{ display: "flex", gap: 18, flexWrap: "wrap", marginBottom: 10 }}>
                {data.ca_win_statement && <WinCard ws={data.ca_win_statement} tone="navy" roleKey="contracting_authority" />}
                {data.bidder_win_statement && <WinCard ws={data.bidder_win_statement} tone="ochre" roleKey="aggrieved_bidder" />}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

function MetaField({ label, value }) {
  return (
    <div>
      <div style={{ fontFamily: monoFont, fontSize: 9.5, letterSpacing: "0.1em", textTransform: "uppercase", color: C.inkMuted, marginBottom: 3 }}>
        {label}
      </div>
      <div style={{ fontFamily: bodyFont, fontSize: 13, fontWeight: 600, color: C.ink }}>{value}</div>
    </div>
  );
}

const labelStyle = {
  fontFamily: monoFont,
  fontSize: 10,
  letterSpacing: "0.1em",
  textTransform: "uppercase",
  color: C.inkMuted,
};
const valueStyle = { fontFamily: bodyFont, fontSize: 12.5, color: C.ink, lineHeight: 1.5, margin: "4px 0 0" };

function btnStyle(muted) {
  return {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    fontFamily: monoFont,
    fontSize: 11.5,
    letterSpacing: "0.04em",
    textTransform: "uppercase",
    fontWeight: 600,
    color: muted ? C.inkMuted : C.paper,
    background: muted ? "transparent" : C.ink,
    border: `1px solid ${muted ? C.hairline : C.ink}`,
    borderRadius: 6,
    padding: "8px 14px",
    cursor: "pointer",
  };
}

function EmptyState({ icon: Icon, title, body }) {
  return (
    <div style={{ textAlign: "center", padding: "60px 20px", background: C.paper, border: `1px dashed ${C.hairline}`, borderRadius: 10 }}>
      <Icon size={28} color={C.inkMuted} style={{ marginBottom: 12 }} />
      <div style={{ fontFamily: displayFont, fontSize: 19, color: C.ink, marginBottom: 6 }}>{title}</div>
      <div style={{ fontFamily: bodyFont, fontSize: 13, color: C.inkMuted, maxWidth: 420, margin: "0 auto" }}>{body}</div>
    </div>
  );
}

/* ============================== DOCKET ANALYTICS VIEW ============================== */

const BATCH_PALETTE = [C.navy, C.ochre, C.oxblood, C.forest];

const METRIC_DEFS = [
  { key: "agreement_rate", label: "Agreement Rate", fmt: fmtPct, higherBetter: true },
  { key: "manifest_error_detection_rate", label: "Manifest Error Detection", fmt: fmtPct, higherBetter: true },
  { key: "deadlock_rate", label: "Deadlock Rate", fmt: fmtPct, higherBetter: false },
  { key: "average_rounds_to_conclusion", label: "Avg Rounds to Conclusion", fmt: (v) => v.toFixed(2), higherBetter: false },
  { key: "average_duration_seconds", label: "Avg Duration", fmt: (v) => v.toFixed(1) + "s", higherBetter: false },
];

function KpiCard({ def, batches }) {
  const baseline = batches[0]?.data.metrics[def.key];
  return (
    <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: "14px 16px", flex: 1, minWidth: 168 }}>
      <div style={{ fontFamily: monoFont, fontSize: 10, letterSpacing: "0.08em", textTransform: "uppercase", color: C.inkMuted, marginBottom: 10 }}>
        {def.label}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {batches.map((b, i) => {
          const val = b.data.metrics[def.key];
          const delta = i === 0 || baseline === undefined ? null : val - baseline;
          const improved = delta !== null && (def.higherBetter ? delta > 0 : delta < 0);
          const worsened = delta !== null && (def.higherBetter ? delta < 0 : delta > 0);
          return (
            <div key={i} style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: 999, background: BATCH_PALETTE[i % 4], flexShrink: 0 }} />
              <span style={{ fontFamily: displayFont, fontSize: 20, fontWeight: 600, color: C.ink }}>{def.fmt(val)}</span>
              {delta !== null && Math.abs(delta) > 0.0005 && (
                <span style={{ display: "flex", alignItems: "center", gap: 2, fontFamily: monoFont, fontSize: 11, color: improved ? C.forest : worsened ? C.oxblood : C.inkMuted }}>
                  {delta > 0 ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                  {def.fmt(Math.abs(delta))}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function BatchTag({ batch, index, active, onClick, onRemove }) {
  const color = BATCH_PALETTE[index % 4];
  return (
    <button
      onClick={onClick}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        background: active ? C.paper : "transparent",
        border: `1px solid ${active ? color : C.hairline}`,
        borderRadius: 8,
        padding: "8px 12px",
        cursor: "pointer",
        textAlign: "left",
      }}
    >
      <span style={{ width: 9, height: 9, borderRadius: 999, background: color, flexShrink: 0 }} />
      <div>
        <div style={{ fontFamily: monoFont, fontSize: 11, fontWeight: 600, color: C.ink }}>{batch.label}</div>
        <div style={{ fontFamily: monoFont, fontSize: 9.5, color: C.inkMuted }}>{fmtBatchTimestamp(batch.data.timestamp)}</div>
      </div>
      {onRemove && (
        <span
          onClick={(e) => { e.stopPropagation(); onRemove(); }}
          style={{ marginLeft: 6, color: C.inkMuted, display: "flex" }}
        >
          <X size={12} />
        </span>
      )}
    </button>
  );
}

function CustomTooltip({ active, payload, label, suffix }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 6, padding: "8px 10px", fontFamily: monoFont, fontSize: 11 }}>
      <div style={{ color: C.inkMuted, marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color }}>
          {p.name}: {typeof p.value === "number" ? p.value.toFixed(1) : p.value}{suffix || ""}
        </div>
      ))}
    </div>
  );
}

function DocketAnalyticsView() {
  const [batches, setBatches] = useState([
    { label: "Before Fix", data: DEMO_BATCH_BEFORE },
    { label: "After Fix", data: DEMO_BATCH_AFTER },
  ]);
  const [activeIdx, setActiveIdx] = useState(0);
  const [error, setError] = useState(null);
  const fileRef = useRef(null);

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target.result);
        if (!parsed.metrics || !parsed.individual_runs) {
          if (parsed.scenario && parsed.messages) {
            setError("This looks like a single case file, not a batch summary. Switch to the Case File tab to load it there.");
          } else {
            setError("This JSON doesn't match a batch_summary file — it should have 'metrics' and 'individual_runs' fields.");
          }
          return;
        }
        setBatches((prev) => [...prev, { label: file.name.replace(/\.json$/i, ""), data: parsed }].slice(0, 4));
        setError(null);
      } catch {
        setError("Couldn't parse that file as JSON.");
      }
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  const rateData = [
    { metric: "Agreement" },
    { metric: "Manifest Error" },
    { metric: "Deadlock" },
  ].map((row, i) => {
    const keys = ["agreement_rate", "manifest_error_detection_rate", "deadlock_rate"];
    const out = { metric: row.metric };
    batches.forEach((b) => { out[b.label] = Math.round(b.data.metrics[keys[i]] * 100); });
    return out;
  });

  const roundsData = batches.map((b) => ({ name: b.label, value: b.data.metrics.average_rounds_to_conclusion }));
  const durationData = batches.map((b) => ({ name: b.label, value: b.data.metrics.average_duration_seconds }));

  const outcomeKeys = useMemo(() => {
    const set = new Set();
    batches.forEach((b) => Object.keys(b.data.metrics.outcome_distribution || {}).forEach((k) => set.add(k)));
    return [...set];
  }, [batches]);

  const outcomeData = outcomeKeys.map((k) => {
    const out = { outcome: shortOutcome(k).replace(" — ", " ") };
    batches.forEach((b) => { out[b.label] = b.data.metrics.outcome_distribution?.[k] || 0; });
    return out;
  });

  const activeBatch = batches[activeIdx];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginBottom: 18, flexWrap: "wrap" }}>
        <button onClick={() => fileRef.current?.click()} style={btnStyle(false)}>
          <Upload size={13} /> Add batch file (.json)
        </button>
        <button
          onClick={() => { setBatches([{ label: "Before Fix", data: DEMO_BATCH_BEFORE }, { label: "After Fix", data: DEMO_BATCH_AFTER }]); setActiveIdx(0); setError(null); }}
          style={btnStyle(true)}
        >
          <FolderOpen size={13} /> Sample dockets
        </button>
        <input ref={fileRef} type="file" accept=".json,application/json" onChange={handleFile} style={{ display: "none" }} />
      </div>

      {error && (
        <div style={{ marginBottom: 18, padding: "12px 16px", background: C.oxbloodSoft, border: `1px solid ${C.oxblood}44`, borderRadius: 8, display: "flex", gap: 8, alignItems: "flex-start" }}>
          <AlertTriangle size={15} color={C.oxblood} style={{ marginTop: 1, flexShrink: 0 }} />
          <span style={{ fontFamily: bodyFont, fontSize: 13, color: C.ink }}>{error}</span>
        </div>
      )}

      {batches.length === 0 ? (
        <EmptyState icon={BarChart3} title="No dockets loaded" body="Upload one or more batch_summary.json files from a batch evaluation run, or load the sample dockets." />
      ) : (
        <>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 22 }}>
            {batches.map((b, i) => (
              <BatchTag
                key={i}
                batch={b}
                index={i}
                active={i === activeIdx}
                onClick={() => setActiveIdx(i)}
                onRemove={batches.length > 1 ? () => { setBatches((prev) => prev.filter((_, j) => j !== i)); setActiveIdx(0); } : null}
              />
            ))}
          </div>

          <div style={{ fontFamily: bodyFont, fontSize: 12.5, color: C.inkMuted, marginBottom: 20 }}>
            {activeBatch.data.scenario_title} · {activeBatch.data.n_runs_successful}/{activeBatch.data.n_runs_requested} runs · max {activeBatch.data.max_rounds} rounds
          </div>

          <SectionEyebrow>Key Metrics</SectionEyebrow>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 30 }}>
            {METRIC_DEFS.map((def) => (
              <KpiCard key={def.key} def={def} batches={batches} />
            ))}
          </div>

          <SectionEyebrow>Compliance & Detection Rates</SectionEyebrow>
          <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: "18px 18px 6px", marginBottom: 30, height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rateData} margin={{ top: 4, right: 8, left: -12, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={C.hairline} vertical={false} />
                <XAxis dataKey="metric" tick={{ fontFamily: monoFont, fontSize: 11, fill: C.inkMuted }} axisLine={{ stroke: C.hairline }} tickLine={false} />
                <YAxis unit="%" tick={{ fontFamily: monoFont, fontSize: 10, fill: C.inkMuted }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip suffix="%" />} cursor={{ fill: C.paperDim }} />
                <Legend wrapperStyle={{ fontFamily: monoFont, fontSize: 11 }} />
                {batches.map((b, i) => (
                  <Bar key={b.label} dataKey={b.label} fill={BATCH_PALETTE[i % 4]} radius={[4, 4, 0, 0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          <SectionEyebrow>Resolution Speed</SectionEyebrow>
          <div style={{ display: "flex", gap: 18, marginBottom: 30, flexWrap: "wrap" }}>
            <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: "18px 18px 6px", flex: 1, minWidth: 260, height: 230 }}>
              <div style={{ fontFamily: monoFont, fontSize: 10.5, textTransform: "uppercase", letterSpacing: "0.08em", color: C.inkMuted, marginBottom: 6 }}>Avg rounds to conclusion</div>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={roundsData} margin={{ top: 4, right: 8, left: -20, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={C.hairline} vertical={false} />
                  <XAxis dataKey="name" tick={{ fontFamily: monoFont, fontSize: 10.5, fill: C.inkMuted }} axisLine={{ stroke: C.hairline }} tickLine={false} />
                  <YAxis tick={{ fontFamily: monoFont, fontSize: 10, fill: C.inkMuted }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: C.paperDim }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {roundsData.map((_, i) => <Cell key={i} fill={BATCH_PALETTE[i % 4]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: "18px 18px 6px", flex: 1, minWidth: 260, height: 230 }}>
              <div style={{ fontFamily: monoFont, fontSize: 10.5, textTransform: "uppercase", letterSpacing: "0.08em", color: C.inkMuted, marginBottom: 6 }}>Avg duration (seconds)</div>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={durationData} margin={{ top: 4, right: 8, left: -20, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={C.hairline} vertical={false} />
                  <XAxis dataKey="name" tick={{ fontFamily: monoFont, fontSize: 10.5, fill: C.inkMuted }} axisLine={{ stroke: C.hairline }} tickLine={false} />
                  <YAxis tick={{ fontFamily: monoFont, fontSize: 10, fill: C.inkMuted }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip suffix="s" />} cursor={{ fill: C.paperDim }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {durationData.map((_, i) => <Cell key={i} fill={BATCH_PALETTE[i % 4]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <SectionEyebrow>Outcome Distribution</SectionEyebrow>
          <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, padding: "18px 18px 6px", marginBottom: 30, height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={outcomeData} margin={{ top: 4, right: 8, left: -12, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={C.hairline} vertical={false} />
                <XAxis dataKey="outcome" tick={{ fontFamily: monoFont, fontSize: 10, fill: C.inkMuted }} axisLine={{ stroke: C.hairline }} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontFamily: monoFont, fontSize: 10, fill: C.inkMuted }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: C.paperDim }} />
                <Legend wrapperStyle={{ fontFamily: monoFont, fontSize: 11 }} />
                {batches.map((b, i) => (
                  <Bar key={b.label} dataKey={b.label} fill={BATCH_PALETTE[i % 4]} radius={[4, 4, 0, 0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          <SectionEyebrow>Run Ledger — {activeBatch.label}</SectionEyebrow>
          <div style={{ background: C.paper, border: `1px solid ${C.hairline}`, borderRadius: 10, overflow: "hidden", marginBottom: 10 }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: monoFont, fontSize: 12 }}>
              <thead>
                <tr style={{ background: C.paperDim, textAlign: "left" }}>
                  {["Run", "Outcome", "Rounds", "Duration", "Manifest Error", "Process Issue"].map((h) => (
                    <th key={h} style={{ padding: "9px 14px", fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase", fontSize: 10.5, color: C.inkMuted, borderBottom: `1px solid ${C.hairline}` }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeBatch.data.individual_runs.map((r, i) => (
                  <tr key={i} style={{ background: i % 2 ? C.paperDim : "transparent" }}>
                    <td style={tdStyle}>#{r.run_number}</td>
                    <td style={{ ...tdStyle, color: TONE[actionTone(r.outcome)].fg, fontWeight: 600 }}>{shortOutcome(r.outcome)}</td>
                    <td style={tdStyle}>{r.rounds_taken}</td>
                    <td style={tdStyle}>{r.duration_seconds?.toFixed(1)}s</td>
                    <td style={tdStyle}>
                      {r.manifest_error_found_any_round
                        ? <span style={{ display: "flex", alignItems: "center", gap: 4, color: C.oxblood }}><AlertTriangle size={13} /> Found</span>
                        : <span style={{ display: "flex", alignItems: "center", gap: 4, color: C.inkMuted }}><Minus size={13} /> None</span>}
                    </td>
                    <td style={tdStyle}>
                      {r.process_not_followed_any_round
                        ? <span style={{ display: "flex", alignItems: "center", gap: 4, color: C.oxblood }}><XCircle size={13} /> Flagged</span>
                        : <span style={{ display: "flex", alignItems: "center", gap: 4, color: C.forest }}><CheckCircle2 size={13} /> Clean</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

const tdStyle = { padding: "8px 14px", color: C.ink, borderBottom: `1px solid ${C.hairline}` };

/* ============================== APP ============================== */

export default function ProcurementDisputeDashboard() {
  const [view, setView] = useState("case");

  return (
    <div style={{ background: C.appBg, minHeight: "100%", padding: "28px 20px 60px", fontFamily: bodyFont }}>
      <style>{FONT_IMPORT}</style>
      <div style={{ maxWidth: 1040, margin: "0 auto" }}>
        <div style={{ marginBottom: 4 }}>
          <div style={{ fontFamily: monoFont, fontSize: 11, letterSpacing: "0.16em", textTransform: "uppercase", color: "#5B5341", marginBottom: 6 }}>
            Multi-Agent Procurement Dispute Resolution — Case Viewer
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
            <Gavel size={22} color={C.oxblood} style={{ transform: "translateY(2px)" }} />
            <h1 style={{ fontFamily: displayFont, fontWeight: 700, fontSize: 30, color: C.ink, margin: 0 }}>
              Fusion21 Dispute Docket
            </h1>
          </div>
        </div>

        <div style={{ display: "flex", marginTop: 22 }}>
          <FolderTab active={view === "case"} onClick={() => setView("case")} icon={ScrollText}>Case File</FolderTab>
          <FolderTab active={view === "docket"} onClick={() => setView("docket")} icon={BarChart3}>Docket Analytics</FolderTab>
        </div>

        <div style={{ background: C.paper, borderRadius: "0 10px 10px 10px", padding: 24, position: "relative", zIndex: 2, boxShadow: "0 4px 18px rgba(30,25,15,0.10)" }}>
          {view === "case" ? <CaseFileView /> : <DocketAnalyticsView />}
        </div>

        <div style={{ textAlign: "center", marginTop: 22, fontFamily: monoFont, fontSize: 10.5, color: "#8C8266" }}>
          Reads NegotiationState and batch_summary JSON produced by the LangGraph orchestrator.
        </div>
      </div>
    </div>
  );
}
