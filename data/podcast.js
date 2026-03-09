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
