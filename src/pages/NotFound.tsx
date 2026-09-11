import { Link } from 'react-router-dom'
import { Compass } from 'lucide-react'
import { Page } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'

export default function NotFound() {
  return (
    <Page>
      <div className="flex min-h-[55vh] flex-col items-center justify-center text-center">
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-soft text-indigo-ink">
          <Compass size={24} />
        </span>
        <h1 className="mt-4 font-display text-[24px] font-semibold">
          This page wandered off the roadmap.
        </h1>
        <p className="mt-1.5 text-[14px] text-ink-soft">
          No harm done — let’s get you back to your learning.
        </p>
        <Link to="/" className="mt-6">
          <Button>Take me home</Button>
        </Link>
      </div>
    </Page>
  )
}
