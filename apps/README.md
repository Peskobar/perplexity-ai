# Apps

This folder contains the user-facing applications of the monorepo.

- `backend` – FastAPI service with JWT authentication and a proxy to Perplexity AI.
- `frontend` – React 19 dashboard built with Vite and Tailwind.

Each app can be started individually using pnpm:

```bash
pnpm --filter ./apps/backend dev
pnpm --filter ./apps/frontend dev
```

