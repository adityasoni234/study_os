import { NavLink, Outlet, useLocation, Link, matchPath } from 'react-router-dom'
import {
  BookOpen,
  Flame,
  Flower2,
  GraduationCap,
  HeartHandshake,
  Home,
  Map,
  Radar,
  Settings,
  Sprout,
} from 'lucide-react'
import { Logo } from '@/lib/icons'
import { cn, firstName, initials } from '@/lib/utils'
import { Toasts } from '@/components/ui/Toasts'
import { useApp } from '@/state/AppContext'

const primaryNav = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/roadmaps', label: 'Roadmaps', icon: Map },
  { to: '/tutor', label: '1:1 Tutor', icon: GraduationCap },
  { to: '/notebook', label: 'Notebook', icon: BookOpen },
  { to: '/growth', label: 'Growth', icon: Sprout },
]

const secondaryNav = [
  { to: '/opportunities', label: 'Opportunity Radar', icon: Radar },
  { to: '/wellbeing', label: 'Wellbeing', icon: HeartHandshake },
  { to: '/inner-growth', label: 'Inner Growth', icon: Flower2 },
]

function SideLink({
  to,
  label,
  icon: Icon,
}: {
  to: string
  label: string
  icon: React.ComponentType<{ size?: number | string; className?: string }>
}) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        cn(
          'group flex items-center gap-3 rounded-[10px] px-3 py-2 text-[13.5px] font-medium transition-all duration-150',
          isActive
            ? 'bg-indigo-soft text-indigo-ink'
            : 'text-ink-soft hover:bg-paper-deep hover:text-ink',
        )
      }
    >
      <Icon size={17} className="shrink-0" />
      {label}
    </NavLink>
  )
}

export function AppShell() {
  const location = useLocation()
  const { state } = useApp()
  const inTutorSession = matchPath('/tutor/:topicId', location.pathname) != null
  const hideMobileChrome = inTutorSession
  const name = state.auth.name

  return (
    <div className="min-h-dvh">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[240px] flex-col border-r bg-card/70 backdrop-blur lg:flex">
        <Link to="/" className="flex items-center gap-2.5 px-5 pt-6 pb-5">
          <Logo size={30} />
          <div>
            <div className="text-[16px] leading-tight font-bold tracking-tight">StudyOS</div>
            <div className="text-[10.5px] font-medium text-ink-faint">Learn · Grow · Belong</div>
          </div>
        </Link>

        <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3">
          {primaryNav.map((item) => (
            <SideLink key={item.to} {...item} />
          ))}
          <div className="mt-5 mb-1.5 px-3 text-[10.5px] font-semibold tracking-[0.1em] text-ink-faint uppercase">
            Explore
          </div>
          {secondaryNav.map((item) => (
            <SideLink key={item.to} {...item} />
          ))}
        </nav>

        <div className="border-t px-3 py-3">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-[10px] px-3 py-2 transition-colors',
                isActive ? 'bg-indigo-soft' : 'hover:bg-paper-deep',
              )
            }
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo to-violet text-[12.5px] font-bold text-white">
              {initials(name)}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-[13px] leading-tight font-semibold">
                {firstName(name)}
              </span>
              <span className="flex items-center gap-1 text-[11px] font-medium text-amber-ink">
                <Flame size={11} /> 12-day streak
              </span>
            </span>
            <Settings size={15} className="text-ink-faint" />
          </NavLink>
          <div className="mt-2 px-3 text-[10px] leading-snug text-ink-faint">
            Built for SDG 4 · Quality Education
          </div>
        </div>
      </aside>

      {/* Mobile top bar */}
      {!hideMobileChrome && (
        <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b bg-paper/85 px-4 backdrop-blur lg:hidden">
          <Link to="/" className="flex items-center gap-2">
            <Logo size={26} />
            <span className="text-[15px] font-bold tracking-tight">StudyOS</span>
          </Link>
          <Link
            to="/settings"
            aria-label="Profile & settings"
            className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo to-violet text-[12px] font-bold text-white"
          >
            {initials(name)}
          </Link>
        </header>
      )}

      {/* Main content */}
      <main
        className={cn(
          'lg:pl-[240px]',
          inTutorSession ? '' : 'pb-24 lg:pb-10',
        )}
      >
        <div key={location.pathname} className={inTutorSession ? '' : 'anim-in'}>
          <Outlet />
        </div>
      </main>

      {/* Mobile bottom nav */}
      {!hideMobileChrome && (
        <nav className="fixed inset-x-0 bottom-0 z-30 border-t bg-card/95 backdrop-blur lg:hidden">
          <div className="mx-auto flex h-16 max-w-md items-stretch justify-around px-2 pb-[env(safe-area-inset-bottom)]">
            {primaryNav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex flex-1 flex-col items-center justify-center gap-0.5 rounded-lg text-[10px] font-semibold transition-colors',
                    isActive ? 'text-indigo-ink' : 'text-ink-faint hover:text-ink-soft',
                  )
                }
              >
                <Icon size={19} />
                {label === '1:1 Tutor' ? 'Tutor' : label}
              </NavLink>
            ))}
          </div>
        </nav>
      )}

      <Toasts />
    </div>
  )
}
