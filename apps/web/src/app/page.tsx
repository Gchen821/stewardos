export default function Home() {
  const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "StewardOS";
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  return (
    <div className="flex min-h-screen flex-col bg-[radial-gradient(circle_at_top,_#f8fafc,_#e2e8f0_45%,_#cbd5e1)] text-slate-950">
      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col justify-center gap-10 px-6 py-16 sm:px-10 lg:px-12">
        <div className="max-w-3xl space-y-6">
          <p className="inline-flex rounded-full border border-slate-300 bg-white/70 px-4 py-1 text-sm font-medium text-slate-700 shadow-sm backdrop-blur">
            Full-stack container starter
          </p>
          <h1 className="text-5xl font-semibold tracking-tight text-slate-950 sm:text-6xl">
            {appName}
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-slate-700">
            Next.js front-end, FastAPI back-end, PostgreSQL, Redis and MinIO
            are wired into one `docker compose` workflow. This page is the
            default landing screen for local development.
          </p>
        </div>

        <div className="grid gap-5 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          <section className="rounded-3xl border border-slate-200 bg-white/80 p-8 shadow-xl shadow-slate-300/30 backdrop-blur">
            <h2 className="text-2xl font-semibold text-slate-950">
              Service endpoints
            </h2>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <a
                className="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition hover:border-slate-400 hover:bg-white"
                href={apiBaseUrl}
                target="_blank"
                rel="noreferrer"
              >
                <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">
                  API Root
                </p>
                <p className="mt-3 text-base font-semibold text-slate-900">
                  {apiBaseUrl}
                </p>
              </a>
              <a
                className="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition hover:border-slate-400 hover:bg-white"
                href={`${apiBaseUrl}/docs`}
                target="_blank"
                rel="noreferrer"
              >
                <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">
                  Swagger Docs
                </p>
                <p className="mt-3 text-base font-semibold text-slate-900">
                  {apiBaseUrl}/docs
                </p>
              </a>
              <a
                className="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition hover:border-slate-400 hover:bg-white"
                href={`${apiBaseUrl}/api/v1/health`}
                target="_blank"
                rel="noreferrer"
              >
                <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">
                  Health
                </p>
                <p className="mt-3 text-base font-semibold text-slate-900">
                  {apiBaseUrl}/api/v1/health
                </p>
              </a>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">
                  Compose
                </p>
                <p className="mt-3 text-base font-semibold text-slate-900">
                  docker compose up --build
                </p>
              </div>
            </div>
          </section>

          <section className="rounded-3xl border border-slate-900 bg-slate-950 p-8 text-slate-100 shadow-xl shadow-slate-400/20">
            <h2 className="text-2xl font-semibold">Included services</h2>
            <div className="mt-6 space-y-4 text-sm leading-7 text-slate-300">
              <p>Web: Next.js 16 on port 3000</p>
              <p>API: FastAPI on port 8000</p>
              <p>Database: PostgreSQL 16 on port 5432</p>
              <p>Cache: Redis 7 on port 6379</p>
              <p>Object storage: MinIO on ports 9000 / 9001</p>
            </div>
          </section>
        </div>

        <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
          <a
            className="flex h-12 w-full items-center justify-center rounded-full bg-slate-950 px-6 text-white transition hover:bg-slate-800 md:w-auto"
            href={`${apiBaseUrl}/docs`}
            target="_blank"
            rel="noreferrer"
          >
            Open API docs
          </a>
          <a
            className="flex h-12 w-full items-center justify-center rounded-full border border-slate-300 bg-white/70 px-6 text-slate-900 transition hover:bg-white md:w-auto"
            href="https://fastapi.tiangolo.com/"
            target="_blank"
            rel="noreferrer"
          >
            FastAPI docs
          </a>
        </div>
      </main>
    </div>
  );
}
