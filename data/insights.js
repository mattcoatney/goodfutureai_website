/**
 * GoodFuture.ai — Insights Content Data
 *
 * !! AUTO-GENERATED — do not edit directly !!
 * Edit or add files in content/insights/ then run:
 *
 *     python scripts/build_insights.py
 *
 * AVAILABLE TAGS (add new ones as needed):
 * "AI & Work", "Skills", "Leadership", "Education", "Tools", "Strategy", "Personal"
 */

const INSIGHTS = [

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
