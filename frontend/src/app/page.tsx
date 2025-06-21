import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-blue-900 text-white">
      <Head>
        <title>Prisoner's Dilemma Arena</title>
        <meta name="description" content="A platform for hosting Iterated Prisoner's Dilemma tournaments" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <div className="text-3xl font-bold text-blue-400">Prisoner's Dilemma Arena</div>
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
        {/* Hero Section */}
        <section className="flex flex-col md:flex-row items-center justify-between py-12">
          <div className="md:w-1/2 mb-8 md:mb-0">
            <h1 className="text-5xl font-bold mb-6">
              Test Your Strategy in the Ultimate Game Theory Challenge
            </h1>
            <p className="text-xl mb-8 text-gray-300">
              Develop AI agents to compete in Iterated Prisoner's Dilemma tournaments. 
              Connect via our API and climb the leaderboard with your winning strategy.
            </p>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
              <Link href="/register" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md text-center transition-colors">
                Register Agent
              </Link>
              <Link href="/docs" className="border border-blue-600 text-blue-400 hover:bg-blue-900 px-6 py-3 rounded-md text-center transition-colors">
                API Documentation
              </Link>
            </div>
          </div>
          <div className="md:w-1/2 flex justify-center">
            <div className="relative w-full max-w-md">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg transform rotate-3"></div>
              <div className="relative bg-gray-800 p-6 rounded-lg shadow-xl">
                <pre className="text-sm text-green-400 overflow-x-auto">
{`{
  "match_id": "xyz123",
  "round": 4,
  "history": [
    {"self": "C", "opponent": "D"},
    {"self": "D", "opponent": "D"},
    {"self": "C", "opponent": "C"}
  ]
}

// Your agent responds:
{ "move": "C" }`}
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Game Theory Section */}
        <section className="py-16">
          <h2 className="text-3xl font-bold mb-8 text-center">Understanding the Prisoner's Dilemma</h2>
          <div className="grid md:grid-cols-2 gap-12">
            <div className="bg-gray-800 bg-opacity-50 p-8 rounded-lg">
              <h3 className="text-2xl font-bold mb-4 text-blue-400">Game Rules</h3>
              <p className="mb-4">The Iterated Prisoner's Dilemma is a classic game theory scenario where two players must choose to either cooperate or defect.</p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="px-4 py-2 text-left">Agent A</th>
                      <th className="px-4 py-2 text-left">Agent B</th>
                      <th className="px-4 py-2 text-left">A's Score</th>
                      <th className="px-4 py-2 text-left">B's Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-700">
                      <td className="px-4 py-2">Cooperate</td>
                      <td className="px-4 py-2">Cooperate</td>
                      <td className="px-4 py-2 text-green-400">3</td>
                      <td className="px-4 py-2 text-green-400">3</td>
                    </tr>
                    <tr className="border-b border-gray-700">
                      <td className="px-4 py-2">Cooperate</td>
                      <td className="px-4 py-2">Defect</td>
                      <td className="px-4 py-2 text-red-400">0</td>
                      <td className="px-4 py-2 text-green-400">5</td>
                    </tr>
                    <tr className="border-b border-gray-700">
                      <td className="px-4 py-2">Defect</td>
                      <td className="px-4 py-2">Cooperate</td>
                      <td className="px-4 py-2 text-green-400">5</td>
                      <td className="px-4 py-2 text-red-400">0</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2">Defect</td>
                      <td className="px-4 py-2">Defect</td>
                      <td className="px-4 py-2 text-yellow-400">1</td>
                      <td className="px-4 py-2 text-yellow-400">1</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div className="bg-gray-800 bg-opacity-50 p-8 rounded-lg">
              <h3 className="text-2xl font-bold mb-4 text-blue-400">Tournament Structure</h3>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-1">
                    <span className="text-sm font-bold">1</span>
                  </div>
                  <p>Each match consists of 200 rounds by default</p>
                </li>
                <li className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-1">
                    <span className="text-sm font-bold">2</span>
                  </div>
                  <p>Tournaments use round-robin format where each agent plays against all others</p>
                </li>
                <li className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-1">
                    <span className="text-sm font-bold">3</span>
                  </div>
                  <p>Agents receive match history and must respond within 200ms</p>
                </li>
                <li className="flex items-start">
                  <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center mr-3 mt-1">
                    <span className="text-sm font-bold">4</span>
                  </div>
                  <p>Leaderboard ranks agents by their average score across all matches</p>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Getting Started Section */}
        <section className="py-16">
          <h2 className="text-3xl font-bold mb-8 text-center">Getting Started</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gray-800 bg-opacity-50 p-6 rounded-lg">
              <div className="h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">1. Register Your Agent</h3>
              <p className="text-gray-300">Create an account and register your agent with a callback URL where it will receive game requests.</p>
            </div>
            <div className="bg-gray-800 bg-opacity-50 p-6 rounded-lg">
              <div className="h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">2. Implement Your Strategy</h3>
              <p className="text-gray-300">Develop your agent to receive match history and respond with moves according to your strategy.</p>
            </div>
            <div className="bg-gray-800 bg-opacity-50 p-6 rounded-lg">
              <div className="h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">3. Compete in Tournaments</h3>
              <p className="text-gray-300">Join tournaments to test your agent against others and climb the leaderboard with your winning strategy.</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-gray-900 py-8">
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
