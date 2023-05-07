import Script from "next/script";
import "./globals.css";
import { Noto_Sans_KR } from "next/font/google";
import Head from "next/head";

const notoSansKr = Noto_Sans_KR({
    subsets: ["latin"],
    weight: ["100", "400", "700", "900"],
});

export const metadata = {
    title: "우가우가GPT",
    description: "고대인이랑 대화를?? 우가가우가!!",
    verification: {
        google: "1KDe4Utph9TllN9u4Gzkgc3k_Xo7kWtruaYaqrIwsKM",
        other: {
            "naver-site-verification": [
                "526dea18e9d6a5d3d8b9c4988fcfa3567fdd64e3",
            ],
        },
    },
    twitter: {
        card: "summary_large_image",
        title: "우가우가GPT",
        description: "고대인이랑 대화를?? 우가가우가!!",
        creator: "@yoonhero",
        images: ["/icon.png"],
    },
    icons: {
        icon: "/icon.png",
        shortcut: "/icon.png",
        apple: "/icon.png",
        other: {
            rel: "apple-touch-icon-precomposed",
            url: "/icon.png",
        },
    },
};

export default function RootLayout({ children }) {
    return (
        <html lang="ko">
            <body className={notoSansKr.className}>{children}</body>
        </html>
    );
}
