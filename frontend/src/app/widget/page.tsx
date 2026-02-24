"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function WidgetPreview() {
  const params = useSearchParams();
  const embedKey = params.get("key") || "";

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Widget Preview
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          This is a preview of how the chat widget will appear on your website.
        </p>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-8 min-h-[400px] border border-gray-200 dark:border-gray-700">
          <p className="text-gray-500 dark:text-gray-400">
            Your website content would appear here. The chat widget bubble is in
            the bottom-right corner.
          </p>
        </div>
      </div>
      {embedKey && (
        <script
          src="/widget/chat.js"
          data-key={embedKey}
          data-api=""
        />
      )}
    </div>
  );
}

export default function WidgetPage() {
  return (
    <Suspense fallback={<div className="p-8">Loading preview...</div>}>
      <WidgetPreview />
    </Suspense>
  );
}
