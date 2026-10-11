import PageHeader from "../components/PageHeader";
import TechnicalPanel from "../components/TechnicalPanel";

const topics = [
  {
    q: "What does HIGH risk mean?",
    a: "Several warning signs matched, such as a fake brand name, a known phishing pattern, or a suspicious domain ending. Treat the site as unsafe. Do not enter a password, OTP, or card number.",
  },
  {
    q: "What does CRITICAL risk mean?",
    a: "Multiple strong signals matched at once. Close the page. If the link came from SMS or WhatsApp, do not tap it again.",
  },
  {
    q: "What should I do after finding a phishing URL?",
    a: "Do not sign in. Do not download files. Tell the person who sent the link. If you already entered a password, change it on the real website using a bookmark, not the suspicious link.",
  },
  {
    q: "How can I recognize a fake login page?",
    a: "Check the spelling in the address bar. Fake pages often use numbers in brand names (paypa1), extra words (sbi-login), or unusual endings (.xyz, .tk). Real banks never rush you with 'act now or your account will be blocked'.",
  },
  {
    q: "A link says verify my account. Is that a prize or a login trap?",
    a: "If the link says verify, login, or your account is locked, treat it as someone trying to steal the login. A prize or lottery only applies when the message says you won money. Do not enter a password or OTP. Open the real app or type the real website yourself.",
  },
];

export default function Advisor() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <PageHeader
        section="08 / Advisor"
        title="Security advisor"
        subtitle="Simple explanations. No technical jargon required."
      />
      {topics.map((item, index) => (
        <TechnicalPanel key={item.q} title={`${String(index + 1).padStart(2, "0")} / Guidance`}>
          <h2 className="font-display text-lg font-semibold text-ink">{item.q}</h2>
          <p className="mt-3 text-sm leading-6 text-ink-soft">{item.a}</p>
        </TechnicalPanel>
      ))}
    </div>
  );
}
