import { useState } from "react";
import Nav from "../components/Nav.jsx";
import Footer from "../components/Footer.jsx";
import IndustryWidget from "../components/IndustryWidget.jsx";
import { ArrowIcon } from "../components/icons.jsx";

const STATS = [
  {
    label: "Peak hour overload",
    value: "62%",
    text: "of calls to small businesses go unanswered during peak hours",
  },
  {
    label: "After-hours silence",
    value: "67%",
    text: "of customers won't call back after one missed attempt",
  },
  {
    label: "Repetition overload",
    value: "80%",
    text: "of customer interactions are repetitive and could be automated",
  },
];

const INDUSTRIES = [
  { kind: "hospital", tone: "teal" },
  { kind: "enterprise", tone: "blue" },
  { kind: "store", tone: "yellow" },
];

const CRM_CALLS = [
  { time: "10:02 AM", caller: "+91 98765 43210", intent: "Appointment booking", status: "resolved", duration: "1:24" },
  { time: "10:08 AM", caller: "+91 87654 32109", intent: "Insurance query", status: "resolved", duration: "0:58" },
  { time: "10:15 AM", caller: "+91 76543 21098", intent: "Report status", status: "pending", duration: "2:11" },
  { time: "10:22 AM", caller: "+91 65432 10987", intent: "Doctor availability", status: "resolved", duration: "1:05" },
  { time: "10:31 AM", caller: "+91 54321 09876", intent: "Emergency info", status: "escalated", duration: "0:42" },
  { time: "10:38 AM", caller: "+91 43210 98765", intent: "Visiting hours", status: "resolved", duration: "0:37" },
];

const BAR_HEIGHTS = [3, 7, 12, 9, 14, 11, 8, 5];
const BAR_LABELS = ["8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm"];

const TICKER_ITEMS = [
  { time: "09:21 PM", business: "Green Leaf Pharmacy", action: "Stock query answered", lang: "Hindi" },
  { time: "04:49 AM", business: "CarePoint Hospital", action: "Appointment booked", lang: "Kannada" },
  { time: "08:14 AM", business: "Apollo Clinic", action: "Appointment booked", lang: "Hindi" },
  { time: "09:47 AM", business: "Titan Stores", action: "Order status checked", lang: "English" },
  { time: "11:32 AM", business: "City Hospital", action: "Appointment rescheduled", lang: "Telugu" },
  { time: "02:18 PM", business: "Metro Clinic", action: "Doctor availability checked", lang: "Tamil" },
  { time: "07:05 AM", business: "Wellness Pharmacy", action: "Prescription refill confirmed", lang: "Hindi" },
  { time: "01:33 PM", business: " Sunrise Hospitals", action: "Insurance verified", lang: "Kannada" },
];

const HOW_STEPS = [
  {
    num: "01",
    title: "Map the calls",
    text: "We sit with your team and map high-volume call intents, your language mix, and how sensitive calls should escalate.",
  },
  {
    num: "02",
    title: "Set up the agent",
    text: "Greeting style, peak-hour behaviour, staff routing, and prompt tuning \u2014 configured for how your front desk actually runs.",
  },
  {
    num: "03",
    title: "Connect your systems",
    text: "Voicera plugs into Sheets, standard APIs, or a custom integration, depending on your tier.",
  },
  {
    num: "04",
    title: "Go live",
    text: "Launch with a full dashboard \u2014 call logs, transcripts, and resolution rates from day one.",
  },
];

const SidebarIcon = ({ d }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {d}
  </svg>
);

export default function Landing() {
  const [activeWidget, setActiveWidget] = useState(null);

  function handleActivate(industry) {
    setActiveWidget(industry);
  }

  return (
    <>
      <Nav />

      <header className="hero" id="top">
        <div className="hero-inner">
          <p className="eyebrow">AI voice receptionist for appointment booking and call automation</p>
          <h1>
            Your front desk, on{" "}
            <span className="hl">
              autopilot.
              <svg viewBox="0 0 300 24" preserveAspectRatio="none" aria-hidden="true">
                <path
                  d="M6 14 C 70 4, 190 2, 294 12"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="9"
                  strokeLinecap="round"
                  opacity="0.4"
                />
              </svg>
            </span>
          </h1>
          <p className="hero-sub">
            Voicera answers every call in a natural cloned voice - books appointments, answers
            questions, and never puts a caller on hold.
          </p>
          <div className="hero-actions">
            <a className="btn btn-primary btn-lg" href="#demo">
              Try now <span className="arrow"><ArrowIcon /></span>
            </a>
            <a className="btn btn-secondary btn-lg" href="#how">
              How it works
            </a>
          </div>
        </div>
        <div className="bars" aria-hidden="true">
          {Array.from({ length: 10 }).map((_, i) => (
            <i key={i} />
          ))}
        </div>
      </header>

      <div className="ticker" aria-label="Live activity feed">
        <div className="ticker-track">
          {[...TICKER_ITEMS, ...TICKER_ITEMS].map((item, i) => (
            <span key={i} className="ticker-item">
              <span className="ticker-time">{item.time}</span>
              {" "}{item.business} — {item.action} — {item.lang}
            </span>
          ))}
        </div>
      </div>

      <main className="band">
        <section id="demo">
          <div className="sec">
            <div className="sec-head">
              <p className="eyebrow">Experience it in action</p>
              <h2>Talk to Voicera right now</h2>
              <p>
                Every reply is spoken aloud by Voicera in the voice you pick. Click any
                industry orb to start a live voice conversation.
              </p>
            </div>
            <div className="demo-grid">
              {INDUSTRIES.map((ind) => (
                <IndustryWidget
                  key={ind.kind}
                  industry={ind.kind}
                  tone={ind.tone}
                  isActive={activeWidget === ind.kind}
                  onActivate={handleActivate}
                />
              ))}
            </div>
          </div>
        </section>

        <section id="why">
          <div className="sec">
            <div className="sec-head">
              <p className="eyebrow">The problem</p>
              <h2>Limited receptionist, unlimited calls.</h2>
              <p>Too many calls, not enough people, and no way to know what got missed.</p>
            </div>
            <div className="stats">
              {STATS.map((stat) => (
                <div key={stat.label} className="stat-wrap">
                  <div className="stat-plate" />
                  <div className="stat-card">
                    <p className="mono">{stat.label}</p>
                    <h3>{stat.value}</h3>
                    <p>{stat.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="product">
          <div className="sec">
            <p className="eyebrow">The product</p>
            <h2>Voicera</h2>
            <p>A voice agent personalized for your business.</p>
          </div>
        </section>

        <section className="crm-section">
          <div className="sec">
            <div className="sec-head">
              <p className="eyebrow">Analytics</p>
              <h2>Live call dashboard</h2>
              <p>Every conversation is logged, transcribed, and analysed in real time.</p>
            </div>
            <div className="crm-dashboard">
              <div className="crm-topbar">
                <div className="crm-topbar-left">
                  <span className="crm-dot crm-dot--red" />
                  <span className="crm-dot crm-dot--yellow" />
                  <span className="crm-dot crm-dot--green" />
                  <span className="crm-topbar-title">Voicera CRM</span>
                </div>
                <div className="crm-topbar-right">Live session - Hospital</div>
              </div>
              <div className="crm-body">
                <aside className="crm-sidebar">
                  <button type="button" className="crm-nav-item active">
                    <SidebarIcon d={<><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>} />
                    Dashboard
                  </button>
                  <button type="button" className="crm-nav-item">
                    <SidebarIcon d={<><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></>} />
                    Calls
                  </button>
                  <button type="button" className="crm-nav-item">
                    <SidebarIcon d={<><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></>} />
                    Contacts
                  </button>
                  <button type="button" className="crm-nav-item">
                    <SidebarIcon d={<><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></>} />
                    Analytics
                  </button>
                  <button type="button" className="crm-nav-item">
                    <SidebarIcon d={<><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></>} />
                    Settings
                  </button>
                </aside>
                <div className="crm-content">
                  <div className="crm-kpi-row">
                    <div className="crm-kpi">
                      <div className="crm-kpi-label">Calls today</div>
                      <div className="crm-kpi-value">47</div>
                      <div className="crm-kpi-change up">+18% vs yesterday</div>
                    </div>
                    <div className="crm-kpi">
                      <div className="crm-kpi-label">AI resolved</div>
                      <div className="crm-kpi-value">82%</div>
                      <div className="crm-kpi-change up">+5% this week</div>
                    </div>
                    <div className="crm-kpi">
                      <div className="crm-kpi-label">Avg handle time</div>
                      <div className="crm-kpi-value">1:12</div>
                      <div className="crm-kpi-change down">-8s faster</div>
                    </div>
                    <div className="crm-kpi">
                      <div className="crm-kpi-label">Satisfaction</div>
                      <div className="crm-kpi-value">4.8</div>
                      <div className="crm-kpi-change up">+0.3 this month</div>
                    </div>
                  </div>
                  <div className="crm-table-wrap">
                    <div className="crm-table-header">
                      <span className="crm-table-title">Recent calls</span>
                    </div>
                    <table className="crm-table">
                      <thead>
                        <tr>
                          <th>Time</th>
                          <th>Caller</th>
                          <th>Intent</th>
                          <th>Status</th>
                          <th>Duration</th>
                        </tr>
                      </thead>
                      <tbody>
                        {CRM_CALLS.map((call, i) => (
                          <tr key={i}>
                            <td>{call.time}</td>
                            <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.78rem" }}>{call.caller}</td>
                            <td>{call.intent}</td>
                            <td>
                              <span className={`crm-badge crm-badge--${call.status}`}>{call.status}</span>
                            </td>
                            <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.78rem" }}>{call.duration}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="crm-chart-area">
                    <div className="crm-chart-card">
                      <div className="crm-chart-title">Calls per hour</div>
                      <div className="crm-bar-chart">
                        {BAR_HEIGHTS.map((h, i) => (
                          <div key={i} className="crm-bar-row">
                            <div className="crm-bar" style={{ height: ((h / 14) * 100) + "%" }} />
                            <div className="crm-bar-label">{BAR_LABELS[i]}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="crm-chart-card">
                      <div className="crm-chart-title">Resolution breakdown</div>
                      <div className="crm-donut-wrap">
                        <div className="crm-donut" />
                        <div className="crm-donut-legend">
                          <div className="crm-legend-item">
                            <span className="crm-legend-dot" style={{ background: "var(--primary)" }} />
                            AI resolved (42%)
                          </div>
                          <div className="crm-legend-item">
                            <span className="crm-legend-dot" style={{ background: "var(--teal-600)" }} />
                            Human assisted (29%)
                          </div>
                          <div className="crm-legend-item">
                            <span className="crm-legend-dot" style={{ background: "var(--yellow-600)" }} />
                            Pending (17%)
                          </div>
                          <div className="crm-legend-item">
                            <span className="crm-legend-dot" style={{ background: "#4b5563" }} />
                            Missed (12%)
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="how">
          <div className="sec how-section">
            <div className="how-header">
              <p className="eyebrow">How It Works</p>
              <h2>Live in days, not quarters.</h2>
              <p className="how-desc">Four steps, in order — most clinics are live and measuring results within a week.</p>
            </div>
            <div className="timeline">
              {HOW_STEPS.map((step, i) => (
                <div key={step.num} className="timeline-step">
                  <div className="timeline-left">
                    <div className="timeline-marker">{step.num}</div>
                    {i < HOW_STEPS.length - 1 && <div className="timeline-line" />}
                  </div>
                  <div className="timeline-right">
                    <h3>{step.title}</h3>
                    <p>{step.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="cta">
          <div className="sec">
            <div className="cta-panel">
              <h2>
                Stop missing calls.
                <br />
                Start with one live pilot.
              </h2>
              <p>
                We configure Voicera for your real calls and launch a live demo you can hear today.
              </p>
              <button type="button" className="btn btn-secondary btn-lg" onClick={() => document.getElementById("demo")?.scrollIntoView({ behavior: "smooth" })}>
                Try Voicera now
              </button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
