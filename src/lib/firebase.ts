import { initializeApp, type FirebaseApp } from 'firebase/app'
import { getAuth, type Auth } from 'firebase/auth'

/**
 * Config comes from .env (VITE_FIREBASE_*) so keys stay out of the repo.
 * Without it the app still runs — auth falls back to local demo mode.
 */
const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string | undefined,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string | undefined,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string | undefined,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET as string | undefined,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string | undefined,
  appId: import.meta.env.VITE_FIREBASE_APP_ID as string | undefined,
}

export const firebaseEnabled = Boolean(config.apiKey && config.authDomain && config.projectId)

let app: FirebaseApp | null = null
let authInstance: Auth | null = null

if (firebaseEnabled) {
  try {
    app = initializeApp(config as Required<typeof config>)
    authInstance = getAuth(app)
  } catch {
    app = null
    authInstance = null
  }
}

export const auth = authInstance

/** Turns Firebase error codes into calm, human sentences. */
export function friendlyAuthError(code: string): string {
  switch (code) {
    case 'auth/invalid-email':
      return 'That email doesn’t look quite right.'
    case 'auth/missing-password':
    case 'auth/weak-password':
      return 'Passwords need at least 6 characters.'
    case 'auth/email-already-in-use':
      return 'That email already has an account — try signing in instead.'
    case 'auth/invalid-credential':
    case 'auth/wrong-password':
    case 'auth/user-not-found':
      return 'Those details didn’t match. Want to try again?'
    case 'auth/too-many-requests':
      return 'Too many attempts just now. Take a breath and retry in a moment.'
    case 'auth/popup-closed-by-user':
    case 'auth/cancelled-popup-request':
      return 'Sign-in window closed — no harm done.'
    case 'auth/popup-blocked':
      return 'Your browser blocked the sign-in window. Allow popups and try again.'
    case 'auth/network-request-failed':
      return 'The network dropped out. Check your connection and try again.'
    case 'auth/operation-not-allowed':
      return 'This sign-in method isn’t enabled for the project yet.'
    case 'auth/unauthorized-domain':
      return 'This domain isn’t authorized in Firebase yet.'
    default:
      return 'Something interrupted that request. Please try again.'
  }
}
