/// <reference types="vite/client" />
import type { ReactNode } from 'react'
import { Link, Outlet, createRootRoute, HeadContent, Scripts } from '@tanstack/react-router'
import appCss from '../styles/app.css?url'

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { title: 'SMC AI — Pilotage' },
    ],
    links: [{ rel: 'stylesheet', href: appCss }],
  }),
  component: RootComponent,
})

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  )
}

function RootDocument({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="fr">
      <head>
        <HeadContent />
      </head>
      <body>
        <nav className="nav">
          <span className="brand">⚡ SMC AI</span>
          <Link to="/" className="link" activeProps={{ className: 'link active' }} activeOptions={{ exact: true }}>
            Dashboard
          </Link>
          <Link to="/backtests" className="link" activeProps={{ className: 'link active' }}>
            Backtests
          </Link>
          <Link to="/data" className="link" activeProps={{ className: 'link active' }}>
            Données
          </Link>
          <Link to="/settings" className="link" activeProps={{ className: 'link active' }}>
            Paramètres
          </Link>
        </nav>
        {children}
        <Scripts />
      </body>
    </html>
  )
}
