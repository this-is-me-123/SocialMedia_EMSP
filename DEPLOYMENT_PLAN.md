# Deployment Plan: Hybrid Stack (Railway + Vercel + Supabase + Fooocus)

## Overview
This plan describes how to deploy a modern web project using:
- **Railway** for WordPress/PHP backend
- **Vercel** for React/Next.js frontend
- **Supabase** for database, authentication, and real-time features
- **Fooocus** for AI/ML image/video generation

---

## 1. Railway: WordPress/PHP Backend
- Prepare a `Dockerfile` or configure Railway’s PHP buildpack
- Push your WordPress code and plugins to GitHub/GitLab
- Set environment variables (DB creds, WP salts, etc.) in Railway dashboard
- Deploy and verify WordPress site

## 2. Vercel: Modern JS Frontend
- Create a new Vercel project for your React/Next.js frontend
- Set environment variables to connect to Railway (API) and Supabase (DB/Auth)
- Deploy via GitHub/GitLab/Bitbucket or CLI
- Verify frontend connects to backend and DB

## 3. Supabase: Database/Auth/Realtime
- Create a new Supabase project
- Set up tables, authentication, and storage as needed
- Obtain API keys and connection strings
- Integrate Supabase with both Railway and Vercel

## 4. Fooocus: AI/ML Service
- Deploy Fooocus on a GPU VM or managed service
- Expose API endpoint for image/video/AI tasks
- Connect from backend (Railway) or serverless (Vercel)

---

## Integration Checklist
- [ ] Railway backend endpoints accessible from Vercel frontend
- [ ] Supabase credentials securely shared between backend and frontend
- [ ] Fooocus API reachable from backend/frontend as needed
- [ ] All environment variables documented and set in each platform

---

## Post-Deployment
- Test all integrations (API, DB, Auth, AI)
- Monitor logs and set up alerting on all platforms
- Document deployment and rollback procedures

---

For detailed, step-by-step guides or platform-specific configs, see the platform documentation or request a custom walkthrough.
