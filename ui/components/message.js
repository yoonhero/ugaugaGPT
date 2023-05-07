import { useEffect, useState } from "react";
import Image from "next/image";

const MessageBox = ({ mode, message, gif }) => {
    const [payload, setPayload] = useState("");

    useEffect(() => {
        // console.log(message);/
        if (message == undefined) return;

        if (mode == "user") {
            setPayload(message);
            return;
        }

        setPayload(message[0]);
    }, [message]);

    useEffect(() => {
        const timeout = setTimeout(() => {
            setPayload(message.slice(0, payload.length + 1));
        }, 200);

        return () => clearTimeout(timeout);
    }, [payload]);

    return (
        <div
            className={`flex flex-row bg-[${
                mode == "user" ? "#CB997E" : "#B7B7A4"
            }] w-full px-[4rem] md:px-[10rem] py-[1.24rem] min-h-[104px] border-b-2 border-[#DDBEA9]`}>
            <div className="mr-[2rem]">
                <Image
                    src={mode == "computer" ? "/uga.png" : "/user.png"}
                    width={60}
                    height={60}
                />
            </div>
            <div className="box-border  flex flex-col">
                {gif && <Image src={gif} width={100} height={100} />}

                <span
                    className={`text-md text-gray-800 ${
                        mode == "computer" &&
                        message != payload &&
                        "blinking-cursor"
                    }`}>
                    {payload}
                </span>
            </div>
        </div>
    );
};

export { MessageBox };
