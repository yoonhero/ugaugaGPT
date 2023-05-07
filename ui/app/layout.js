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
    description: "고대인이랑 대화를?? 우가가우가",
};

export default function RootLayout({ children }) {
    return (
        <html lang="ko">
            <body className={notoSansKr.className}>{children}</body>

            <Script
                strategy="afterInteractive"
                type="text/javascript"
                src="//wcs.naver.net/wcslog.js"
                id="naver"
            />
            <Script
                strategy="afterInterative"
                id="naver"
                dangerouslySetInnerHTML={{
                    __html: `
                            
                            if(!wcs_add) var wcs_add = {};
                            wcs_add["wa"] = "1b075fcf999f240";
                            if(window.wcs) {
                            wcs_do();
                            }`,
                }}
            />
        </html>
    );
}
