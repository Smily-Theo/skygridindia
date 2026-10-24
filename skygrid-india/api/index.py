"""Vercel Python entry point for the SKYGRID INDIA FastAPI application.

Note: Vercel Functions are ephemeral/serverless. In-memory simulation state,
background loops, WebSockets, and local SQLite persistence are not reliable
across invocations. See DEPLOY_VERCEL.md before deploying a public demo.
"""
from backend.app.main import app
