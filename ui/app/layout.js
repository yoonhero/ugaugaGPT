import './globals.css'
import { Noto_Sans_KR  } from 'next/font/google'

const notoSansKr = Noto_Sans_KR({
  subsets: ["latin"],
  weight: ["100", "400", "700", "900"]
})

export const metadata = {
  title: '우가우가GPT',
  description: '고대인이랑 대화를?? 우가가우가',
}

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body className={notoSansKr.className}>{children}</body>
    </html>
  )
}
