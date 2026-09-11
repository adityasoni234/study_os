import {
  Brain,
  Code2,
  Layers,
  MessageCircle,
  Rocket,
  Sparkles,
  type LucideIcon,
} from 'lucide-react'

const iconMap: Record<string, LucideIcon> = {
  brain: Brain,
  rocket: Rocket,
  code: Code2,
  chat: MessageCircle,
  layers: Layers,
  sparkles: Sparkles,
}

export function RoadmapIcon({ name, size = 18 }: { name: string; size?: number }) {
  const Icon = iconMap[name] ?? Sparkles
  return <Icon size={size} />
}

export function Logo({ size = 30 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden>
      <defs>
        <linearGradient id="logo-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#5B56D6" />
          <stop offset="1" stopColor="#7C5CF0" />
        </linearGradient>
      </defs>
      <rect x="4" y="4" width="56" height="56" rx="15" fill="url(#logo-g)" />
      <path
        d="M32 13 L36.4 27.6 L51 32 L36.4 36.4 L32 51 L27.6 36.4 L13 32 L27.6 27.6 Z"
        fill="#FFFFFF"
      />
      <circle cx="45.5" cy="18.5" r="3" fill="#FFFFFF" opacity="0.85" />
    </svg>
  )
}
