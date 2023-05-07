"use client";
import { MessageBox } from "@/components/message";
import Image from "next/image";
import { set, useForm } from "react-hook-form";
import ScrollToBottom, { useScrollToBottom } from "react-scroll-to-bottom";
import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import Head from "next/head";
import Script from "next/script";

export default function Home() {
    const [chats, setChat] = useState([]);
    const chatContainerRef = useRef(null);
    // const scrollToBottom = useScrollToBottom();

    const {
        register,
        handleSubmit,
        watch,
        setValue,
        formState: { errors },
    } = useForm();
    const onSubmit = (data) => {
        const command = data.command;
        setValue("command", "");

        const chat = {
            mode: "user",
            message: command,
        };
        setChat([...chats, chat]);
    };

    const enterSubmit = (e) => {
        if (e.key === "Enter" && e.shiftKey == false) {
            const data = { command: e.target.value };
            return handleSubmit(onSubmit(data));
        }
    };

    const Api = async (message) => {
        // try {
        //     const res = await fetch(
        //         "/api?prompt=" + encodeURIComponent(message)
        //     );
        //     if (res.status !== 200) {
        //         console.error("Error Generating text with Ai");
        //     } else {
        //         const jsoned = await res.json();
        //         console.log(jsoned);
        //     }
        // } catch (error) {
        //     console.log(error);
        // }

        const chat = {
            mode: "computer",
            gif: "/start.gif",
            message: "우가우가우가ㅣ우가",
        };

        setChat([...chats, chat]);
    };
    const scrollToBottom = () => {
        chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
    };

    useEffect(() => {
        if (chats.length == 0) return;
        if (chats[chats.length - 1].mode == "user") {
            Api(chats[chats.length - 1].message);

            scrollToBottom();
        }
    }, [chats]);

    return (
        <>
            <Script
                strategy="afterInteractive"
                type="text/javascript"
                src="//wcs.naver.net/wcslog.js"
                id="naver"
            />
            <Script strategy="afterInterative" id="naver-analystic">
                {`
                            
                            if(!wcs_add) var wcs_add = {};
                            wcs_add["wa"] = "1b075fcf999f240";
                            if(window.wcs) {
                            wcs_do();
                            }`}
            </Script>
            <main className="flex flex-row h-screen w-screen">
                {/* Chat Archive */}
                {/* <div className='flex'>
          <div className='hidden md:block md:min-w-[240px] flex-col bg-[#B7B7A4] p-2'>

            <button className='p-3 border border-1 border-gray-300 w-full rounded-md'>
              <div className="text-md text-white">새로운 대화</div>
            </button>

            <div className="h-5"></div>

            <div className="flex flex-col w-full  flex-start">
              <div className="w-full flex justify-around">
                <div className="text-md text-white">New Chat</div>
              </div>
            </div>
          </div>
      </div> */}

                {/* Main Chat Space */}
                <div className="relative overflow-hidden h-full flex flex-col w-full  bg-[#DDBEA9]">
                    <div
                        className={`${
                            chats.length != 0 && "hidden"
                        }  flex-1 flex flex-col items-center text-center flex-col w-full justify-center items-center `}>
                        <div className="text-3xl text-[#6B705C] font-extrabold">
                            UgaugaGPT
                        </div>
                        <div className="flex items-center mx-20 my-10">
                            <Image
                                src={"/start.gif"}
                                width={200}
                                height={200}
                            />
                        </div>

                        <div className="max-w-[340px] py-1 px-5 rounded-md">
                            <span className="font-bold text-gray-800">
                                가가우우우가우가우가우우가우우우
                                가우가가우우우가우가우가우가우가
                                가가우가우가우가우가우가가우우우
                                가가우우우우우가우우가가가우우우
                                가가우우우가가우가우우가우가우우 가우우우우우
                            </span>
                        </div>
                        <div className="mt-2 flex flex-row gap-2 animate-bounce text-gray-600 text-sm">
                            Copyright 2023 ©{" "}
                            <Link href="https://github.com/yoonhero">
                                <p className="cursor-pointer font-bold text-md text-gray-800">
                                    Yoonhero
                                </p>
                            </Link>
                        </div>
                    </div>

                    <div
                        className={`${
                            chats.length == 0 && "hidden"
                        } overflow-hidden w-full flex-1 `}>
                        <div
                            ref={chatContainerRef}
                            className="overflow-y-scroll h-full flex flex-col items-center ">
                            <div className="w-full">
                                {chats.map((chat, i) => {
                                    return (
                                        <MessageBox
                                            key={i}
                                            mode={chat.mode}
                                            message={chat.message}
                                            gif={
                                                chat.mode == "computer" &&
                                                chat.gif
                                            }
                                        />
                                    );
                                })}
                                <div className="h-[100px]"></div>
                            </div>
                        </div>
                    </div>
                    <div className="fixed box-content w-full bottom-0 flex justify-center items-center flex-col ">
                        <form
                            onSubmit={handleSubmit(onSubmit)}
                            className="w-full pt-[1.5rem] max-w-[48rem] flex flex-col justify-center align-center items-center">
                            <div className="shadow-xl relative pl-[1rem] py-[0.75rem] rounded-md w-[90%] md:w-full relative bg-[#FFE8D6]">
                                <textarea
                                    onKeyPress={enterSubmit}
                                    {...register("command", { required: true })}
                                    className="resize-none max-h-[24px] border-box border-none outline-none w-full bg-transparent text-gray-600 leading-[1.5rem] align-middle overflow-hidden"
                                />

                                <button className="absolute right-0 bottom-1">
                                    <Image
                                        src="/send.png"
                                        width={40}
                                        height={40}
                                    />
                                </button>
                            </div>
                            {errors.command && (
                                <span className="pl-2 text-sm text-green-900 font-bold">
                                    우가우!가! 입력해주세요.
                                </span>
                            )}
                        </form>

                        <div className="pt-[6px] pb-[12px]">
                            <span className="text-sm text-[#6B705C]">
                                이것은 패러디 웹사이트이며 OpenAI와 관련이
                                없습니다.
                            </span>
                        </div>
                    </div>
                </div>
            </main>
        </>
    );
}
