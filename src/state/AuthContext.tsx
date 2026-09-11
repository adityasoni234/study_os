import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInAnonymously,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut as fbSignOut,
  updateProfile,
  type User as FirebaseUser,
} from 'firebase/auth'
import { auth, firebaseEnabled, friendlyAuthError } from '@/lib/firebase'

export interface AuthUser {
  uid: string
  name: string
  email: string | null
  photoURL: string | null
  isDemo: boolean
}

type Status = 'loading' | 'authed' | 'guest'

interface AuthApi {
  user: AuthUser | null
  status: Status
  /** True when Firebase is configured; false means local demo-only mode. */
  live: boolean
  signUp: (name: string, email: string, password: string) => Promise<void>
  signIn: (email: string, password: string) => Promise<void>
  signInWithGoogle: () => Promise<void>
  continueAsDemo: () => Promise<void>
  signOut: () => Promise<void>
}

const Ctx = createContext<AuthApi | null>(null)

const DEMO_KEY = 'studyos-demo-user'

function toAuthUser(u: FirebaseUser): AuthUser {
  return {
    uid: u.uid,
    name: u.displayName || u.email?.split('@')[0]?.replace(/[._-]/g, ' ') || 'Learner',
    email: u.email,
    photoURL: u.photoURL,
    isDemo: u.isAnonymous,
  }
}

/** Thrown errors carry a human-readable message ready for the UI. */
function rethrowFriendly(e: unknown): never {
  const code = (e as { code?: string })?.code ?? ''
  throw new Error(friendlyAuthError(code))
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [status, setStatus] = useState<Status>(firebaseEnabled ? 'loading' : 'guest')

  // Local demo session (used when Firebase is unavailable or the learner picks demo mode).
  useEffect(() => {
    if (firebaseEnabled && auth) {
      return onAuthStateChanged(
        auth,
        (fbUser) => {
          if (fbUser) {
            setUser(toAuthUser(fbUser))
            setStatus('authed')
          } else {
            const demo = readDemo()
            setUser(demo)
            setStatus(demo ? 'authed' : 'guest')
          }
        },
        () => {
          const demo = readDemo()
          setUser(demo)
          setStatus(demo ? 'authed' : 'guest')
        },
      )
    }
    const demo = readDemo()
    setUser(demo)
    setStatus(demo ? 'authed' : 'guest')
  }, [])

  const api = useMemo<AuthApi>(() => {
    const localDemo = (name = 'Aditya') => {
      const demo: AuthUser = {
        uid: 'demo-user',
        name,
        email: null,
        photoURL: null,
        isDemo: true,
      }
      try {
        localStorage.setItem(DEMO_KEY, JSON.stringify(demo))
      } catch {
        /* private mode — session simply won't persist */
      }
      setUser(demo)
      setStatus('authed')
    }

    return {
      user,
      status,
      live: firebaseEnabled && auth != null,

      signUp: async (name, email, password) => {
        if (!auth) return localDemo(name)
        try {
          const cred = await createUserWithEmailAndPassword(auth, email, password)
          if (name.trim()) {
            await updateProfile(cred.user, { displayName: name.trim() })
            setUser({ ...toAuthUser(cred.user), name: name.trim() })
          }
        } catch (e) {
          rethrowFriendly(e)
        }
      },

      signIn: async (email, password) => {
        if (!auth) return localDemo(email.split('@')[0].replace(/[._-]/g, ' '))
        try {
          await signInWithEmailAndPassword(auth, email, password)
        } catch (e) {
          rethrowFriendly(e)
        }
      },

      signInWithGoogle: async () => {
        if (!auth) return localDemo()
        try {
          await signInWithPopup(auth, new GoogleAuthProvider())
        } catch (e) {
          rethrowFriendly(e)
        }
      },

      continueAsDemo: async () => {
        if (auth) {
          try {
            await signInAnonymously(auth)
            return
          } catch {
            /* anonymous auth may be disabled — fall through to local demo */
          }
        }
        localDemo()
      },

      signOut: async () => {
        try {
          localStorage.removeItem(DEMO_KEY)
        } catch {
          /* noop */
        }
        if (auth) {
          try {
            await fbSignOut(auth)
          } catch {
            /* still clear locally */
          }
        }
        setUser(null)
        setStatus('guest')
      },
    }
  }, [user, status])

  return <Ctx.Provider value={api}>{children}</Ctx.Provider>
}

function readDemo(): AuthUser | null {
  try {
    const raw = localStorage.getItem(DEMO_KEY)
    return raw ? (JSON.parse(raw) as AuthUser) : null
  } catch {
    return null
  }
}

export function useAuth(): AuthApi {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
