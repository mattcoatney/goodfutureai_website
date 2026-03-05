/**
 * GoodFuture.ai — Podcast Content Data
 *
 * HOW TO ADD A NEW EPISODE:
 * 1. Add a new object to PODCAST_EPISODES (newest first).
 * 2. Set youtubeId if there's a YouTube recording (e.g., "dQw4w9WgXcQ").
 * 3. Set spotifyEmbedUrl for a Spotify embed (the full embed URL).
 * 4. Set applePodcastsUrl and spotifyUrl for platform links.
 * 5. The coverImage field is optional — leave null to use the default show art.
 *
 * HOW TO ADD A NEW APPEARANCE:
 * 1. Add a new object to PODCAST_APPEARANCES (newest first).
 * 2. Set the show name, episode title, description, and link URL.
 */

const PODCAST_SHOW = {
  name: "Building Tomorrow, Today",
  tagline: "with GoodFuture.ai",
  description: "Real conversations about navigating the AI era — without the hype and without the doom. Just honest talk about where we're headed, what it means for real people, and how to feel a little more confident about the future.",
  platforms: [
    { name: "Apple Podcasts", url: "#", icon: "apple" },
    { name: "Spotify", url: "#", icon: "spotify" },
    { name: "YouTube", url: "#", icon: "youtube" },
  ],
  listenUrl: "#",
};

/**
 * Episodes — add new episodes here.
 * Fields:
 *   slug         - URL-friendly identifier
 *   title        - Episode title
 *   date         - Publication date (YYYY-MM-DD)
 *   tags         - Array of topic tags
 *   excerpt      - Short description (1-2 sentences)
 *   youtubeId    - YouTube video ID if available (null if not)
 *   spotifyEmbedUrl - Full Spotify embed URL if available (null if not)
 *   applePodcastsUrl - Apple Podcasts link (null if not available)
 *   spotifyUrl   - Spotify episode link
 *   coverImage   - Path to episode cover image (null to use show default)
 *   duration     - Episode length (e.g., "42 min")
 */
const PODCAST_EPISODES = [
  /* Example — uncomment and fill in when your first episode is ready:
  {
    slug: "ep-1-getting-started-with-ai",
    title: "Getting Started With AI: Where to Begin Without Getting Overwhelmed",
    date: "2025-03-01",
    tags: ["Getting Started", "AI Tools"],
    excerpt: "The first episode of Building Tomorrow, Today — a conversation about what AI actually is, why it matters, and the very first step to take.",
    youtubeId: null,
    spotifyEmbedUrl: null,
    applePodcastsUrl: null,
    spotifyUrl: null,
    coverImage: null,
    duration: "38 min",
  },
  */
];

/**
 * Podcast appearances — guest spots on other shows.
 * Fields:
 *   show         - Name of the podcast/show
 *   title        - Episode title
 *   date         - Appearance date (YYYY-MM-DD)
 *   description  - Short description (1-3 sentences)
 *   url          - Link to the episode
 *   tags         - Optional topic tags
 */
const PODCAST_APPEARANCES = [
  {
    show: "The Future of Work",
    title: "AI Isn't the Enemy — Complacency Is",
    date: "2025-01-20",
    description: "A conversation about why the biggest risk isn't AI taking jobs — it's people deciding they don't need to adapt. And what to do instead.",
    url: "#",
    tags: ["AI & Work"],
  },
  {
    show: "Work 3.0",
    title: "The Human Cloud: What We Got Right and Wrong",
    date: "2024-12-15",
    description: "Looking back at the predictions from The Human Cloud and what the last few years have actually taught us about the future of work.",
    url: "#",
    tags: ["Future of Work"],
  },
  {
    show: "The Learning Curve",
    title: "Redesigning Education for the AI Generation",
    date: "2024-11-28",
    description: "What if we stopped asking how to keep AI out of classrooms and started asking how to use it to build better, more resilient learners?",
    url: "#",
    tags: ["Education"],
  },
  {
    show: "Leadership Now",
    title: "What Great Leaders Do When Technology Disrupts Everything",
    date: "2024-10-15",
    description: "The leaders navigating disruption best have one thing in common — and it's not being technical. A conversation about leading with humanity.",
    url: "#",
    tags: ["Leadership"],
  },
  {
    show: "Startup Stories",
    title: "Building in the Age of AI-First Everything",
    date: "2024-09-30",
    description: "What it means to build something new right now — and why the AI era might actually be the best time in history to start a company.",
    url: "#",
    tags: ["Strategy"],
  },
  {
    show: "The Career Lab",
    title: "Reskilling in Your 40s: A Real Conversation",
    date: "2024-08-20",
    description: "An honest conversation about mid-career transitions in the AI era — the fears, the real opportunities, and what actually helps people make the jump.",
    url: "#",
    tags: ["Skills"],
  },
];

/* Helper: format date for display */
function formatPodcastDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

/* Helper: SVG icons for platforms */
const PLATFORM_ICONS = {
  apple: `<svg width="15" height="15" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">
    <path d="M7.5 0C3.4 0 0 3.4 0 7.5S3.4 15 7.5 15 15 11.6 15 7.5 11.6 0 7.5 0zm0 2.5a5 5 0 110 10 5 5 0 010-10zm.5 2H7v4.5l3.5 2-.5-.8-3-1.7V4.5z" opacity=".8"/>
  </svg>`,
  spotify: `<svg width="15" height="15" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">
    <path d="M7.5 0C3.4 0 0 3.4 0 7.5S3.4 15 7.5 15 15 11.6 15 7.5 11.6 0 7.5 0zm3.3 10.7c-.1.2-.4.3-.6.1-1.6-1-3.5-1.2-5.8-.7-.2.1-.4-.1-.5-.3-.1-.2.1-.4.3-.5 2.5-.6 4.6-.3 6.3.8.3.1.3.4.3.6zm.9-2c-.2.2-.5.3-.7.1-1.8-1.1-4.5-1.4-6.7-.8-.3.1-.5-.1-.6-.4-.1-.3.1-.5.4-.6 2.4-.7 5.4-.4 7.5.9.2.1.3.5.1.8zm.1-2.1c-2.2-1.3-5.8-1.4-7.9-.8-.3.1-.6-.1-.7-.4-.1-.3.1-.6.4-.7 2.4-.7 6.4-.6 8.9.9.3.2.4.5.2.8-.2.3-.6.4-.9.2z" opacity=".8"/>
  </svg>`,
  youtube: `<svg width="15" height="15" viewBox="0 0 15 15" fill="currentColor" aria-hidden="true">
    <path d="M7.5 0C3.4 0 0 3.4 0 7.5S3.4 15 7.5 15 15 11.6 15 7.5 11.6 0 7.5 0zm-1.5 4.5l6 3-6 3V4.5z" opacity=".8"/>
  </svg>`,
};
