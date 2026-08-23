// Voicera front-desk knowledge base. Simple keyword rules — no server needed.

export const GREETING =
  "Hi, I'm Voicera, your AI front desk. Ask me about business hours, appointments, or anything else — I'll answer right here, out loud.";

export const SUGGESTIONS = [
  "What are your business hours?",
  "How do I book an appointment?",
  "Do you support multiple languages?",
  "Can you take a message?",
];

const RULES = [
  {
    keys: ["hours", "open", "close", "when are you open", "timing"],
    reply:
      "We're open Monday to Friday, eight a.m. to six p.m., and Saturdays from nine to one. After hours I answer every call, take a message, or book an appointment for the next business day.",
  },
  {
    keys: ["appointment", "book", "booking", "reserve", "slot", "schedule", "meet the doctor", "see the doctor"],
    reply:
      "Booking is easy. Tell me your preferred day and time and I'll check the calendar, grab a slot, and confirm it right here by voice. What day works best for you?",
  },
  {
    keys: ["price", "pricing", "cost", "how much", "plan", "month", "trial", "free"],
    reply:
      "Pilot plans start well below the cost of a single missed customer. In this demo I'll connect you with the team for exact numbers — a seven-day pilot is free.",
  },
  {
    keys: ["language", "spanish", "french", "hindi", "english", "multilingual", "languages"],
    reply:
      "Absolutely. I detect the caller's language and reply in all major Indian languages. Right now I'm speaking English, but the real assistant switches fluently.",
  },
  {
    keys: ["message", "leave a message", "voicemail", "call back", "someone"],
    reply:
      "No problem. I'll take your name and number and make sure the right person gets your message. Who should I say is calling?",
  },
  {
    keys: [
      "hello",
      "hi ",
      "hey",
      "good morning",
      "good afternoon",
      "good evening",
      "who are you",
      "help",
      "what can you do",
      "start",
      "demo",
      "test",
    ],
    reply:
      "Hello! I'm Voicera, your voice front desk. I can share business hours, book appointments, answer questions, and take messages. What would you like to know?",
  },
];

const FALLBACK =
  "Great question. In this demo I know about our hours, appointments, pricing, languages, and taking messages. For anything else I'd route you to the right human. Try another question, or pick a suggestion below the mic.";

export function answer(text) {
  const lower = text.toLowerCase();
  for (const rule of RULES) {
    if (rule.keys.some((key) => lower.includes(key))) return rule.reply;
  }
  return FALLBACK;
}
