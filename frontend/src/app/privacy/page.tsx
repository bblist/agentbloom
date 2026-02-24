import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Privacy Policy — AgentBloom",
    description: "AgentBloom Privacy Policy",
};

export default function PrivacyPage() {
    return (
        <main className="min-h-screen bg-white dark:bg-gray-950">
            <div className="max-w-3xl mx-auto px-6 py-16">
                <Link href="/" className="text-blue-600 hover:underline text-sm mb-8 inline-block">
                    ← Back to AgentBloom
                </Link>
                <h1 className="text-4xl font-bold mb-2">Privacy Policy</h1>
                <p className="text-gray-500 mb-10">Last updated: February 24, 2026</p>

                <div className="prose dark:prose-invert max-w-none space-y-6">
                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">1. Introduction</h2>
                        <p>NobleBlocks LLC (&quot;we&quot;, &quot;us&quot;, &quot;our&quot;) operates AgentBloom. This Privacy Policy describes how we collect, use, and protect your personal information when you use our Service.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">2. Information We Collect</h2>
                        <h3 className="text-lg font-medium mt-4 mb-2">Information You Provide</h3>
                        <ul className="list-disc pl-6 space-y-1">
                            <li>Account information (name, email, password)</li>
                            <li>Organization details (business name, niche, description)</li>
                            <li>Content you create (websites, emails, courses, documents)</li>
                            <li>Contact lists and CRM data you upload</li>
                            <li>Payment information (processed by Stripe; we do not store card numbers)</li>
                            <li>Communications with our AI agent</li>
                        </ul>
                        <h3 className="text-lg font-medium mt-4 mb-2">Information Collected Automatically</h3>
                        <ul className="list-disc pl-6 space-y-1">
                            <li>Log data (IP address, browser type, pages visited)</li>
                            <li>Usage analytics (features used, time spent)</li>
                            <li>Device information (operating system, screen size)</li>
                            <li>Cookies and similar technologies</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">3. How We Use Your Information</h2>
                        <ul className="list-disc pl-6 space-y-1">
                            <li>Provide, maintain, and improve the Service</li>
                            <li>Process transactions and send related communications</li>
                            <li>Power AI features (content generation, receptionist, recommendations)</li>
                            <li>Send service notifications and updates</li>
                            <li>Detect and prevent fraud, abuse, and security issues</li>
                            <li>Comply with legal obligations</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">4. AI Data Processing</h2>
                        <p>When you use AI features, your prompts and content may be sent to third-party AI providers (OpenAI, Anthropic, Google) for processing. We do not use your data to train AI models. AI providers process data in accordance with their own data processing agreements.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">5. Data Sharing</h2>
                        <p>We do not sell your personal information. We may share data with:</p>
                        <ul className="list-disc pl-6 space-y-1">
                            <li><strong>Service providers</strong>: AWS (hosting, email), Stripe (payments), AI providers (content generation)</li>
                            <li><strong>Legal requirements</strong>: When required by law, subpoena, or legal process</li>
                            <li><strong>Business transfers</strong>: In connection with a merger, acquisition, or sale of assets</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">6. Data Storage & Security</h2>
                        <p>Data is stored on AWS infrastructure in the United States. We implement industry-standard security measures including encryption in transit (TLS 1.3) and at rest, access controls, and regular security assessments.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">7. Your Rights</h2>
                        <p>Depending on your jurisdiction, you may have the right to:</p>
                        <ul className="list-disc pl-6 space-y-1">
                            <li><strong>Access</strong>: Request a copy of your personal data</li>
                            <li><strong>Correction</strong>: Request correction of inaccurate data</li>
                            <li><strong>Deletion</strong>: Request deletion of your data (&quot;right to be forgotten&quot;)</li>
                            <li><strong>Export</strong>: Request your data in a portable format</li>
                            <li><strong>Objection</strong>: Object to certain processing of your data</li>
                            <li><strong>Restriction</strong>: Request restriction of processing</li>
                        </ul>
                        <p className="mt-2">To exercise these rights, contact <a href="mailto:privacy@nobleblocks.com" className="text-blue-600 hover:underline">privacy@nobleblocks.com</a>.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">8. Cookies</h2>
                        <p>We use cookies for:</p>
                        <ul className="list-disc pl-6 space-y-1">
                            <li><strong>Essential</strong>: Authentication, session management, security</li>
                            <li><strong>Functional</strong>: User preferences, theme settings</li>
                            <li><strong>Analytics</strong>: Usage patterns to improve the Service</li>
                        </ul>
                        <p className="mt-2">You can manage cookie preferences through our cookie consent banner or your browser settings.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">9. Data Retention</h2>
                        <p>We retain your data for as long as your account is active. After account deletion, we retain minimal data for up to 90 days for backup recovery, then permanently delete it. Some data may be retained longer to comply with legal obligations.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">10. Children&apos;s Privacy</h2>
                        <p>The Service is not intended for users under 18. We do not knowingly collect data from children. If we learn we have collected data from a child under 18, we will delete it promptly.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">11. Changes to This Policy</h2>
                        <p>We may update this Privacy Policy periodically. We will notify you of material changes via email or in-app notification. The &quot;Last updated&quot; date at the top reflects the most recent revision.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mt-8 mb-3">12. Contact Us</h2>
                        <p>For privacy-related questions or requests:</p>
                        <p className="mt-2">
                            NobleBlocks LLC<br />
                            Email: <a href="mailto:privacy@nobleblocks.com" className="text-blue-600 hover:underline">privacy@nobleblocks.com</a>
                        </p>
                    </section>
                </div>
            </div>
        </main>
    );
}
