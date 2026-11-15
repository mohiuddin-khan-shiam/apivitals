# Contributor's Guide: Adding a New Public API

This guide walks you through adding a new public API to the **ApiVitals** catalog.

---

## Prerequisites

Before submitting an API, verify that it meets our inclusion criteria:

1. **Free Tier**: Must be free to access without requiring payment information or credit cards. APIs with no required authentication (`auth: none`) are preferred.
2. **Documented**: Must provide official, working documentation.
3. **Legal & Safe**: Must not serve illegal, adult, scraping-prohibited, or infringing content.
4. **Reliable**: Must have demonstrated reasonable availability and response stability.

---

## Step 1: Choose or Create a Category

Place your definition file in `apis/<category>/<api-slug>.yaml`.

Existing categories include:
- `weather`
- `geocoding`
- `science`
- `finance`
- `developer-tools`
- `books-literature`
- `entertainment`
- `government-data`
- `health-medicine`
- `food-nutrition`

If your API does not fit these categories, you may create a new subfolder in `apis/` with a descriptive kebab-case name.

---

## Step 2: Write the YAML Definition

Create `apis/<category>/<api-slug>.yaml`:

```yaml
id: cat-facts
name: Cat Facts Ninja
description: Daily random cat facts and trivia for developers and cat enthusiasts.
category: Entertainment & Media
homepage: https://catfact.ninja
documentation: https://catfact.ninja
auth: none
https: true
cors: true
endpoints:
  - name: Random Fact
    path: https://catfact.ninja/fact
    method: GET
    expected_status: 200
    expected_content_type: json
tags:
  - animals
  - cats
  - trivia
license: MIT
rate_limit: Polite non-commercial use
```

---

## Step 3: Validate Your Definition Locally

Run the validation command:

```bash
uv run apivitals validate
```

If your YAML has syntax errors or misses required fields, the CLI will output clear line numbers and descriptions.

---

## Step 4: Test a Live Probe

Test that ApiVitals can successfully probe your endpoint:

```bash
uv run apivitals probe <api-slug>
```

You should see output similar to:

```text
Probing API Cat Facts Ninja (cat-facts)...
State: HEALTHY
Latency: 142.3 ms
HTTP Status: 200
CORS Detected: True
SSL Cert Expiry: 82 days remaining
```

---

## Step 5: Submit a Pull Request

Create a branch and commit your file with a conventional commit:

```bash
git checkout -b add-cat-facts
git add apis/entertainment/cat-facts.yaml
git commit -m "feat(api): add cat facts ninja endpoint"
git push origin add-cat-facts
```

Our automated CI will validate your file and run synthetic checks.
