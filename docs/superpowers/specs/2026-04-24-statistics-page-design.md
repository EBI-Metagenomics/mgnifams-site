# MGnifams Statistics Page Design

## Summary

Add a new expandable statistics page to the MGnifams site. The first version will host two supplied static release-level plots:

- `family_length_short.png`
- `family_size_medium.png`

The page should be a durable place for future dataset overview plots, but the initial implementation should only expose the two supplied images.

## Goals

- Add a first-class internal `/statistics/` page for MGnifams release-level plots.
- Link the page from the shared main navigation so it is discoverable from every page.
- Store the supplied PNG files as Django static assets.
- Render plots from structured metadata so future plots can be added without duplicating template markup.
- Keep the first version static and low-risk: no new database queries, background processing, charting libraries, or dynamic image generation.

## Non-Goals

- Do not regenerate the plots from database data.
- Do not add interactive chart filtering, zooming, or JavaScript chart libraries.
- Do not redesign the global navigation beyond adding the new internal link.
- Do not add placeholder sections for future plot categories until there are plots to show.

## Navigation

Add a `Statistics` link to the shared main navigation in `explorer/templates/explorer/base.html`.

Recommended placement:

1. `Home`
2. `Statistics`
3. Existing external links

This keeps internal site destinations grouped first. The existing `Available MGnifams` browse page is currently linked from the homepage rather than the main nav, so the new statistics page should not require a broader navigation restructure.

Do not add a homepage button for the first version; the statistics page should be linked only from the shared main navigation.

## Route and View

Add a new URL pattern:

- Path: `/statistics/`
- Name: `statistics`
- View: `views.statistics`
- Template: `explorer/statistics.html`

The view should render a small metadata structure, for example:

```python
plot_sections = [
    {
        "heading": "Family length distribution",
        "plots": [
            {
                "title": "Short family lengths",
                "filename": "explorer/statistics/family_length_short.png",
                "alt": "Stacked bar chart showing MGnifam family length distribution for HMM consensus lengths 1 to 700, split into annotated and unannotated families.",
                "caption": "Family length distribution for short HMM consensus lengths, binned by 25 amino acids.",
            }
        ],
    },
    {
        "heading": "Family size distribution",
        "plots": [
            {
                "title": "Medium family sizes",
                "filename": "explorer/statistics/family_size_medium.png",
                "alt": "Stacked bar chart showing MGnifam family size distribution for families with 21 to 100000 sequences, split into annotated and unannotated families.",
                "caption": "Family size distribution for medium-sized families, binned by 10000 sequences.",
            }
        ],
    },
]
```

The exact names can be adjusted during implementation, but the view should pass structured data rather than hard-coding each image block in the template.

## Static Assets

Copy the supplied images into:

- `explorer/static/explorer/statistics/family_length_short.png`
- `explorer/static/explorer/statistics/family_size_medium.png`

Reference them from the template using Django's `{% static %}` tag. These files will be served by the existing Django staticfiles and WhiteNoise setup after `collectstatic`.

## Page Content

The statistics page should extend `explorer/base.html` and use Visual Framework-compatible markup already used by the site.

Suggested content:

- Page heading: `MGnifams statistics`
- Short intro text explaining that these plots summarize the currently hosted MGnifams release.
- One section for `Family length distribution`.
- One section for `Family size distribution`.
- Each plot appears with:
  - A human-readable title.
  - The responsive image.
  - A caption.
  - A direct `Open image` link to the PNG for full-resolution viewing.

The page should not include empty future sections.

## Responsive Layout

The supplied plots are wide PNG charts, especially `family_length_short.png` at `2730 x 900`. The template and CSS should preserve readability on desktop while still behaving well on smaller screens.

Recommended behavior:

- Wrap each image in a horizontal overflow container.
- Render the image at its natural width up to the available viewport.
- Allow horizontal scrolling for very wide charts rather than shrinking labels until they become unreadable.
- Keep captions and headings outside the scrollable image area.

CSS can be added to `explorer/static/explorer/mgnifams.css` using page-specific classes such as:

- `.statistics-section`
- `.statistics-plot`
- `.statistics-plot__image-wrap`
- `.statistics-plot__image`

## Accessibility

- Each plot image must have descriptive `alt` text that states what the chart shows.
- Captions should summarize the plot in plain text.
- The `Open image` link should make full-resolution inspection available without relying on browser zoom.
- The page should work without JavaScript.

## Testing

Add focused Django tests for:

- `/statistics/` returns `200`.
- The `statistics` URL name resolves.
- The response includes both static image paths.
- The shared navigation includes the `Statistics` link.

Existing test command:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test
```

## Implementation Files

Expected files to change:

- `mgnifams_site/explorer/urls.py`
- `mgnifams_site/explorer/views.py`
- `mgnifams_site/explorer/templates/explorer/base.html`
- `mgnifams_site/explorer/templates/explorer/statistics.html`
- `mgnifams_site/explorer/static/explorer/mgnifams.css`
- `mgnifams_site/explorer/static/explorer/statistics/family_length_short.png`
- `mgnifams_site/explorer/static/explorer/statistics/family_size_medium.png`
- `mgnifams_site/explorer/tests.py`

## Risks and Mitigations

- Very wide chart labels may become unreadable if the images are forced to shrink. Use horizontal overflow around images.
- Adding a top-level nav link could crowd the existing navigation. Place only one short `Statistics` label near `Home`.
- Future plots could create template duplication. Use view-provided metadata and loop rendering from the first version.

## Acceptance Criteria

- Users can open `/statistics/` directly.
- The main navigation contains an internal `Statistics` link.
- Both supplied PNGs render on the statistics page.
- Each plot has a heading, caption, descriptive alt text, and direct full-resolution image link.
- The page remains usable on narrow screens.
- The Django test suite passes after implementation.
