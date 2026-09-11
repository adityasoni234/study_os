import { Component, type ReactNode } from 'react'
import { BrowserRouter, Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { AppProvider } from '@/state/AppContext'
import { AuthProvider, useAuth } from '@/state/AuthContext'
import { Logo } from '@/lib/icons'
import { AppShell } from '@/components/layout/AppShell'
import Landing from '@/pages/Landing'
import Auth from '@/pages/Auth'
import Home from '@/pages/Home'
import Roadmaps from '@/pages/Roadmaps'
import RoadmapDetail from '@/pages/RoadmapDetail'
import TutorHub from '@/pages/TutorHub'
import TutorSession from '@/pages/TutorSession'
import Quiz from '@/pages/Quiz'
import Notebook from '@/pages/Notebook'
import Growth from '@/pages/Growth'
import Opportunities from '@/pages/Opportunities'
import PrepareMe from '@/pages/PrepareMe'
import Wellbeing from '@/pages/Wellbeing'
import Reset from '@/pages/Reset'
import InnerGrowth from '@/pages/InnerGrowth'
import Settings from '@/pages/Settings'
import NotFound from '@/pages/NotFound'

class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-dvh flex-col items-center justify-center bg-paper px-6 text-center">
          <h1 className="font-display text-[22px] font-semibold text-ink">
            Something interrupted this request.
          </h1>
          <p className="mt-1.5 text-[14px] text-ink-soft">
            Nothing is lost — your progress is saved.
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false })
              window.location.href = '/'
            }}
            className="mt-6 h-11 rounded-xl bg-indigo px-5 text-[14.5px] font-semibold text-white transition-colors hover:bg-indigo-deep"
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

/** Sends signed-out visitors to the landing page, preserving where they were headed. */
function RequireAuth() {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'loading') {
    return (
      <div className="flex min-h-dvh flex-col items-center justify-center gap-3 bg-paper">
        <span className="gentle-float">
          <Logo size={40} />
        </span>
        <span className="text-[13px] font-medium text-ink-faint">Opening your learning space…</span>
      </div>
    )
  }
  if (status === 'guest') {
    return <Navigate to="/welcome" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

export default function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <BrowserRouter>
        <ErrorBoundary>
          <ScrollToTop />
          <Routes>
            <Route path="/welcome" element={<Landing />} />
            <Route path="/auth" element={<Auth />} />
            <Route element={<RequireAuth />}>
              <Route path="/reset" element={<Reset />} />
              <Route element={<AppShell />}>
                <Route path="/" element={<Home />} />
                <Route path="/roadmaps" element={<Roadmaps />} />
                <Route path="/roadmaps/:id" element={<RoadmapDetail />} />
                <Route path="/tutor" element={<TutorHub />} />
                <Route path="/tutor/:topicId" element={<TutorSession />} />
                <Route path="/quiz" element={<Quiz />} />
                <Route path="/quiz/:topicId" element={<Quiz />} />
                <Route path="/notebook" element={<Notebook />} />
                <Route path="/growth" element={<Growth />} />
                <Route path="/opportunities" element={<Opportunities />} />
                <Route path="/opportunities/:id/prepare" element={<PrepareMe />} />
                <Route path="/wellbeing" element={<Wellbeing />} />
                <Route path="/inner-growth" element={<InnerGrowth />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Route>
          </Routes>
          </ErrorBoundary>
        </BrowserRouter>
      </AppProvider>
    </AuthProvider>
  )
}
