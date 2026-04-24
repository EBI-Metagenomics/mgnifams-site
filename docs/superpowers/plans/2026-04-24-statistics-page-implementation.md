# MGnifams Statistics Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an expandable `/statistics/` page that displays the two supplied MGnifams release-level plot images and links to it from the main navigation and homepage.

**Architecture:** Add a small Django view that passes structured plot metadata into a new template. Store supplied PNGs as static assets and render them through a reusable template loop so future plots can be added by extending metadata, not duplicating markup.

**Tech Stack:** Django 4.2 templates, Django staticfiles, existing Visual Framework CSS classes, existing `explorer` app tests using `django.test.TestCase`.

**User Constraint:** Do not run Git commands. Version control operations are intentionally omitted.

---

## File Structure

- Modify `mgnifams_site/explorer/tests.py`
  - Add focused tests for the statistics URL, static assets, rendered image paths, main navigation link, and homepage entry point.
- Modify `mgnifams_site/explorer/views.py`
  - Add `STATISTICS_PLOT_SECTIONS` metadata and a `statistics` view.
- Modify `mgnifams_site/explorer/urls.py`
  - Add the `/statistics/` route named `statistics`.
- Modify `mgnifams_site/explorer/storage.py`
  - Keep development and test rendering working when new app static files have not been collected into an existing static manifest yet.
- Create `mgnifams_site/explorer/templates/explorer/statistics.html`
  - Render the page from `plot_sections` using a template loop.
- Modify `mgnifams_site/explorer/templates/explorer/base.html`
  - Add a `Statistics` link after `Home` in the shared main navigation.
- Modify `mgnifams_site/explorer/templates/explorer/index.html`
  - Add a secondary `View statistics` link near `View available MGnifams`.
- Modify `mgnifams_site/explorer/static/explorer/mgnifams.css`
  - Add page-specific image overflow and caption styles.
- Create directory `mgnifams_site/explorer/static/explorer/statistics/`
  - Copy `family_length_short.png` and `family_size_medium.png` from `/home/vangelis/Downloads/images/`.

---

## Task Progress

- [x] Task 1: Add Failing Statistics Tests
- [x] Task 2: Add the Supplied Static PNG Assets
- [x] Task 3: Add the Statistics View and URL
- [x] Task 4: Create the Statistics Template
- [x] Task 5: Add Navigation and Homepage Links
- [ ] Task 6: Add Responsive Statistics Styles
- [ ] Task 7: Final Verification

---

### Task 1: Add Failing Statistics Tests

**Files:**
- Modify: `mgnifams_site/explorer/tests.py`

- [x] **Step 1: Add the staticfiles finder import**

Add this import near the existing Django imports:

```python
from django.contrib.staticfiles import finders
```

The top import block should include:

```python
from unittest.mock import MagicMock, patch

import requests.exceptions
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
```

- [x] **Step 2: Add the new test class**

Insert this class after `IndexViewTests` and before `DetailsViewTests`:

```python
class StatisticsViewTests(TestCase):
    def test_statistics_url_returns_200(self):
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)

    def test_statistics_context_lists_plot_sections(self):
        response = self.client.get(reverse('statistics'))
        self.assertIn('plot_sections', response.context)
        self.assertEqual(
            [section['heading'] for section in response.context['plot_sections']],
            ['Family length distribution', 'Family size distribution'],
        )

    def test_statistics_page_renders_supplied_plot_paths(self):
        response = self.client.get(reverse('statistics'))
        self.assertContains(response, 'explorer/statistics/family_length_short.png')
        self.assertContains(response, 'explorer/statistics/family_size_medium.png')
        self.assertContains(response, 'Open image', count=2)

    def test_statistics_static_assets_exist(self):
        self.assertIsNotNone(finders.find('explorer/statistics/family_length_short.png'))
        self.assertIsNotNone(finders.find('explorer/statistics/family_size_medium.png'))

    def test_main_navigation_links_to_statistics(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, f'href="{reverse("statistics")}"')
        self.assertContains(response, 'Statistics')

    def test_index_links_to_statistics_entry_point(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, f'href="{reverse("statistics")}"')
        self.assertContains(response, 'View statistics')
```

- [x] **Step 3: Run the new tests and confirm they fail for the expected reason**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test explorer.tests.StatisticsViewTests
```

Expected result: failures/errors because the `statistics` URL name and static files do not exist yet. The important expected error is:

```text
django.urls.exceptions.NoReverseMatch: Reverse for 'statistics' not found.
```

---

### Task 2: Add the Supplied Static PNG Assets

**Files:**
- Create: `mgnifams_site/explorer/static/explorer/statistics/family_length_short.png`
- Create: `mgnifams_site/explorer/static/explorer/statistics/family_size_medium.png`

- [x] **Step 1: Create the statistics static asset directory**

Run from the repository root:

```bash
mkdir -p mgnifams_site/explorer/static/explorer/statistics
```

- [x] **Step 2: Copy the supplied PNG files into the app static directory**

Run from the repository root:

```bash
cp /home/vangelis/Downloads/images/family_length_short.png mgnifams_site/explorer/static/explorer/statistics/family_length_short.png
cp /home/vangelis/Downloads/images/family_size_medium.png mgnifams_site/explorer/static/explorer/statistics/family_size_medium.png
```

- [x] **Step 3: Verify the files exist**

Run:

```bash
test -f mgnifams_site/explorer/static/explorer/statistics/family_length_short.png
test -f mgnifams_site/explorer/static/explorer/statistics/family_size_medium.png
```

Expected result: both commands exit with status `0` and print no output.

- [x] **Step 4: Run the static asset test**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test explorer.tests.StatisticsViewTests.test_statistics_static_assets_exist
```

Expected result:

```text
Ran 1 test
OK
```

---

### Task 3: Add the Statistics View and URL

**Files:**
- Modify: `mgnifams_site/explorer/views.py`
- Modify: `mgnifams_site/explorer/urls.py`

- [x] **Step 1: Add structured plot metadata and the view**

In `mgnifams_site/explorer/views.py`, add this block after `index` and before `translate_mgyf_to_int_id`:

```python
STATISTICS_PLOT_SECTIONS = [
    {
        'heading': 'Family length distribution',
        'plots': [
            {
                'title': 'Short family lengths',
                'filename': 'explorer/statistics/family_length_short.png',
                'alt': (
                    'Stacked bar chart showing MGnifam family length distribution for HMM consensus '
                    'lengths 1 to 700, split into annotated and unannotated families.'
                ),
                'caption': 'Family length distribution for short HMM consensus lengths, binned by 25 amino acids.',
            }
        ],
    },
    {
        'heading': 'Family size distribution',
        'plots': [
            {
                'title': 'Medium family sizes',
                'filename': 'explorer/statistics/family_size_medium.png',
                'alt': (
                    'Stacked bar chart showing MGnifam family size distribution for families with '
                    '21 to 100000 sequences, split into annotated and unannotated families.'
                ),
                'caption': 'Family size distribution for medium-sized families, binned by 10000 sequences.',
            }
        ],
    },
]


def statistics(request):
    return render(
        request,
        'explorer/statistics.html',
        {
            'plot_sections': STATISTICS_PLOT_SECTIONS,
        },
    )
```

- [x] **Step 2: Add the URL route**

In `mgnifams_site/explorer/urls.py`, add the `statistics` path immediately after the index route:

```python
urlpatterns = [
    path('', views.index, name='index'),
    path('statistics/', views.statistics, name='statistics'),
    path('mgnifams_list/', views.mgnifams_list, name='mgnifams_list'),
    path('mgnifams_data/', views.mgnifams_data, name='mgnifams_data'),
    path('details/<str:pk>/', views.details, name='details'),
    path('serve_blob/<int:pk>/<str:column_name>/', views.serve_blob_as_file, name='serve_blob_as_file'),
]
```

- [x] **Step 3: Run the statistics tests and confirm the next expected failure**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test explorer.tests.StatisticsViewTests
```

Expected result: the static asset test should pass, and the URL should resolve. The page-rendering tests should still error because the template does not exist yet:

```text
django.template.exceptions.TemplateDoesNotExist: explorer/statistics.html
```

---

### Task 4: Create the Statistics Template

**Files:**
- Modify: `mgnifams_site/explorer/storage.py`
- Create: `mgnifams_site/explorer/templates/explorer/statistics.html`

- [x] **Step 1: Add a manifest-storage fallback for newly added app static files**

In `mgnifams_site/explorer/storage.py`, update `ManifestOptionalStaticFilesStorage` to:

```python
class ManifestOptionalStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Whitenoise storage with manifest_strict=False so that missing or not-yet-built
    manifests don't raise errors in development or tests.  In production, after
    `collectstatic` is run, files are served with content-hash cache-busting and
    gzip/brotli compression as normal.
    """

    manifest_strict = False

    def stored_name(self, name):
        try:
            return super().stored_name(name)
        except ValueError:
            return self.clean_name(name)
```

- [x] **Step 2: Create the template**

Create `mgnifams_site/explorer/templates/explorer/statistics.html` with this content:

```django
{% extends "explorer/base.html" %}
{% load static %}

{% block title %}
    MGnifams statistics
{% endblock title %}

{% block content %}
<section class="vf-content | vf-stack vf-stack--600">
    <header class="vf-stack vf-stack--400">
        <h2>MGnifams statistics</h2>
        <p>
            These plots summarize the currently hosted MGnifams release and
            show how families are distributed by length, size, and annotation status.
        </p>
    </header>

    {% for section in plot_sections %}
        <section class="statistics-section | vf-stack vf-stack--400" aria-labelledby="statistics-section-{{ forloop.counter }}">
            <h3 id="statistics-section-{{ forloop.counter }}">{{ section.heading }}</h3>

            {% for plot in section.plots %}
                {% static plot.filename as plot_url %}
                <figure class="statistics-plot | vf-stack vf-stack--400">
                    <h4>{{ plot.title }}</h4>
                    <div class="statistics-plot__image-wrap">
                        <img class="statistics-plot__image" src="{{ plot_url }}" alt="{{ plot.alt }}">
                    </div>
                    <figcaption class="statistics-plot__caption">{{ plot.caption }}</figcaption>
                    <p><a class="vf-link" href="{{ plot_url }}">Open image</a></p>
                </figure>
            {% endfor %}
        </section>
    {% endfor %}
</section>
{% endblock content %}
```

- [x] **Step 3: Run the statistics tests and confirm navigation/homepage failures remain**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test explorer.tests.StatisticsViewTests
```

Expected result: route, context, static asset, and plot rendering tests should pass. The remaining failures should be the tests expecting the main navigation link and homepage entry point.

---

### Task 5: Add Navigation and Homepage Links

**Files:**
- Modify: `mgnifams_site/explorer/templates/explorer/base.html`
- Modify: `mgnifams_site/explorer/templates/explorer/index.html`

- [x] **Step 1: Add `Statistics` after `Home` in the shared nav**

In `mgnifams_site/explorer/templates/explorer/base.html`, update the first part of the nav list to:

```django
        <ul class="vf-navigation__list | vf-list | vf-cluster__inner">
            <li class="vf-navigation__item">
                <a href="{% url "index" %}"
                    class="vf-navigation__link">Home</a>
            </li>
            <li class="vf-navigation__item">
                <a href="{% url "statistics" %}"
                    class="vf-navigation__link">Statistics</a>
            </li>
            <li class="vf-navigation__item">
                <a href="https://www.ebi.ac.uk/metagenomics/proteins/"
                    target="_blank"
                    class="vf-navigation__link">
                    <i class="icon icon-common icon-external-link-alt"></i>
                    Protein Landing Page
                </a>
            </li>
```

- [x] **Step 2: Add a homepage statistics button near the browse action**

In `mgnifams_site/explorer/templates/explorer/index.html`, update the search form action row to:

```django
        <input type="submit" value="Go to Details" class="vf-button vf-button--primary">
        <a href="{% url 'mgnifams_list' %}" class="vf-button vf-button--secondary">View available MGnifams</a>
        <a href="{% url 'statistics' %}" class="vf-button vf-button--secondary">View statistics</a>
        <button id="example-btn" type="button" class="vf-button vf-button--secondary">Example</button>
```

- [x] **Step 3: Run the statistics tests**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test explorer.tests.StatisticsViewTests
```

Expected result:

```text
Ran 6 tests
OK
```

---

### Task 6: Add Responsive Statistics Styles

**Files:**
- Modify: `mgnifams_site/explorer/static/explorer/mgnifams.css`

- [ ] **Step 1: Append page-specific CSS**

Append this CSS to `mgnifams_site/explorer/static/explorer/mgnifams.css`:

```css
.statistics-section {
    margin-top: 2rem;
}

.statistics-plot {
    margin-top: 1rem;
}

.statistics-plot__image-wrap {
    max-width: 100%;
    overflow-x: auto;
    border: 1px solid #d0d0ce;
    background: #ffffff;
}

.statistics-plot__image {
    display: block;
    width: auto;
    max-width: none;
    height: auto;
}

.statistics-plot__caption {
    color: #54585a;
    font-size: 16px;
}
```

- [ ] **Step 2: Run the focused tests again**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test explorer.tests.StatisticsViewTests
```

Expected result:

```text
Ran 6 tests
OK
```

---

### Task 7: Final Verification

**Files:**
- Verify all files touched by prior tasks.

- [ ] **Step 1: Run the full Django test suite**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key python manage.py test
```

Expected result:

```text
OK
```

- [ ] **Step 2: Run Ruff on the Django project**

Run from the repository root:

```bash
ruff check mgnifams_site
```

Expected result:

```text
All checks passed!
```

- [ ] **Step 3: Manually smoke-test the page in the dev server**

Run:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key DJANGO_DEBUG=True python manage.py runserver 8000
```

Open:

```text
http://127.0.0.1:8000/statistics/
```

Expected result:

- The page loads with the shared MGnifams header and navigation.
- `Statistics` appears after `Home` in the main nav.
- The page title is `MGnifams statistics`.
- Both plot sections are visible.
- Each plot has a caption and an `Open image` link.
- Narrowing the browser keeps headings and captions readable, and wide images can be inspected with horizontal scrolling.

Stop the dev server with `Ctrl-C` after the smoke test.

---

## Spec Coverage Review

- `/statistics/` route: Task 3.
- Static PNG hosting: Task 2.
- Structured metadata for future plots: Task 3.
- Reusable template loop: Task 4.
- Main nav link after `Home`: Task 5.
- Homepage entry point: Task 5.
- Responsive wide-image behavior: Task 6.
- Alt text, captions, and full-resolution image links: Tasks 3 and 4.
- Focused Django tests: Task 1 through Task 5.
- Full verification: Task 7.
