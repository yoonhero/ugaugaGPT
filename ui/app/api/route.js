import openai from "@/utils/openai";
import { NextResponse } from "next/server";

export async function GET(req, { params }) {
    const prompt = decodeURIComponent(params.prompt);

    if (!prompt) {
        return NextResponse.status(404).json({ error: "Prompt Missing" });
    }

    const completion = await openai.createChatCompletion({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: "안녕?" }],
    });
    const responseText = completion.data.choices[0].message.content;
    const responseObject = JSON.parse(responseText);

    return NextResponse.json(responseObject);
}
