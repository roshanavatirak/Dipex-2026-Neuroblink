// 'use client';

// import './globals.css'
// import type { Metadata } from 'next'
// import { Inter } from 'next/font/google'
// import { useEffect } from 'react'

// const inter = Inter({ subsets: ['latin'] })

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode
// }) {
//   useEffect(() => {
//     // Fix hydration issues by ensuring client-side rendering
//     document.documentElement.classList.add('dark')
//   }, [])

//   return (
//     <html lang="en" suppressHydrationWarning>
//       <body className={`${inter.className} bg-black text-white min-h-screen`} suppressHydrationWarning>
//         <div className="relative min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
//           {/* Animated background grid */}
//           <div className="absolute inset-0 bg-cyber-grid bg-cyber-grid opacity-20"></div>
          
//           {/* Floating orbs */}
//           <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
//           <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
//           <div className="absolute top-3/4 left-1/3 w-48 h-48 bg-cyan-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }}></div>
          
//           {/* Main content */}
//           <div className="relative z-10">
//             {children}
//           </div>
//         </div>
//       </body>
//     </html>
//   )
// }
'use client';

import './globals.css'
import { Inter } from 'next/font/google'
  // ← won't work, use below

// ✅ Correct way in App Router:
import { usePathname } from 'next/navigation'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-black text-white min-h-screen`} suppressHydrationWarning>
        <LayoutWrapper>{children}</LayoutWrapper>
      </body>
    </html>
  )
}

function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const isLivePage = pathname === '/live'

  // Live page manages its own background — don't wrap it
  if (isLivePage) {
    return <>{children}</>
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      <div className="absolute inset-0 bg-cyber-grid bg-cyber-grid opacity-20" />
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      <div className="absolute top-3/4 left-1/3 w-48 h-48 bg-cyan-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }} />
      <div className="relative z-10">{children}</div>
    </div>
  )
}