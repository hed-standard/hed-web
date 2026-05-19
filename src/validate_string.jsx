import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { ErrorDisplay } from "./components/ErrorDisplay";
import {
  buildSchemasFromVersion,
  parseStandaloneString,
  BidsHedIssue,
} from "hed-validator";

// --- Add TailwindCSS to the document head for immediate styling ---
(() => {
  if (!document.querySelector('script[src="https://cdn.tailwindcss.com"]')) {
    const script = document.createElement("script");
    script.src = "https://cdn.tailwindcss.com";
    document.head.appendChild(script);
  }
})();

// --- Main Application Component ---

function ValidateStringApp() {
  const [hedString, setHedString] = useState("");
  const [hedVersion, setHedVersion] = useState("8.4.0");
  const [checkWarnings, setCheckWarnings] = useState(false);
  const [errors, setErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [validated, setValidated] = useState(false);

  function handleClear() {
    setHedString("");
    setHedVersion("8.4.0");
    setCheckWarnings(false);
    setErrors([]);
    setSuccessMessage("");
    setValidated(false);
  }

  function formatRawIssues(rawIssues, severity) {
    return rawIssues.map((issue) => ({
      issueMessage: issue.issueMessage || String(issue),
      severity,
    }));
  }

  async function handleValidation() {
    if (!hedString.trim()) return;
    setIsLoading(true);
    setErrors([]);
    setSuccessMessage("");
    setValidated(true);

    try {
      const hedSchemas = await buildSchemasFromVersion(hedVersion.trim());
      const [, rawErrors, rawWarnings] = parseStandaloneString(
        hedString.trim(),
        hedSchemas,
        null,
      );

      const formattedErrors = formatRawIssues(rawErrors, "error");
      const formattedWarnings = checkWarnings
        ? formatRawIssues(rawWarnings, "warning")
        : [];
      const allIssues = [...formattedErrors, ...formattedWarnings];

      if (allIssues.length > 0) {
        setErrors(allIssues);
      } else {
        setSuccessMessage("No validation issues found.");
      }
    } catch (err) {
      setErrors([
        {
          issueMessage: err.message || String(err),
          severity: "error",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <header className="text-center mb-10">
          <a
            href="./"
            className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 mb-4 block"
          >
            &larr; Back to Home
          </a>
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white">
            Validate a HED string
          </h1>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Validate a HED annotation string against a specified schema version.
            <br />
            This tool is browser-based -- all data remains local.
          </p>
        </header>

        <main className="bg-white dark:bg-gray-800/50 p-6 md:p-8 rounded-xl shadow-lg ring-1 ring-gray-200 dark:ring-gray-700">
          <div className="flex flex-col gap-6">
            {/* HED String textarea */}
            <div>
              <label
                htmlFor="hed-string-input"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                HED String
              </label>
              <textarea
                id="hed-string-input"
                value={hedString}
                onChange={(e) => setHedString(e.target.value)}
                placeholder="e.g. Sensory-event, (Red, Large)"
                rows={5}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
            </div>

            {/* HED version and options */}
            <div className="flex flex-wrap gap-6 items-center">
              <div className="flex items-center gap-3">
                <label
                  htmlFor="hed-version"
                  className="text-gray-600 dark:text-gray-400 whitespace-nowrap"
                >
                  HED schema version
                </label>
                <input
                  id="hed-version"
                  type="text"
                  value={hedVersion}
                  onChange={(e) => setHedVersion(e.target.value)}
                  title="Enter the HED schema version (e.g. 8.4.0)"
                  className="w-28 px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>

              <div className="flex items-center">
                <input
                  id="check-warnings"
                  type="checkbox"
                  checked={checkWarnings}
                  onChange={(e) => setCheckWarnings(e.target.checked)}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <label
                  htmlFor="check-warnings"
                  className="ml-2 text-gray-600 dark:text-gray-400"
                >
                  Check warnings
                </label>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex gap-4">
              <button
                onClick={handleValidation}
                disabled={isLoading || !hedString.trim() || !hedVersion.trim()}
                className="w-36 px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 disabled:dark:bg-gray-600"
              >
                {isLoading ? "Validating..." : "Validate"}
              </button>
              <button
                onClick={handleClear}
                className="w-36 px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-all duration-300"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Results */}
          {validated && !isLoading && (
            <>
              {successMessage && (
                <div className="text-center mt-4">
                  <p className="text-green-600 dark:text-green-400">
                    {successMessage}
                  </p>
                </div>
              )}
              {errors.length > 0 && <ErrorDisplay errors={errors} />}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

// --- Mount the App to the DOM ---

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <ValidateStringApp />
  </React.StrictMode>,
);
