import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Leaderboard() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-blue-900 text-white">
      <Head>
        <title>Leaderboard | Prisoner's Dilemma Arena</title>
        <meta name="description" content="Agent rankings in the Prisoner's Dilemma Arena" />
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
            <Link href="/leaderboard" className="text-blue-400 transition-colors">Leaderboard</Link>
            <Link href="/docs" className="hover:text-blue-400 transition-colors">API Docs</Link>
            <Link href="/login" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">Login</Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">Agent Leaderboard</h1>
          <p className="text-gray-300">Rankings of all agents based on their performance in tournaments.</p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div className="flex space-x-2 mb-4 md:mb-0">
            <button className="bg-blue-600 px-4 py-2 rounded-md">All Time</button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-md">Weekly</button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-md">Daily</button>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search agents..."
              className="bg-gray-800 px-4 py-2 rounded-md w-full md:w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="bg-gray-800 bg-opacity-50 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-900">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Agent</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Matches</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Avg. Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Total Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {/* Sample data - would be replaced with actual API data */}
                <tr className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-yellow-500 flex items-center justify-center text-black font-bold">1</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">TitForTatBot</div>
                    <div className="text-xs text-gray-400">Cooperates first, then mirrors opponent's last move</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">128</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400">3.14</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">402</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Link href="/agents/1" className="text-blue-400 hover:text-blue-300">View Details</Link>
                  </td>
                </tr>
                <tr className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center text-black font-bold">2</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">GrimTriggerBot</div>
                    <div className="text-xs text-gray-400">Cooperates until opponent defects, then always defects</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">128</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400">2.89</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">370</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Link href="/agents/2" className="text-blue-400 hover:text-blue-300">View Details</Link>
                  </td>
                </tr>
                <tr className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-orange-600 flex items-center justify-center text-black font-bold">3</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">PavlovBot</div>
                    <div className="text-xs text-gray-400">Starts with cooperation, switches if outcome is unfavorable</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">128</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400">2.76</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">353</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Link href="/agents/3" className="text-blue-400 hover:text-blue-300">View Details</Link>
                  </td>
                </tr>
                <tr className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-600 flex items-center justify-center text-white font-bold">4</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">ForgivingBot</div>
                    <div className="text-xs text-gray-400">Mostly cooperates but occasionally forgives defections</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">128</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400">2.65</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">339</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Link href="/agents/4" className="text-blue-400 hover:text-blue-300">View Details</Link>
                  </td>
                </tr>
                <tr className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-600 flex items-center justify-center text-white font-bold">5</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">RandomBot</div>
                    <div className="text-xs text-gray-400">Makes random decisions with equal probability</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">128</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-yellow-400">2.12</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">271</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Link href="/agents/5" className="text-blue-400 hover:text-blue-300">View Details</Link>
                  </td>
                </tr>
                <tr className="hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-600 flex items-center justify-center text-white font-bold">6</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">AlwaysDefectBot</div>
                    <div className="text-xs text-gray-400">Always defects regardless of history</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">128</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-red-400">1.87</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">239</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Link href="/agents/6" className="text-blue-400 hover:text-blue-300">View Details</Link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Pagination */}
        <div className="flex justify-center mt-8">
          <nav className="flex items-center space-x-2">
            <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600 disabled:opacity-50">Previous</button>
            <button className="px-3 py-1 rounded-md bg-blue-600">1</button>
            <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">2</button>
            <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">3</button>
            <span className="px-3 py-1">...</span>
            <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">10</button>
            <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">Next</button>
          </nav>
        </div>
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
