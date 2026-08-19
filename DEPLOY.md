# Publish your premium GitHub profile

Your GitHub profile README appears when a **public repository has exactly the same name as your username**.

## 1. Create the profile repository

1. Open <https://github.com/new>
2. Set **Repository name** to `muhammadashir0`
3. Set visibility to **Public**
4. Check **Add a README file**
5. Select **Create repository**

## 2. Upload this package

Upload both items while preserving the folder structure:

```text
muhammadashir0/
├── README.md
└── assets/
    └── profile-banner.svg
```

On GitHub, choose **Add file → Upload files**, drag in `README.md` and the `assets` folder, then commit to `main`.

## 3. Improve the profile sidebar

Open <https://github.com/settings/profile> and use:

- **Name:** Muhammad Ashir
- **Bio:** `Data Scientist · Machine Learning · Responsible AI | Building explainable, globally useful systems`
- **Location:** `Frankfurt, Hesse, Germany`
- **Website:** `https://datascienceportfol.io/ashirali0998`
- **LinkedIn:** Keep the existing LinkedIn link
- **Status:** `🌍 Building responsible AI` (optional)

Also correct the profile timezone if GitHub shows `UTC -12:00`; Germany uses `Europe/Berlin` (CET/CEST).

## 4. Curate pinned repositories

On the profile page, select **Customize your pins**. Recommended order after the projects contain substantive work:

1. `CertifAI` — strongest, differentiated Responsible AI concept
2. `netflix-eda` — current completed data-analysis example
3. `DeepLearningWithPytorch` — pin after adding notebooks, README, and results
4. A future end-to-end deployed ML project

Do not pin empty repositories. Until `CertifAI` and `DeepLearningWithPytorch` contain code and documentation, pin `netflix-eda` only rather than presenting empty work as finished.

## 5. High-impact next upgrades

- Add a clear README, demo image, architecture, setup steps, and license to `CertifAI`.
- Add 2–3 polished notebooks and learning outcomes to `DeepLearningWithPytorch`.
- Add screenshots/plots and a concise executive summary to `netflix-eda`.
- Create one deployed project with a live demo and measurable evaluation metrics.
- Add repository topics (`machine-learning`, `responsible-ai`, `data-science`, etc.).
- Commit consistently; profile widgets become more credible when backed by real activity.

## Notes

- The README uses live cards from `github-readme-stats.vercel.app` and `github-readme-activity-graph.vercel.app`; GitHub loads these over the web.
- The custom banner is stored locally in the repository, so its main visual does not depend on a third-party image host.
- If a live card is temporarily rate-limited, it may disappear until the provider recovers; the rest of the profile remains intact.
