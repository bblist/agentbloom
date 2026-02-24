"use client";

import Link from "next/link";
import { useState, useRef, useEffect } from "react";

interface Message {
    role: "bot" | "user";
    text: string;
    options?: string[];
}

const INITIAL_MESSAGES: Message[] = [
    { role: "bot", text: "👋 Hi! Welcome to Bright Smile Dental Studio. I'm your AI receptionist. How can I help you today?", options: ["Book an appointment", "What services do you offer?", "Hours & location", "Insurance questions", "I have a dental emergency"] },
];

const CONVERSATION_FLOWS: Record<string, Message[]> = {
    "Book an appointment": [
        { role: "user", text: "Book an appointment" },
        { role: "bot", text: "I'd love to help you book an appointment! Are you a new or existing patient?", options: ["New patient", "Existing patient"] },
    ],
    "New patient": [
        { role: "user", text: "New patient" },
        { role: "bot", text: "Welcome! 🎉 Great news — we have a new patient special: Exam, X-Rays & Cleaning for just $99 (a $350 value).\n\nWhat type of appointment are you looking for?", options: ["General checkup & cleaning", "Cosmetic consultation", "Invisalign consultation", "Dental emergency"] },
    ],
    "Existing patient": [
        { role: "user", text: "Existing patient" },
        { role: "bot", text: "Welcome back! What type of appointment do you need?", options: ["Routine cleaning", "Follow-up visit", "New concern", "Cosmetic consultation"] },
    ],
    "General checkup & cleaning": [
        { role: "user", text: "General checkup & cleaning" },
        { role: "bot", text: "Here are our next available slots for a general checkup:\n\n🗓️ **Tomorrow (Tue)** — 10:00 AM, 2:30 PM\n🗓️ **Wednesday** — 9:00 AM, 11:30 AM, 3:00 PM\n🗓️ **Thursday** — 10:00 AM, 1:00 PM\n🗓️ **Friday** — 9:00 AM, 4:00 PM\n\nWhich time works best for you?", options: ["Tomorrow at 10:00 AM", "Wednesday at 9:00 AM", "Show me next week"] },
    ],
    "Routine cleaning": [
        { role: "user", text: "Routine cleaning" },
        { role: "bot", text: "Here are our next available cleaning slots:\n\n🗓️ **Tomorrow (Tue)** — 10:00 AM, 2:30 PM\n🗓️ **Wednesday** — 9:00 AM, 11:30 AM, 3:00 PM\n🗓️ **Thursday** — 10:00 AM, 1:00 PM\n\nWhich time works best?", options: ["Tomorrow at 10:00 AM", "Wednesday at 9:00 AM", "Show me next week"] },
    ],
    "Tomorrow at 10:00 AM": [
        { role: "user", text: "Tomorrow at 10:00 AM" },
        { role: "bot", text: "Excellent choice! I'll book you for **Tuesday at 10:00 AM** with Dr. Sarah Chen.\n\nTo confirm your appointment, I just need a few details:\n\n📝 Could you share your full name?", options: [] },
    ],
    "Wednesday at 9:00 AM": [
        { role: "user", text: "Wednesday at 9:00 AM" },
        { role: "bot", text: "I'll book you for **Wednesday at 9:00 AM** with Dr. Sarah Chen.\n\nTo confirm your appointment, I just need a few details:\n\n📝 Could you share your full name?", options: [] },
    ],
    "Show me next week": [
        { role: "user", text: "Show me next week" },
        { role: "bot", text: "Here are next week's available slots:\n\n🗓️ **Monday** — 9:00 AM, 11:00 AM, 2:00 PM\n🗓️ **Tuesday** — 10:00 AM, 3:30 PM\n🗓️ **Wednesday** — 9:00 AM, 1:00 PM, 4:00 PM\n🗓️ **Thursday** — 11:00 AM, 2:00 PM\n🗓️ **Friday** — 9:00 AM, 10:30 AM\n\nWhich works for you?", options: ["Monday at 9:00 AM", "Tuesday at 10:00 AM", "Friday at 9:00 AM"] },
    ],
    "Monday at 9:00 AM": [
        { role: "user", text: "Monday at 9:00 AM" },
        { role: "bot", text: "I'll book you for **Monday at 9:00 AM** with Dr. Sarah Chen.\n\nTo confirm, could you share your full name?", options: [] },
    ],
    "Tuesday at 10:00 AM": [
        { role: "user", text: "Tuesday at 10:00 AM" },
        { role: "bot", text: "I'll get you booked for **Tuesday at 10:00 AM** with Dr. Sarah Chen.\n\nCould you share your full name to confirm?", options: [] },
    ],
    "Friday at 9:00 AM": [
        { role: "user", text: "Friday at 9:00 AM" },
        { role: "bot", text: "I'll book **Friday at 9:00 AM** with Dr. Sarah Chen for you.\n\nCould you share your full name?", options: [] },
    ],
    "Cosmetic consultation": [
        { role: "user", text: "Cosmetic consultation" },
        { role: "bot", text: "A cosmetic consultation is a great first step! Dr. Chen will do a full assessment, take photos, and discuss your options — whitening, veneers, bonding, or a full smile makeover.\n\n🕐 Consultations are 30 minutes. Here are the next available:\n\n🗓️ **Thursday** — 11:00 AM, 3:00 PM\n🗓️ **Friday** — 2:00 PM\n🗓️ **Next Monday** — 10:00 AM\n\nWhich works for you?", options: ["Thursday at 11:00 AM", "Friday at 2:00 PM", "Next Monday at 10:00 AM"] },
    ],
    "Invisalign consultation": [
        { role: "user", text: "Invisalign consultation" },
        { role: "bot", text: "Invisalign consultations are with Dr. James Park, our Diamond Invisalign Provider (1,500+ cases completed!).\n\nThe consultation includes a 3D iTero scan, treatment timeline estimate, and cost breakdown.\n\n🗓️ **Wednesday** — 10:00 AM, 2:00 PM\n🗓️ **Friday** — 11:00 AM\n\nWhich time works?", options: ["Wednesday at 10:00 AM", "Friday at 11:00 AM"] },
    ],
    "What services do you offer?": [
        { role: "user", text: "What services do you offer?" },
        { role: "bot", text: "We offer a full range of dental services:\n\n🦷 **General Dentistry** — Exams, cleanings, fillings, crowns\n✨ **Cosmetic Dentistry** — Whitening, veneers, bonding, smile makeovers\n📐 **Orthodontics** — Invisalign clear aligners, traditional braces\n🔩 **Dental Implants** — Permanent tooth replacement\n👶 **Pediatric Dentistry** — Gentle care for kids\n🚨 **Emergency Care** — Same-day appointments\n\nWould you like to learn more about any of these, or book an appointment?", options: ["Book an appointment", "Tell me about Invisalign", "How much does whitening cost?", "Back to main menu"] },
    ],
    "Tell me about Invisalign": [
        { role: "user", text: "Tell me about Invisalign" },
        { role: "bot", text: "Invisalign uses custom-made clear aligners to straighten your teeth — no metal brackets or wires!\n\n✅ Virtually invisible\n✅ Removable (eat whatever you want)\n✅ Comfortable — no wire adjustments\n✅ Average treatment: 6-18 months\n✅ 3D progress tracking\n\nDr. Park is a Diamond Invisalign Provider with 1,500+ cases. He'll create a digital treatment plan so you can preview your results before starting.\n\n💰 Pricing starts at $3,500. We offer 0% interest payment plans and accept most dental insurance.\n\nWant to book a free Invisalign consultation?", options: ["Yes, book a consultation", "How does pricing work?", "Back to main menu"] },
    ],
    "How much does whitening cost?": [
        { role: "user", text: "How much does whitening cost?" },
        { role: "bot", text: "We offer two whitening options:\n\n🏥 **In-Office Whitening** — $450\nOne 60-minute session. Up to 8 shades whiter. Immediate, dramatic results.\n\n🏠 **Take-Home Kit** — $250\nCustom-fitted trays + professional-grade gel. Use 30 min/day for 2 weeks.\n\n💡 **Combo Deal** — $599\nGet both! In-office session + take-home kit for maintenance.\n\nWould you like to book a whitening appointment?", options: ["Book in-office whitening", "Book an appointment", "Back to main menu"] },
    ],
    "Hours & location": [
        { role: "user", text: "Hours & location" },
        { role: "bot", text: "📍 **Bright Smile Dental Studio**\n456 Oak Avenue, Suite 200\nAnytown, USA 12345\n\n🕐 **Hours:**\nMon-Fri: 8:00 AM – 6:00 PM\nSaturday: 9:00 AM – 3:00 PM\nSunday: Closed\n\n🅿️ Free parking available in our building garage.\n🚇 We're 2 blocks from the Oak Street Metro station.\n\n📞 Phone: (555) 234-5678\n✉️ Email: hello@brightsmiledentalstudio.com\n\nCan I help with anything else?", options: ["Book an appointment", "Insurance questions", "Back to main menu"] },
    ],
    "Insurance questions": [
        { role: "user", text: "Insurance questions" },
        { role: "bot", text: "We accept most major dental insurance plans, including:\n\n✅ Delta Dental\n✅ Cigna\n✅ Aetna\n✅ MetLife\n✅ Guardian\n✅ United Healthcare\n✅ BlueCross BlueShield\n✅ Humana\n\nWe'll verify your benefits before your visit and maximise your coverage.\n\n**No insurance?** We offer:\n💳 0% interest payment plans (CareCredit)\n🏷️ In-house membership: $29/month (2 cleanings, exams, X-rays + 20% off all treatments)\n\nWant to verify your specific plan, or book an appointment?", options: ["Book an appointment", "Tell me about the membership plan", "Back to main menu"] },
    ],
    "Tell me about the membership plan": [
        { role: "user", text: "Tell me about the membership plan" },
        { role: "bot", text: "Our **Bright Smile Membership** is perfect for patients without insurance:\n\n💰 **$29/month** or **$299/year** (save $49)\n\n**Included:**\n✅ 2 professional cleanings per year\n✅ 2 comprehensive exams\n✅ Full digital X-rays\n✅ 1 emergency exam per year\n\n**Plus 20% off:**\n• Fillings, crowns, root canals\n• Cosmetic procedures\n• Invisalign treatment\n• Dental implants\n\nNo waiting periods, no deductibles, no maximums.\n\nWant to sign up or book an appointment?", options: ["Book an appointment", "Back to main menu"] },
    ],
    "I have a dental emergency": [
        { role: "user", text: "I have a dental emergency" },
        { role: "bot", text: "I'm sorry you're in pain! Let me help right away. 🚨\n\nCan you describe what's happening?", options: ["Severe toothache", "Broken or chipped tooth", "Knocked-out tooth", "Lost filling or crown", "Swelling or abscess"] },
    ],
    "Severe toothache": [
        { role: "user", text: "Severe toothache" },
        { role: "bot", text: "I understand — toothaches can be incredibly painful. Here's what to do right now:\n\n🧊 Apply a cold compress to the outside of your cheek\n💊 Take over-the-counter ibuprofen (Advil) for pain and inflammation\n🚫 Avoid very hot or cold foods/drinks\n\n**We have same-day emergency slots available:**\n\n🗓️ **Today** — 3:30 PM, 5:00 PM\n🗓️ **Tomorrow** — 8:00 AM (first thing)\n\nWould you like me to book you in?", options: ["Today at 3:30 PM", "Tomorrow at 8:00 AM", "Call the office directly"] },
    ],
    "Broken or chipped tooth": [
        { role: "user", text: "Broken or chipped tooth" },
        { role: "bot", text: "Don't worry — we can usually fix this! Here's immediate advice:\n\n💧 Rinse your mouth with warm water\n🧊 Use a cold compress for any swelling\n🩹 If there's a sharp edge, cover it with sugar-free gum or dental wax\n📦 Save any broken pieces if possible\n\n**Emergency appointments available:**\n\n🗓️ **Today** — 3:30 PM, 5:00 PM\n🗓️ **Tomorrow** — 8:00 AM\n\nShall I book you in?", options: ["Today at 3:30 PM", "Tomorrow at 8:00 AM", "Call the office directly"] },
    ],
    "Today at 3:30 PM": [
        { role: "user", text: "Today at 3:30 PM" },
        { role: "bot", text: "I'll get you booked for **today at 3:30 PM** as an emergency appointment with Dr. Chen.\n\n📝 Could you share your full name so I can confirm?", options: [] },
    ],
    "Tomorrow at 8:00 AM": [
        { role: "user", text: "Tomorrow at 8:00 AM" },
        { role: "bot", text: "Booked! **Tomorrow at 8:00 AM** emergency appointment with Dr. Chen.\n\n📝 What's your full name?", options: [] },
    ],
    "Call the office directly": [
        { role: "user", text: "Call the office directly" },
        { role: "bot", text: "Of course! You can reach us at:\n\n📞 **(555) 234-5678**\n\nFor after-hours emergencies, our on-call line is:\n📞 **(555) 234-9999**\n\nIs there anything else I can help with?", options: ["Back to main menu"] },
    ],
    "Back to main menu": [
        { role: "user", text: "Back to main menu" },
        { role: "bot", text: "No problem! How can I help you?", options: ["Book an appointment", "What services do you offer?", "Hours & location", "Insurance questions", "I have a dental emergency"] },
    ],
};

export default function ReceptionistDemo() {
    const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
    const [currentOptions, setCurrentOptions] = useState<string[]>(INITIAL_MESSAGES[0].options || []);
    const [typing, setTyping] = useState(false);
    const [userInput, setUserInput] = useState("");
    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, typing]);

    const handleOption = (option: string) => {
        const flow = CONVERSATION_FLOWS[option];
        if (!flow) return;

        // Add user message immediately
        const userMsg = flow.find((m) => m.role === "user");
        if (userMsg) {
            setMessages((prev) => [...prev, userMsg]);
        }
        setCurrentOptions([]);
        setTyping(true);

        // Simulate typing delay
        setTimeout(() => {
            const botMsg = flow.find((m) => m.role === "bot");
            if (botMsg) {
                setMessages((prev) => [...prev, botMsg]);
                setCurrentOptions(botMsg.options || []);
            }
            setTyping(false);
        }, 800 + Math.random() * 600);
    };

    const handleFreeText = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userInput.trim()) return;

        const text = userInput.trim();
        setUserInput("");
        setMessages((prev) => [...prev, { role: "user", text }]);
        setCurrentOptions([]);
        setTyping(true);

        setTimeout(() => {
            setMessages((prev) => [
                ...prev,
                {
                    role: "bot",
                    text: `Thank you! I've noted "${text}". In a live AgentBloom receptionist, I'd process this with AI to understand your request and respond intelligently.\n\nFor this demo, you can continue using the quick-reply buttons below to explore the full conversation flow.`,
                    options: ["Book an appointment", "What services do you offer?", "Hours & location", "Insurance questions", "I have a dental emergency"],
                },
            ]);
            setCurrentOptions(["Book an appointment", "What services do you offer?", "Hours & location", "Insurance questions", "I have a dental emergency"]);
            setTyping(false);
        }, 1000);
    };

    const resetChat = () => {
        setMessages(INITIAL_MESSAGES);
        setCurrentOptions(INITIAL_MESSAGES[0].options || []);
        setTyping(false);
        setUserInput("");
    };

    const formatText = (text: string) => {
        return text.split("\n").map((line, i) => {
            // Bold
            const boldFormatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            return <p key={i} className={i > 0 ? "mt-1" : ""} dangerouslySetInnerHTML={{ __html: boldFormatted }} />;
        });
    };

    return (
        <main className="min-h-screen bg-gray-50 dark:bg-gray-950">
            {/* Banner */}
            <div className="bg-blue-600 text-white text-center py-2 text-sm font-medium">
                <Link href="/" className="hover:underline">← This is an AgentBloom AI Receptionist demo — Create your own for free</Link>
            </div>

            {/* Header */}
            <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
                <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-teal-500 flex items-center justify-center text-white font-bold text-sm">BS</div>
                        <div>
                            <h1 className="font-semibold text-lg leading-tight">Bright Smile Dental</h1>
                            <p className="text-xs text-green-500 flex items-center gap-1"><span className="w-1.5 h-1.5 bg-green-500 rounded-full inline-block" /> AI Receptionist Online</p>
                        </div>
                    </div>
                    <button onClick={resetChat} className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">Reset Chat</button>
                </div>
            </div>

            {/* Chat */}
            <div className="max-w-3xl mx-auto px-4 py-6">
                {/* Info banner */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mb-6 text-sm text-blue-700 dark:text-blue-300">
                    <strong>Interactive Demo:</strong> This is a simulated AI receptionist for a dental practice. Click the quick-reply buttons to explore different conversation flows — booking, services, insurance, emergencies, and more. In production, it handles any free-text input with full AI understanding.
                </div>

                <div className="space-y-4">
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === "user" ? "bg-blue-600 text-white rounded-br-md" : "bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-bl-md"}`}>
                                <div className="text-sm leading-relaxed">{formatText(msg.text)}</div>
                            </div>
                        </div>
                    ))}

                    {/* Typing indicator */}
                    {typing && (
                        <div className="flex justify-start">
                            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl rounded-bl-md px-4 py-3">
                                <div className="flex gap-1">
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={chatEndRef} />
                </div>

                {/* Quick reply options */}
                {currentOptions.length > 0 && !typing && (
                    <div className="mt-4 flex flex-wrap gap-2">
                        {currentOptions.map((opt) => (
                            <button key={opt} onClick={() => handleOption(opt)} className="px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-full text-sm font-medium hover:bg-blue-50 hover:border-blue-300 dark:hover:bg-blue-900/20 dark:hover:border-blue-700 transition-all cursor-pointer">
                                {opt}
                            </button>
                        ))}
                    </div>
                )}

                {/* Free text input */}
                <form onSubmit={handleFreeText} className="mt-6 flex gap-2">
                    <input
                        type="text"
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button type="submit" className="px-5 py-3 bg-blue-600 text-white rounded-xl font-semibold text-sm hover:bg-blue-700 transition-colors">Send</button>
                </form>
            </div>

            {/* Feature callout */}
            <div className="max-w-3xl mx-auto px-4 pb-12">
                <div className="bg-gradient-to-br from-slate-900 to-blue-950 rounded-2xl p-8 text-white mt-8">
                    <h2 className="text-2xl font-bold mb-4">What AgentBloom AI Receptionist Can Do</h2>
                    <div className="grid sm:grid-cols-2 gap-4 text-sm">
                        {[
                            { title: "24/7 Availability", desc: "Never miss a patient inquiry — your AI receptionist works around the clock, even holidays." },
                            { title: "Smart Booking", desc: "Integrates with your calendar to show real availability and book appointments automatically." },
                            { title: "Insurance Verification", desc: "Answers insurance questions and helps patients understand their coverage." },
                            { title: "Emergency Triage", desc: "Provides immediate guidance for dental emergencies and prioritises urgent cases." },
                            { title: "Multi-Language Support", desc: "Communicates in 50+ languages to serve diverse patient populations." },
                            { title: "Seamless Handoff", desc: "Transfers complex cases to your human staff with full conversation context." },
                        ].map((f) => (
                            <div key={f.title} className="bg-white/5 rounded-xl p-4">
                                <h3 className="font-semibold mb-1">{f.title}</h3>
                                <p className="text-gray-300 text-xs leading-relaxed">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                    <div className="mt-6 text-center">
                        <Link href="/" className="inline-block px-7 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors">Get Your AI Receptionist — Free</Link>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="py-8 bg-gray-900 text-gray-400 text-center text-sm">
                <p>AI Receptionist Demo · Powered by <Link href="/" className="text-blue-400 hover:underline">AgentBloom</Link></p>
            </footer>
        </main>
    );
}
