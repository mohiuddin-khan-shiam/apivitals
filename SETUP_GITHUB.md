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
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/apivitals.git

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
   **Settings** &rarr; **Secrets and variables** &rarr; **Actions** &rarr; **Variables** tab (not Secrets).
2. Click **New repository variable**:
   - **Name**: `GIT_AUTHOR_NAME`
   - **Value**: Your real name or GitHub username (e.g., `Jane Doe`)
   - Click **Add variable**.
3. Click **New repository variable** again:
   - **Name**: `GIT_AUTHOR_EMAIL`
   - **Value**: Your noreply email (e.g., `12345678+username@users.noreply.github.com`)
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

### 3. Enable Discussions (Recommended)
1. Navigate to: **Settings** &rarr; **General** &rarr; Scroll down to **Features**.
2. Check the box for **Discussions**.

---

## Step 5: Trigger the First Daily Run & Verify

1. Go to the **Actions** tab in your repository.
2. In the left sidebar, click on **"Daily API Health & Benchmark Update"**.
3. Click the **"Run workflow"** dropdown on the right, select branch `main`, and click **Run workflow**.
4. Wait approximately 60–90 seconds for the job to complete.
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
