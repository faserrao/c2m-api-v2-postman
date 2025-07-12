import React from "react";
import Head from "next/head";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 py-10 px-6">
      <Head>
        <title>LOB API Docs</title>
      </Head>
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-2xl shadow-xl">
        <h1 className="text-3xl font-bold mb-4">LOB API Documentation</h1>
        <p className="text-gray-700 mb-6">
          View interactive documentation, download the spec, or explore generated SDKs.
        </p>
        <ul className="space-y-4">
          <li>
            <Link href="/swagger.html" target="_blank" className="text-blue-600 hover:underline">
              👉 Swagger UI Viewer
            </Link>
          </li>
          <li>
            <Link href="/redoc.html" target="_blank" className="text-blue-600 hover:underline">
              👉 ReDoc Viewer
            </Link>
          </li>
          <li>
            <a
              href="/lob_openapi_spec_final.yaml"
              target="_blank"
              className="text-blue-600 hover:underline"
            >
              📄 Download OpenAPI YAML
            </a>
          </li>
          <li>
            <a
              href="https://github.com/YOUR_USERNAME/YOUR_REPO_NAME"
              target="_blank"
              className="text-blue-600 hover:underline"
            >
              🔗 GitHub Repository
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}