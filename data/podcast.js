/**
 * GoodFuture.ai — Podcast Content Data
 *
 * !! AUTO-GENERATED — do not edit directly !!
 * Edit files in content/podcast/ then run:
 *
 *     python scripts/build_podcast.py
 *
 *   _show.yaml        — show name, description, platform links
 *   episodes/*.md     — individual episodes (newest first)
 *   appearances/*.md  — guest appearances on other shows
 */

const PODCAST_SHOW = {
  name:        "Building a Better Future Together",
  tagline:     "with GoodFuture.ai",
  description: "Real conversations about navigating the AI era — without the hype and without the doom. Just honest talk about where we're headed, what it means for real people, and how to feel a little more confident about the future.\n",
  platforms:   [
    { name: "Apple Podcasts", url: "#", icon: "apple" },
    { name: "Spotify", url: "#", icon: "spotify" },
    { name: "YouTube", url: "#", icon: "youtube" }
  ],
  listenUrl:   "#",
};

/**
 * Episodes — newest first.
 * Fields: slug, title, date, tags, excerpt, duration,
 *         youtubeId, spotifyEmbedUrl, applePodcastsUrl, spotifyUrl, coverImage
 */
const PODCAST_EPISODES = [
  /* No episodes yet — add .md files to content/podcast/episodes/ */
];

/**
 * Podcast appearances — guest spots on other shows — newest first.
 * Fields: show, title, date, description, url, tags
 */
const PODCAST_APPEARANCES = [
  {
    show:        "The Wired Garage with Pops",
    title:       "Chatbots Were the Trailer, Agents Are the Movie",
    date:        "2026-02-17",
    description: "AI has moved well beyond chatbots — today's agents can plan, execute, and iterate on complex tasks with minimal human intervention. We explored the real productivity gains happening in software development, why clear specifications matter more than ever, and the honest ethical questions that come with automating more of our work.",
    url:         "https://podcasts.apple.com/gm/podcast/chatbots-were-the-trailer-agents-are-the-movie/id1861572678?i=1000750125404",
    tags:        ["AI & Work", "Tools"],
  },
  {
    show:        "The Wired Garage with Pops",
    title:       "Unleashing Human Creativity with Agentic AI",
    date:        "2025-12-15",
    description: "How does agentic AI change the way we work — and what does it mean for human creativity? We talked through how AI enhances collaboration rather than replacing it, the necessity of human judgment in high-stakes decisions, and what skills leaders need to cultivate as autonomous systems become more capable.",
    url:         "https://podcasts.apple.com/gm/podcast/unleashing-human-creativity-with-agentic-a/id1861572678?i=1000741426777",
    tags:        ["AI & Work", "Leadership"],
  },
  {
    show:        "Product Mastery Now",
    title:       "Using AI in Risk-Averse Industries",
    date:        "2025-03-01",
    description: "Healthcare, finance, legal — highly regulated industries can't just move fast and break things. In episode 531 of Product Mastery Now, we talked about how to introduce AI thoughtfully in risk-averse environments, where to start, what guardrails matter, and how to build trust with teams that are understandably cautious.",
    url:         "https://productmasterynow.com/blog/531-using-ai-in-risk-adverse-industries-with-matt-coatney/",
    tags:        ["AI & Work", "Strategy", "Leadership"],
  },
  {
    show:        "The Forward Slash Podcast",
    title:       "AI: The Jagged Frontier",
    date:        "2024-11-27",
    description: "The \"jagged frontier\" of AI captures something real — it's remarkably capable in some areas and surprisingly brittle in others. We talked through what data foundations companies actually need before chasing AI, where generative AI reliably delivers business value, and how to set honest expectations with your team about what it can and can't do.",
    url:         "https://podcasts.apple.com/us/podcast/ai-the-jagged-frontier/id1744372906?i=1000678409487",
    tags:        ["AI & Work", "Strategy"],
  }
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
