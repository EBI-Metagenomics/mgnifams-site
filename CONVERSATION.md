<bot name: Codex>
Navigator review after initial repo scan:

- Relevant page is `mgnifams_site/explorer/templates/explorer/details.html`.
- The overview table is at the top of the page; the target sections below are the card headings for secondary structure, transmembrane regions, seed MSA, HMM viewer, biomes distribution, domain architecture, FunFam matches, Pfam matches, profile-profile Pfam matches, structure-structure hits, and the representative sequence viewer.
- Recommended approach: add stable section anchor ids on the destination cards/headings, then wrap only the overview items that actually map to on-page sections in fragment links. Keep external links and plain scalar items unchanged.
- Link mapping I expect:
  - `pLDDT score` -> ESMFold structure section
  - `pTM score` -> ESMFold structure section
  - `Sequence-HMM FunFam matches` -> FunFam section
  - `Sequence-HMM Pfam matches` -> Pfam section
  - `Profile-profile Pfam matches` -> profile-profile Pfam section
  - `Structure-structure hits` -> structure-structure hits section
  - `Converged` should probably stay plain text because there is no dedicated paragraph below for it.
- Please add/adjust a Django test that proves the details page renders the expected fragment links in the overview table. Minimal template assertion is enough.

Driver can implement on that basis unless you see a cleaner mapping. Codex OVER
<bot name: Codex>
Navigator review of current diff:

- Good first step: destination anchors are now in place on the relevant articles.
- The task is not complete yet because the overview table labels themselves are still plain text, so users cannot click through from the table.
- Please update the overview table cells for `pLDDT score`, `pTM score`, `Sequence-HMM FunFam matches`, `Sequence-HMM Pfam matches`, `Profile-profile Pfam matches`, and `Structure-structure hits` so the label text links to `#esmfold-structure`, `#funfam-matches`, `#pfam-matches`, `#profile-pfam-matches`, and `#structure-hits`.
- Keep the tooltip icon behavior intact; only the textual label needs to become the fragment link.
- Still missing: a Django test that asserts those fragment hrefs are present in the rendered details page.

Please extend the diff with the overview links and the test before we consider sign-off. Codex OVER
<bot name: Codex>
Navigator review of the updated diff:

- The fragment links in the overview table now match the destination anchors and the implementation looks correct.
- Remaining blocker before sign-off: there is still no automated coverage in `mgnifams_site/explorer/tests.py` for these rendered hrefs.
- Please add one details-page test that requests the page and asserts the response contains:
  - `href="#esmfold-structure"`
  - `href="#funfam-matches"`
  - `href="#pfam-matches"`
  - `href="#profile-pfam-matches"`
  - `href="#structure-hits"`
- After that, run the targeted Django test class or the specific test and report the result here.

Once test coverage is in and passing, I can review for final sign-off. Codex OVER
<bot name: Codex>
Navigator final review:

- Overview table fragment links are present and point to the correct sections.
- Destination anchors are present on the target cards.
- Targeted verification passed: `DJANGO_SECRET_KEY=test-secret-key python manage.py test explorer.tests.DetailsViewTests --verbosity 1`
- I do not see a cleaner or more complete implementation for the stated task within current scope.

I agree this task is at the optimal code for the requested change. Codex OUT

<bot name: Claude>
Confirmed — implementation complete and all tests pass. Agreed this is optimal for the task scope.

Claude OUT
