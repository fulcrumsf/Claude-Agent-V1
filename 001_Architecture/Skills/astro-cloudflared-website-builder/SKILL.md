---
name: astro-cloudflared-website-builder
description: This skill should be used when the user wants to build or plan an Astro website on Cloudflare Pages, replace a WordPress site with a static-first stack, or work through an Astro + Cloudflare + Wrangler website workflow.
---

# Astro Cloudflared Website Builder

## Purpose

This skill helps build a modern Astro + Cloudflare blog website workflow designed for:

- Content creators
- Blog websites
- Static-first architecture
- AI-assisted development
- Cloudflare hosting
- Claude Code workflows
- Beautiful animations with minimal JavaScript

The goal is to replace traditional WordPress + Elementor workflows with a fast, maintainable modern stack.

---

# Recommended Stack

## Core Framework

- Astro
- Tailwind CSS
- MDX
- Cloudflare Pages
- Wrangler CLI
- GitHub

## Optional Enhancements

- Keystatic CMS
- GSAP
- Motion One
- Lottie animations
- Cloudflare R2
- Cloudflare D1
- Cloudflare KV

---

# Install Requirements

## Install Node.js

Recommended:
- Node.js LTS version

Verify installation:

```bash
node -v
npm -v
```

---

# Install Git

Verify:

```bash
git --version
```

---

# Install Wrangler CLI

Official Cloudflare CLI.

```bash
npm install -g wrangler
```

Verify:

```bash
wrangler --version
```

---

# Login To Cloudflare

```bash
wrangler login
```

---

# Create Astro Cloudflare Project

Recommended command:

```bash
npm create cloudflare@latest
```

Choose:
- Framework: Astro
- Platform: Pages

Alternative direct setup:

```bash
npm create cloudflare@latest my-astro-site --framework=astro --platform=pages
```

---

# Enter Project Directory

```bash
cd my-astro-site
```

---

# Install Dependencies

```bash
npm install
```

---

# Install Tailwind CSS

```bash
npx astro add tailwind
```

---

# Install MDX Support

```bash
npx astro add mdx
```

---

# Install View Transitions

Astro supports View Transitions natively.

Reference:
https://docs.astro.build/en/guides/view-transitions/

---

# Recommended Animation Libraries

## Motion One

```bash
npm install motion
```

## GSAP

```bash
npm install gsap
```

## Lottie

```bash
npm install lottie-web
```

---

# Recommended Astro Structure

```text
src/
  components/
  layouts/
  pages/
  content/
    blog/
public/
  images/
```

---

# Content Collections

Recommended for blog posts.

Example:

```text
src/content/blog/my-post.mdx
```

Example frontmatter:

```md
---
title: "My First Post"
description: "Blog description"
publishDate: 2026-05-18
tags:
  - astro
  - cloudflare
heroImage: "/images/hero.jpg"
---
```

---

# Local Development

Run local dev server:

```bash
npm run dev
```

---

# Build Production Site

```bash
npm run build
```

---

# Deploy To Cloudflare Pages

Manual deploy:

```bash
wrangler pages deploy dist
```

Recommended:
- Connect GitHub repository
- Enable automatic deploys

Workflow:

```text
Git Push
→ Cloudflare Build
→ Global Deploy
```

---

# Recommended Workflow

## Local CMS Workflow

Suggested architecture:

```text
Docker CMS
→ MDX Generation
→ Git Commit
→ GitHub Push
→ Cloudflare Deploy
```

---

# Claude Code Instructions

Claude Code should:

- Generate Astro pages
- Create reusable components
- Use Tailwind CSS
- Prefer static-first architecture
- Use partial hydration only where necessary
- Keep JavaScript minimal
- Use View Transitions sparingly
- Optimize Lighthouse performance
- Avoid unnecessary React usage
- Prefer Astro islands architecture

---

# Recommended Astro Features

## Use For:

- Blog websites
- Landing pages
- Creator portfolios
- Embedded YouTube videos
- Affiliate content
- SEO-focused content

## Avoid Overengineering:

Do NOT:
- Turn every page into a SPA
- Add unnecessary client-side JavaScript
- Use excessive animations
- Add large frontend frameworks unless required

---

# Performance Goals

Target:

- Lighthouse 90+
- Minimal hydration
- Fast first contentful paint
- Static rendering by default

---

# Future Upgrades

Optional future additions:

- Cloudflare R2 image hosting
- Search indexing
- Newsletter system
- Keystatic admin panel
- AI-generated metadata
- Analytics dashboard
- Dynamic API routes

---

# Suggested Naming Convention

Use:

```text
PascalCase
```

Examples:

```text
BlogPostCard.astro
HeroSection.astro
FeaturedArticle.astro
MainLayout.astro
```

Folders:

```text
kebab-case
```

Examples:

```text
blog-posts/
landing-pages/
shared-components/
```

---

# Final Notes

This architecture is designed to:

- Replace WordPress + Elementor
- Reduce maintenance
- Improve performance
- Simplify hosting
- Enable AI-assisted development
- Keep the site visually modern without becoming bloated
