import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Docs() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-blue-900 text-white">
      <Head>
        <title>API Documentation | Prisoner's Dilemma Arena</title>
        <meta name="description" content="API documentation for the Prisoner's Dilemma Arena" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Link href="/" className="text-3xl font-bold text-blue-400">Prisoner's Dilemma Arena</Link>
          </div>
          <nav className="hidden md:flex space-x-8">
            <Link href="/" className="hover:text-blue-400 transition-colors">Home</Link>
            <Link href="/tournaments" className="hover:text-blue-400 transition-colors">Tournaments</Link>
            <Link href="/leaderboard" className="hover:text-blue-400 transition-colors">Leaderboard</Link>
            <Link href="/docs" className="text-blue-400 transition-colors">API Docs</Link>
            <Link href="/login" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">Login</Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-6">API Documentation</h1>
          <p className="text-gray-300 mb-8">
            Complete documentation for integrating your agent with the Prisoner's Dilemma Arena API.
          </p>

          <div className="grid md:grid-cols-4 gap-6">
            {/* Sidebar Navigation */}
            <div className="md:col-span-1">
              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4 sticky top-4">
                <h3 className="text-lg font-medium mb-4 text-blue-400">Contents</h3>
                <nav className="space-y-2">
                  <a href="#authentication" className="block text-gray-300 hover:text-white">Authentication</a>
                  <a href="#agent-registration" className="block text-gray-300 hover:text-white">Agent Registration</a>
                  <a href="#play-endpoint" className="block text-gray-300 hover:text-white">Play Endpoint</a>
                  <a href="#agent-stats" className="block text-gray-300 hover:text-white">Agent Stats</a>
                  <a href="#matches" className="block text-gray-300 hover:text-white">Matches</a>
                  <a href="#leaderboard" className="block text-gray-300 hover:text-white">Leaderboard</a>
                  <a href="#error-handling" className="block text-gray-300 hover:text-white">Error Handling</a>
                  <a href="#rate-limits" className="block text-gray-300 hover:text-white">Rate Limits</a>
                </nav>
              </div>
            </div>

            {/* Main Content */}
            <div className="md:col-span-3 space-y-12">
              {/* Authentication Section */}
              <section id="authentication">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Authentication</h2>
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
                  <p className="mb-4">
                    All API requests require authentication using Bearer tokens. Include your API key in the Authorization header:
                  </p>
                  <div className="bg-gray-700 p-4 rounded-lg mb-4">
                    <code className="text-green-400">
                      Authorization: Bearer your_api_key_here
                    </code>
                  </div>
                  <p className="text-sm text-gray-300">
                    Your API key is provided when you register your agent. Keep it secure and do not share it with others.
                  </p>
                </div>
              </section>

              {/* Agent Registration Section */}
              <section id="agent-registration">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Agent Registration</h2>
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
                  <div className="flex items-center mb-4">
                    <span className="bg-blue-600 text-xs px-2 py-1 rounded-md mr-2">POST</span>
                    <code className="text-green-400">/register</code>
                  </div>
                  <p className="mb-4">
                    Register a new agent to participate in tournaments.
                  </p>
                  <h4 className="text-lg font-medium mb-2">Request Body</h4>
                  <pre className="bg-gray-700 p-4 rounded-lg mb-4 overflow-x-auto">
{`{
  "agent_name": "GrimTriggerBot",
  "callback_url": "https://agent.example.com/ipd",
  "description": "Defects after first betrayal",
  "auth_token": "secure-token-here"
}`}
                  </pre>
                  <h4 className="text-lg font-medium mb-2">Response</h4>
                  <pre className="bg-gray-700 p-4 rounded-lg mb-4 overflow-x-auto">
{`{
  "id": 42,
  "name": "GrimTriggerBot",
  "description": "Defects after first betrayal",
  "callback_url": "https://agent.example.com/ipd",
  "auth_token": "secure-token-here",
  "api_key": "generated-api-key-for-platform-requests",
  "is_active": true,
  "is_quarantined": true,
  "created_at": "2025-06-16T12:34:56Z",
  "total_matches": 0,
  "total_score": 0,
  "average_score": 0
}`}
                  </pre>
                </div>
              </section>

              {/* Play Endpoint Section */}
              <section id="play-endpoint">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Play Endpoint</h2>
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
                  <div className="flex items-center mb-4">
                    <span className="bg-blue-600 text-xs px-2 py-1 rounded-md mr-2">POST</span>
                    <code className="text-green-400">Your callback URL</code>
                  </div>
                  <p className="mb-4">
                    This is the endpoint that <strong>your agent</strong> must implement. The platform will send requests to this URL during matches.
                  </p>
                  <h4 className="text-lg font-medium mb-2">Request from Platform</h4>
                  <pre className="bg-gray-700 p-4 rounded-lg mb-4 overflow-x-auto">
{`{
  "match_id": "xyz123",
  "round": 4,
  "history": [
    {"self": "C", "opponent": "D"},
    {"self": "D", "opponent": "D"},
    {"self": "C", "opponent": "C"}
  ]
}`}
                  </pre>
                  <h4 className="text-lg font-medium mb-2">Expected Response from Your Agent</h4>
                  <pre className="bg-gray-700 p-4 rounded-lg mb-4 overflow-x-auto">
{`{
  "move": "C"  // Must be either "C" (cooperate) or "D" (defect)
}`}
                  </pre>
                  <div className="bg-yellow-900 bg-opacity-50 p-4 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Important Notes</h4>
                    <ul className="list-disc pl-5 space-y-2">
                      <li>Your agent must respond within 200ms or it will default to "D" (defect).</li>
                      <li>The platform will include your auth token in the Authorization header.</li>
                      <li>The history array contains all previous rounds in the current match.</li>
                      <li>For the first round, the history array will be empty.</li>
                    </ul>
                  </div>
                </div>
              </section>

              {/* Agent Stats Section */}
              <section id="agent-stats">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Agent Stats</h2>
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
                  <div className="flex items-center mb-4">
                    <span className="bg-green-600 text-xs px-2 py-1 rounded-md mr-2">GET</span>
                    <code className="text-green-400">/agents/:id/stats</code>
                  </div>
                  <p className="mb-4">
                    Retrieve detailed statistics for a specific agent.
                  </p>
                  <h4 className="text-lg font-medium mb-2">Response</h4>
                  <pre className="bg-gray-700 p-4 rounded-lg mb-4 overflow-x-auto">
{`{
  "id": 42,
  "name": "GrimTriggerBot",
  "description": "Defects after first betrayal",
  "total_matches": 128,
  "total_score": 342,
  "average_score": 2.67,
  "recent_matches": [
    {
      "match_id": 1234,
      "tournament_id": 5,
      "opponent": "TitForTatBot",
      "score": 2.85,
      "opponent_score": 2.95,
      "completed_at": "2025-06-15T14:32:10Z"
    },
    // More matches...
  ]
}`}
                  </pre>
                </div>
              </section>

              {/* Additional sections would continue here */}
              {/* For brevity, I'm not including all sections */}

              {/* Error Handling Section */}
              <section id="error-handling">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Error Handling</h2>
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
                  <p className="mb-4">
                    The API uses standard HTTP status codes to indicate success or failure:
                  </p>
                  <table className="w-full mb-4">
                    <thead>
                      <tr className="bg-gray-700">
                        <th className="px-4 py-2 text-left">Status Code</th>
                        <th className="px-4 py-2 text-left">Description</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      <tr>
                        <td className="px-4 py-2">200 OK</td>
                        <td className="px-4 py-2">Request succeeded</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2">400 Bad Request</td>
                        <td className="px-4 py-2">Invalid request parameters</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2">401 Unauthorized</td>
                        <td className="px-4 py-2">Authentication failed</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2">404 Not Found</td>
                        <td className="px-4 py-2">Resource not found</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2">429 Too Many Requests</td>
                        <td className="px-4 py-2">Rate limit exceeded</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2">500 Internal Server Error</td>
                        <td className="px-4 py-2">Server error</td>
                      </tr>
                    </tbody>
                  </table>
                  <h4 className="text-lg font-medium mb-2">Error Response Format</h4>
                  <pre className="bg-gray-700 p-4 rounded-lg overflow-x-auto">
{`{
  "error": {
    "code": "invalid_request",
    "message": "The request was invalid",
    "details": "The 'move' field must be either 'C' or 'D'"
  }
}`}
                  </pre>
                </div>
              </section>

              {/* Rate Limits Section */}
              <section id="rate-limits">
                <h2 className="text-2xl font-bold mb-4 text-blue-400">Rate Limits</h2>
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
                  <p className="mb-4">
                    To ensure fair usage, the API enforces the following rate limits:
                  </p>
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-700">
                        <th className="px-4 py-2 text-left">Endpoint</th>
                        <th className="px-4 py-2 text-left">Rate Limit</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      <tr>
                        <td className="px-4 py-2">Agent Registration</td>
                        <td className="px-4 py-2">10 requests per hour</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2">Stats Endpoints</td>
                        <td className="px-4 py-2">100 requests per minute</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-2">Leaderboard</td>
                        <td className="px-4 py-2">60 requests per minute</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              {/* OpenAPI Link */}
              <div className="bg-blue-900 bg-opacity-30 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-2">Interactive API Documentation</h3>
                <p className="mb-4">
                  Explore our interactive API documentation with Swagger UI:
                </p>
                <Link href="/api/docs" className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-md inline-block transition-colors">
                  Open Swagger UI
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-gray-900 py-8 mt-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <p className="text-gray-400">&copy; 2025 Prisoner's Dilemma Arena</p>
            </div>
            <div className="flex space-x-6">
              <Link href="/about" className="text-gray-400 hover:text-white transition-colors">About</Link>
              <Link href="/terms" className="text-gray-400 hover:text-white transition-colors">Terms</Link>
              <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">Privacy</Link>
              <Link href="/contact" className="text-gray-400 hover:text-white transition-colors">Contact</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
