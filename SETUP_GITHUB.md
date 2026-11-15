# GitHub Setup & Deployment Guide for ApiVitals

This guide contains exact, copy-pasteable instructions to publish **ApiVitals** to GitHub, configure automated daily updates, enable GitHub Pages, and ensure that your daily automated commits appear on your GitHub contribution graph.

---

## Step 1: Create the Empty GitHub Repository

1. Go to [https://github.com/new](https://github.com/new).
2. **Repository name**: Enter `apivitals` (exact slug).
3. **Visibility**: Select **Public**.
4. **Initialize this repository with**:
   - ⚠️ **DO NOT check** "Add a README file".
   - ⚠️ **DO NOT check** "Add .gitignore".
   - ⚠️ **DO NOT check** "Choose a license".
   *(The repository must be completely empty so our existing files become the root commit).*
5. Click **Create repository**.

---

## Step 2: Initialize Git and Push to GitHub

Open your terminal in the project directory (`ProjectX`) and run the following commands (replace `YOUR_GITHUB_USERNAME` with your actual GitHub username):

```bash
# Initialize local git repository
git init -b main

# Stage all files
git add .

# Create the initial commit
git commit -m "feat: initial release of ApiVitals v0.1.0"

# Add your GitHub remote
git remote add origin https://github.com/mohiuddin-khan-shiam/apivitals.git

# Push to main branch
git push -u origin main
```

---

## Step 3: Configure Repository Variables for Contribution Graph Credit

By default, GitHub Actions commits authored by `github-actions[bot]` **do not count toward your personal GitHub contribution graph** (the green squares).

To make automated daily updates appear under your profile:

### How to Find Your GitHub No-Reply Email:
1. Go to [GitHub Email Settings](https://github.com/settings/emails).
2. Look at the section **"Keep my email addresses private"**.
3. You will see an address formatted like:
   `12345678+username@users.noreply.github.com`
4. Copy this email address.

### Set the Variables in Your Repository:
1. In your `apivitals` repository on GitHub, navigate to:
   **Settings** &rarr; **Secrets and variables** &rarr; **Actions** &rarr; **Variables** tab (make sure it's the **Variables** tab, not Secrets).
2. Click **New repository variable**:
   - **Name**: `GIT_AUTHOR_NAME`
   - **Value**: `Mohiuddin Khan Shiam` (or simply `mohiuddin-khan-shiam` — do not type "your name/")
   - Click **Add variable**.
3. Click **New repository variable** again:
   - **Name**: `GIT_AUTHOR_EMAIL`
   - **Value**: `147746955+mohiuddin-khan-shiam@users.noreply.github.com`
   - Click **Add variable**.

> 💡 *Now, every automated daily update commit will be authored by your account, automatically earning you daily contribution activity on your profile!*

---

## Step 4: Configure GitHub Repository Settings

### 1. Enable Actions Read & Write Permissions
1. Navigate to: **Settings** &rarr; **Actions** &rarr; **General**.
2. Scroll down to **Workflow permissions**.
3. Select **"Read and write permissions"**.
4. Check **"Allow GitHub Actions to create and approve pull requests"**.
5. Click **Save**.

### 2. Configure GitHub Pages
1. Navigate to: **Settings** &rarr; **Pages**.
2. Under **Build and deployment** &rarr; **Source**:
   Select **GitHub Actions** (not "Deploy from a branch").
3. The deployment workflow (`.github/workflows/pages.yml`) will handle everything automatically.

### 3. Important Note Regarding "Your main branch isn't protected"
GitHub displays a warning recommending branch protection rules. For **ApiVitals**, please keep this critical detail in mind:
- **Do NOT enable** "Require a pull request before merging" on `main` without adding a bypass.
- **Why?** Our automated workflow (`daily-update.yml`) runs on a daily schedule and pushes updated health statistics and benchmarks directly to `main`. If you require pull requests to push to `main`, GitHub Actions will be blocked with a permissions error when pushing daily data.
- **Recommended Protection (if desired)**: If you want protection, go to **Settings** &rarr; **Rules** &rarr; **Rulesets** &rarr; **New branch ruleset**:
  - Name: `Protect main`
  - Target branches: `Include default branch`
  - Check **"Block force pushes"** and **"Restrict deletions"**.
  - Leave "Require a pull request before merging" **unchecked**.

### 4. Enable Discussions (Recommended)
1. Navigate to: **Settings** &rarr; **General** &rarr; Scroll down to **Features**.
2. Check the box for **Discussions**.

---

## Step 5: How to Trigger the Daily Run Manually

To test the automated pipeline right now:

1. Go to your repository on GitHub: [https://github.com/mohiuddin-khan-shiam/apivitals](https://github.com/mohiuddin-khan-shiam/apivitals)
2. Click the **Actions** tab at the top.
3. In the left sidebar list of workflows, click on **"Daily API Health & Benchmark Update"** (or open: [https://github.com/mohiuddin-khan-shiam/apivitals/actions/workflows/daily-update.yml](https://github.com/mohiuddin-khan-shiam/apivitals/actions/workflows/daily-update.yml)).
4. On the right side above the run history, look for the gray box that says: **"This workflow has a `workflow_dispatch` event trigger."**
5. Click the **Run workflow** dropdown button.
6. Keep `Branch: main` selected and click the green **Run workflow** button.
7. Refresh the page after 5 seconds: you will see a yellow running circle for your manual run.
8. Wait ~60 seconds:
   - The job will turn into a green checkmark `✓`.
   - Go to the **Code** tab: you will see a fresh commit authored by you: `data: update API health vitals and benchmarks (YYYY-MM-DD)`.
   - Check your profile to see the new green contribution square!
5. Once the run finishes with a green checkmark:
   - Go to your repository code tab.
   - Look at the latest commit: you will see a conventional commit formatted as:
     `data: update API health vitals and benchmarks (YYYY-MM-DD)`.
   - Click on `STATUS.md` and verify that the latency and uptime metrics are freshly updated.
   - Go to your personal GitHub profile to confirm that the commit appears on your contribution graph!

---

## Step 6: Verify GitHub Scheduled Workflows (Keepalive Note)

> ⚠️ **GitHub Inactivity Caveat**: GitHub automatically disables scheduled cron workflows if a repository has had **no activity for 60 consecutive days**.
>
> **How ApiVitals avoids this**: Because our `daily-update.yml` runs daily and pushes real, verified latency and status metric updates to the default `main` branch, the repository remains continuously active! As long as automated commits land on `main`, the 60-day inactivity timer never triggers.

---

## Step 7: Launch & Promotion Checklist

To attract real users, contributors, and GitHub stars, follow this proven open-source launch checklist:

### 1. Hacker News ("Show HN")
- **Title**: `Show HN: ApiVitals – Living health radar and latency benchmarks for free public APIs`
- **Post Structure**:
  - *Problem*: `public-apis` has 300k+ stars but 40% of the links are dead or paywalled.
  - *Solution*: We built ApiVitals, an automated living catalog that tests public APIs daily for latency, CORS, and SSL.
  - *Features*: Zero-config Python CLI (`pip install apivitals`), offline SQLite/JSON datasets, and a zero-dependency static dashboard.
  - *Link*: Link to your GitHub repository and GitHub Pages site.

### 2. Reddit Communities
Share the project in:
- `r/Python`: "I built an open-source CLI & daily health radar for free public APIs"
- `r/webdev`: "Tired of finding dead APIs on GitHub? Here's a live-benchmarked directory with verified CORS support"
- `r/opensource`: "ApiVitals: A self-maintaining open-source directory of public APIs"

### 3. Dev.to / Hashnode / Medium
Write a short post: *"Why Most Public API Lists on GitHub Are Broken (And How We Built an Automated Health Radar to Fix Them)"*. Highlight the architecture, the GitHub Actions cron automation, and invite readers to submit their favorite APIs via simple YAML PRs.

### 4. Twitter / X / Bluesky / LinkedIn
- Post a short demo video or GIF showing `apivitals list` in the terminal and the dark-mode static dashboard.
- Tag relevant open-data maintainers (e.g. `@Open_Meteo`).
