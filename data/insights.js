/**
 * GoodFuture.ai — Insights Content Data
 *
 * HOW TO ADD A NEW INSIGHT:
 * 1. Add a new object to the INSIGHTS array below.
 * 2. Set featured: true for the first/most important article (shown prominently on home page).
 * 3. Fill in slug, title, date (YYYY-MM-DD), tags, excerpt, readingTime.
 * 4. If the insight has a YouTube video, set youtubeId to the video ID (e.g., "dQw4w9WgXcQ").
 * 5. If there's a cover image, set coverImage to the path (e.g., "/assets/images/my-post.jpg").
 * 6. The body field supports basic HTML for rich content.
 *
 * AVAILABLE TAGS (add new ones as needed):
 * "AI & Work", "Skills", "Leadership", "Education", "Tools", "Strategy", "Personal"
 */

const INSIGHTS = [
  {
    slug: "ai-wont-replace-you",
    title: "Why AI Won't Replace You — But Will Replace You If You Don't Use It",
    date: "2025-02-01",
    tags: ["AI & Work"],
    excerpt: "The narrative has been binary for too long. Here's the more nuanced, more useful truth about what AI actually means for your career.",
    body: `<p>The fear is real. The headlines are loud. "AI will take your job." "Humans are obsolete." It makes for great clicks, and for a lot of sleepless nights.</p>
<p>But here's what's actually happening: AI isn't replacing humans. It's replacing humans who aren't using AI. And that's a very different — and much more hopeful — situation to be in.</p>
<p>Think about it this way. When spreadsheets arrived, they didn't replace accountants. They replaced the tedious parts of accounting and made accountants dramatically more productive. The accountants who embraced spreadsheets became better, faster, and more valuable. The ones who didn't... well.</p>
<p>AI is the next spreadsheet. Except it's not just for one profession — it's for everyone who works with information, ideas, or communication. Which is most of us.</p>
<p>So the question isn't "will AI take my job?" The question is "am I learning to work alongside it?" If the answer is yes, you're going to be fine. Better than fine, actually.</p>`,
    coverImage: null,
    youtubeId: null,
    readingTime: "8 min read",
    featured: true,
  },
  {
    slug: "5-skills-ai-era",
    title: "The 5 Skills You Actually Need in the AI Era",
    date: "2025-01-15",
    tags: ["Skills"],
    excerpt: "Forget prompt engineering tutorials. The real differentiators are the ones that have always mattered — now amplified.",
    body: `<p>Everyone wants to know: what skills do I need to survive the AI era? And the internet is happy to oblige — with tutorials on prompt engineering, AI tool certifications, and "how to use ChatGPT" courses.</p>
<p>Here's the thing though: those aren't the skills that will make you exceptional in an AI-augmented world. The skills that matter are the ones that have always mattered, now made more powerful by AI.</p>
<p><strong>1. Critical thinking.</strong> AI generates plausible-sounding content at scale. Humans who can evaluate it, question it, and improve it are invaluable. AI doesn't replace critical thinking — it demands more of it.</p>
<p><strong>2. Curiosity.</strong> The professionals thriving right now aren't necessarily the most technical. They're the most curious — constantly asking what's possible, what's changed, what they haven't tried yet.</p>
<p><strong>3. Communication.</strong> As AI handles more execution, humans who can communicate clearly — in writing, in conversation, in presentations — become more essential, not less.</p>
<p><strong>4. Collaboration.</strong> Working well with other humans is increasingly rare and increasingly valuable. AI can generate ideas; it can't navigate relationships, build trust, or read a room.</p>
<p><strong>5. Judgment.</strong> When everything can be generated instantly, the ability to decide what's worth generating — and what to do with it — is the real competitive advantage.</p>`,
    coverImage: null,
    youtubeId: null,
    readingTime: "6 min read",
    featured: false,
  },
  {
    slug: "honest-ai-conversation-team",
    title: "How to Have an Honest Conversation With Your Team About AI",
    date: "2024-12-10",
    tags: ["Leadership"],
    excerpt: "Most leaders avoid this conversation. Here's a framework for having it in a way that builds trust, not anxiety.",
    body: `<p>Your team is scared. Maybe they're not saying it out loud — but they're watching the news, reading the headlines, and wondering if their job is safe. And if you're not talking about it, that silence is getting filled with fear and speculation.</p>
<p>The good news: this conversation is actually one of the best opportunities you have to build trust with your team. Here's how to have it well.</p>
<p><strong>Start with honesty about uncertainty.</strong> You don't know exactly how AI will change your industry. Nobody does. Admitting that isn't weakness — it's credibility. "I don't have all the answers, but I want us to figure this out together" lands very differently than "everything's fine."</p>
<p><strong>Separate fact from fear.</strong> AI is genuinely changing things. But the timeline, scope, and impact in your specific context may be very different from the worst-case headlines. Help your team see the actual landscape of your industry.</p>
<p><strong>Make it about growth, not replacement.</strong> Reframe the conversation around capability-building. What can we learn? What can we do better? What could we do now that we couldn't before?</p>
<p><strong>Invite experimentation.</strong> Give your team permission — even encouragement — to try AI tools. Make it safe to explore, safe to fail, and safe to share what they find.</p>`,
    coverImage: null,
    youtubeId: null,
    readingTime: "5 min read",
    featured: false,
  },
  {
    slug: "schools-getting-ai-wrong",
    title: "The Real Reason Schools Are Getting AI Wrong",
    date: "2024-11-05",
    tags: ["Education"],
    excerpt: "Education is panicking about AI and asking the wrong questions. Here's what we should actually be focused on.",
    body: `<p>The conversation in education right now is dominated by one question: how do we stop students from using AI to cheat?</p>
<p>It's the wrong question. And asking the wrong question is costing us something important.</p>
<p>Here's the right question: how do we prepare students for a world where AI is everywhere, and help them develop the judgment to use it well?</p>
<p>The goal of education has never been to make students memorize and regurgitate information. It's been to develop thinkers, problem solvers, communicators, and collaborators. AI doesn't threaten those goals. It's a stress test for them.</p>
<p>If a student can use AI to complete an assignment, and we can't tell the difference... maybe we were asking the wrong question in the first place. Maybe we were testing retention when we should be testing thinking.</p>
<p>The schools getting this right aren't banning AI. They're redesigning their curriculum around the skills that AI can't replicate: synthesis, application, ethics, creativity, communication. They're treating AI as a co-learner, not a cheat code.</p>
<p>That's the future of education. And the sooner we get there, the better prepared our kids will be.</p>`,
    coverImage: null,
    youtubeId: null,
    readingTime: "7 min read",
    featured: false,
  },
  {
    slug: "honest-ai-toolkit",
    title: "My Honest AI Toolkit: What I Use, What I Ditched, and Why",
    date: "2024-10-22",
    tags: ["Tools"],
    excerpt: "A no-fluff look at the AI tools that actually make a difference in my workflow — and the ones I've stopped using.",
    body: `<p>I've been testing AI tools obsessively for the past couple of years. Not because I'm a tech enthusiast (I'm not, particularly), but because I'm genuinely trying to figure out what helps and what doesn't. Here's what I've learned.</p>
<p><strong>What I use every single day:</strong> A conversational AI assistant (currently Claude) for thinking through problems, drafting, and editing. It's not about generating content — it's about having a thinking partner who's always available and never impatient.</p>
<p><strong>What I use weekly:</strong> Transcription and summarization tools for meetings and interviews. The hours I've gotten back here are real.</p>
<p><strong>What I stopped using:</strong> Most of the specialized AI tools I signed up for in the hype cycle of 2023. The all-in-one AI workspace apps. The "AI-powered" versions of tools that worked fine before. The novelty wore off fast.</p>
<p><strong>What I've learned:</strong> The most powerful AI use isn't flashy. It's using AI to think better, write better, and move faster in the work you're already doing. The best tool is usually the one that disappears into your workflow.</p>
<p>AI tools aren't magic. They're amplifiers. They make good processes better and bad processes faster (which isn't always good). Get your process right first, then bring in AI.</p>`,
    coverImage: null,
    youtubeId: null,
    readingTime: "9 min read",
    featured: false,
  },
];

/* Helper: format date for display */
function formatInsightDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

/* Helper: get all unique tags */
function getInsightTags() {
  const tags = new Set();
  INSIGHTS.forEach(a => a.tags.forEach(t => tags.add(t)));
  return Array.from(tags).sort();
}
