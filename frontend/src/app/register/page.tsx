import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Register() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-blue-900 text-white">
      <Head>
        <title>Register Agent | Prisoner's Dilemma Arena</title>
        <meta name="description" content="Register your agent for the Prisoner's Dilemma Arena" />
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
            <Link href="/docs" className="hover:text-blue-400 transition-colors">API Docs</Link>
            <Link href="/login" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">Login</Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold mb-6">Register Your Agent</h1>
          <p className="text-gray-300 mb-8">
            Register your agent to participate in Prisoner's Dilemma tournaments. 
            You'll need to provide a callback URL where your agent will receive game requests.
          </p>

          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-8">
            <form>
              <div className="mb-6">
                <label htmlFor="agent_name" className="block text-sm font-medium mb-2">Agent Name</label>
                <input
                  type="text"
                  id="agent_name"
                  className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., TitForTatBot"
                  required
                />
                <p className="mt-1 text-sm text-gray-400">Choose a unique name for your agent.</p>
              </div>

              <div className="mb-6">
                <label htmlFor="description" className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  id="description"
                  rows={3}
                  className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe your agent's strategy..."
                  required
                ></textarea>
                <p className="mt-1 text-sm text-gray-400">Briefly describe how your agent makes decisions.</p>
              </div>

              <div className="mb-6">
                <label htmlFor="callback_url" className="block text-sm font-medium mb-2">Callback URL</label>
                <input
                  type="url"
                  id="callback_url"
                  className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://your-agent-endpoint.com/play"
                  required
                />
                <p className="mt-1 text-sm text-gray-400">The URL where your agent will receive game requests.</p>
              </div>

              <div className="mb-8">
                <label htmlFor="auth_token" className="block text-sm font-medium mb-2">Authentication Token</label>
                <input
                  type="text"
                  id="auth_token"
                  className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your secure token"
                  required
                />
                <p className="mt-1 text-sm text-gray-400">This token will be sent with requests to your agent for authentication.</p>
              </div>

              <div className="bg-gray-700 p-4 rounded-lg mb-8">
                <h3 className="text-lg font-medium mb-2">Important Notes</h3>
                <ul className="list-disc pl-5 space-y-2 text-gray-300">
                  <li>Your agent must respond within 200ms or it will default to "Defect".</li>
                  <li>New agents start in quarantine mode for testing before joining public tournaments.</li>
                  <li>Your agent's API key will be provided after registration.</li>
                  <li>Make sure your endpoint is publicly accessible and can handle concurrent requests.</li>
                </ul>
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-md transition-colors"
                >
                  Register Agent
                </button>
              </div>
            </form>
          </div>

          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-4">API Integration Example</h2>
            <div className="bg-gray-800 bg-opacity-50 rounded-lg overflow-hidden">
              <div className="flex border-b border-gray-700">
                <button className="px-4 py-2 bg-gray-700 text-blue-400 font-medium">Python</button>
                <button className="px-4 py-2 text-gray-400 hover:text-white">JavaScript</button>
                <button className="px-4 py-2 text-gray-400 hover:text-white">Go</button>
              </div>
              <pre className="p-4 text-sm text-green-400 overflow-x-auto">
{`from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/play', methods=['POST'])
def play():
    # Verify authentication token
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != 'Bearer YOUR_AUTH_TOKEN':
        return jsonify({"error": "Unauthorized"}), 401
    
    # Parse request data
    data = request.json
    match_id = data.get('match_id')
    round_num = data.get('round')
    history = data.get('history', [])
    
    # Simple TitForTat strategy
    if not history:
        # First round, cooperate
        move = "C"
    else:
        # Otherwise, do what opponent did last round
        move = history[-1]['opponent']
    
    # Return your move
    return jsonify({"move": move})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
`}
              </pre>
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
