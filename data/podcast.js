/**
 * GoodFuture.ai — Podcast Content Data
 *
 * !! AUTO-GENERATED — do not edit directly !!
 * Edit files in content/podcast/ then run:
 *
 *     python scripts/build_podcast.py
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

const PODCAST_EPISODES = [
  /* No episodes yet — add .md files to content/podcast/episodes/ */
];

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
  },
  {
    show:        "The Geek In Review",
    title:       "The Human Cloud: The World of Projects and Freelancers",
    date:        "2021-11-11",
    description: "Episode 136 of The Geek In Review, a legal technology podcast. We explored how freelancing and project-based work combined with AI and machine learning are disrupting how work gets done — including inside law firms, where legal matters are essentially projects and contract attorneys are already functioning as freelancers. Plus a look at what organizations risk if they don't prepare for this shift.",
    url:         "https://podcasts.apple.com/us/podcast/matthew-coatney-the-human-cloud-the-world/id1401505293?i=1000541457900",
    tags:        ["AI & Work", "Strategy"],
  },
  {
    show:        "Futurized",
    title:       "Orchestrating the Freelance Economy",
    date:        "2021-05-04",
    description: "A conversation with host Trond Arne Undheim about how AI and the rise of freelance work are transforming employment. We covered the shift from assembly-line roles to project-based work, the enabling technologies making distributed teams possible at scale, and why orchestration — the skill of managing complex, distributed work — is becoming one of the most valuable capabilities anyone can develop.",
    url:         "https://www.podbean.com/media/share/pb-23532-ff9a12",
    tags:        ["AI & Work", "Strategy"],
  },
  {
    show:        "Product Mastery Now",
    title:       "The Coming Work Paradigm Shift",
    date:        "2021-04-12",
    description: "Episode 330 of Product Mastery Now (formerly The Everyday Innovator). We talked about how the future of work is being reshaped by technology, the gig economy, and AI — and what that means for product managers and business leaders. The conversation centered on the concept of \"Changemakers\": people who thrive not by clinging to job titles, but by driving value through an entrepreneurial mindset in a project-based world.",
    url:         "https://productmasterynow.com/blog/tei-330-the-coming-work-paradigm-shift-with-matt-coatney/",
    tags:        ["AI & Work", "Strategy", "Leadership"],
  }
];

/* Helper: format date for display */
function formatPodcastDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}
