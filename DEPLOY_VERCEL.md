# Deploy SKYGRID INDIA to Vercel

This repository now includes a Vercel Python entry point and root dependency file. A successful build is not the same as a fully reliable hosted simulation: Vercel Functions are serverless and ephemeral, so this app's in-memory fleet state, continuous simulation loop, WebSocket event stream, and local SQLite database are not guaranteed to persist or behave like the local development server.

## Deploy a preview

1. Push the entire `skygrid-india` directory to a GitHub repository (include `api/`, `backend/`, `requirements.txt`, and `vercel.json`). Do not commit `.env`, credentials, `.venv`, or local database files.
2. Import the repository in Vercel and deploy with the project root set to the repository root.
3. After deployment, open `/api/health` and `/docs` on the assigned domain.
4. Open the homepage and check every menu. If the dashboard loads but simulation state resets between requests, that is a serverless-state limitation, not a frontend issue.

CLI alternative from the repository root:

```powershell
npm install -g vercel
vercel login
vercel
```

Use `vercel --prod` only after the preview has been tested.

## Required before relying on a public live demo

- Move incident storage to a hosted PostgreSQL database. Set `DATABASE_URL` in Vercel Environment Variables to the provider's connection string. Confirm network access and TLS settings with the database provider.
- Move persistent simulation state and the simulation tick loop to a long-running backend (or redesign the simulator as request-driven/stateless). A serverless function's process memory is not durable.
- Replace the current WebSocket stream with polling or a supported external realtime service, because Vercel Functions do not act as a persistent WebSocket server.
- Configure `CORS_ORIGINS` to the exact deployed frontend origin if frontend and API are separated.
- Add rate limiting, request validation, logs, and end-to-end tests for the deployed URL.

## Safety and accuracy

SKYGRID INDIA is a simulation/research prototype. It is not certified aviation software, does not control real aircraft, and must not be used to authorize real flights. The India hazard, cable, restricted-zone, and vertiport records in this project are synthetic demonstration data, not official aeronautical information.
