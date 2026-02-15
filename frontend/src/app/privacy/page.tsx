import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <div className="max-w-3xl mx-auto px-6 py-16 space-y-8">
        <div className="space-y-2">
          <Link
            href="/"
            className="text-sm text-accent hover:underline"
          >
            &larr; Back to home
          </Link>
          <h1 className="text-3xl font-bold">Privacy Policy</h1>
          <p className="text-text-tertiary text-sm">
            Last updated: February 15, 2026
          </p>
        </div>

        <div className="prose prose-invert max-w-none space-y-6 text-text-secondary">
          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              1. Information We Collect
            </h2>
            <p>
              <strong>Account Information:</strong> When you create an account,
              we collect your email address and display name. If you sign in via
              Google, we receive your name and email from Google.
            </p>
            <p>
              <strong>Preference Data:</strong> Genre preferences, mood
              selections, dealbreakers, and other inputs you provide when
              requesting recommendations.
            </p>
            <p>
              <strong>Usage Data:</strong> We collect anonymized analytics about
              how you interact with the app, including pages viewed, features
              used, and recommendation outcomes.
            </p>
            <p>
              <strong>Device Information:</strong> Browser type, operating
              system, and screen size for optimizing your experience.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              2. How We Use Your Information
            </h2>
            <ul className="list-disc pl-6 space-y-1.5">
              <li>To generate personalized movie recommendations</li>
              <li>To improve recommendation quality over time through your taste profile</li>
              <li>To enable group recommendation sessions</li>
              <li>To communicate with you about your account and service updates</li>
              <li>To monitor and improve application performance and reliability</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              3. AI Processing
            </h2>
            <p>
              Your preference data is sent to Anthropic&apos;s Claude AI to
              generate recommendations. This data is processed in real-time
              and is not stored by Anthropic beyond the immediate request.
              We do not send personally identifiable information to the AI
              model.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              4. Data Sharing
            </h2>
            <p>
              We do not sell your personal data. We share data only with:
            </p>
            <ul className="list-disc pl-6 space-y-1.5">
              <li>
                <strong>Anthropic:</strong> Anonymized preference data for AI
                recommendation processing
              </li>
              <li>
                <strong>TMDB:</strong> Movie data queries (no personal data shared)
              </li>
              <li>
                <strong>Analytics providers:</strong> Anonymized usage data for
                product improvement
              </li>
              <li>
                <strong>Error tracking:</strong> Technical error reports
                (Sentry) that may include browser/device information
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              5. Data Retention
            </h2>
            <p>
              Active session data is stored temporarily in Redis (30-minute TTL).
              Account data and watch history are retained as long as your account
              is active. You can delete your account and all associated data at
              any time from your profile settings.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              6. Your Rights
            </h2>
            <p>You have the right to:</p>
            <ul className="list-disc pl-6 space-y-1.5">
              <li>Access the personal data we hold about you</li>
              <li>Request correction of inaccurate data</li>
              <li>Request deletion of your data</li>
              <li>Export your data in a portable format</li>
              <li>Opt out of analytics tracking</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              7. Cookies
            </h2>
            <p>
              We use essential cookies for authentication and session management.
              Analytics cookies are used only with your consent. You can manage
              cookie preferences in your browser settings.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-text-primary">
              8. Contact
            </h2>
            <p>
              For privacy-related questions or requests, contact us at{" "}
              <a
                href="mailto:privacy@filmmatch.ai"
                className="text-accent hover:underline"
              >
                privacy@filmmatch.ai
              </a>
              .
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
