# SKYGRID INDIA — API connection fix

This patch makes the dashboard resilient when the optional `/api/incidents` endpoint fails and improves error messages so the failing endpoint is visible. It does not conceal a genuine backend failure.

## Deploy
1. Extract this ZIP.
2. Replace the existing project files with these patched files (or copy the changed `backend/app/static/index.html` into your existing repository).
3. From the project root, redeploy using `vercel.cmd --prod` (or `vercel --prod`).
4. Open these endpoints on the deployed domain:
   - `/api/health`
   - `/api/overview`
   - `/api/vehicles`
   - `/api/obstacles`
   - `/api/incidents`
5. Reload the dashboard. If a required endpoint fails, the toast now names the endpoint and HTTP/network error.

## Important
Vercel serverless functions do not guarantee durable process memory, long-running simulation loops, WebSocket service, or persistent local SQLite storage. This patch improves frontend diagnostics and resilience; it does not turn the demo into production aviation software or solve serverless persistence. For a stable multi-request simulation, use a persistent hosted database and a suitable long-running backend or redesign the simulation to be request-driven.
