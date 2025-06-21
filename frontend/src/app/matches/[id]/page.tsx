import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function MatchDetail() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-blue-900 text-white">
      <Head>
        <title>Match Details | Prisoner's Dilemma Arena</title>
        <meta name="description" content="Detailed match information in the Prisoner's Dilemma Arena" />
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
        <div className="mb-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
            <div>
              <h1 className="text-4xl font-bold mb-2">Match #12345</h1>
              <p className="text-gray-300">Part of <Link href="/tournaments/1" className="text-blue-400 hover:text-blue-300">Weekly Championship Tournament</Link></p>
            </div>
            <div className="mt-4 md:mt-0 flex space-x-4">
              <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">
                Download JSON
              </button>
              <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-md transition-colors">
                Download CSV
              </button>
            </div>
          </div>
        </div>

        {/* Match Summary */}
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Match Summary</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-bold text-blue-400">TitForTatBot</h3>
                  <p className="text-sm text-gray-300">Cooperates first, then mirrors opponent's last move</p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-green-400">3.15</p>
                  <p className="text-sm text-gray-300">Average Score</p>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-bold text-red-400">AlwaysDefectBot</h3>
                  <p className="text-sm text-gray-300">Always defects regardless of history</p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-yellow-400">1.95</p>
                  <p className="text-sm text-gray-300">Average Score</p>
                </div>
              </div>
            </div>
            <div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-400">Rounds</p>
                  <p className="text-lg font-semibold">200</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Status</p>
                  <p className="text-lg font-semibold text-green-400">Complete</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Started</p>
                  <p className="text-sm">Jun 15, 2025 14:30:12 UTC</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Completed</p>
                  <p className="text-sm">Jun 15, 2025 14:32:45 UTC</p>
                </div>
              </div>
              <div className="mt-4">
                <p className="text-xs text-gray-400">Mutual Cooperation Rate</p>
                <div className="w-full bg-gray-700 rounded-full h-2.5 mt-1 mb-1">
                  <div className="bg-green-600 h-2.5 rounded-full" style={{ width: '12%' }}></div>
                </div>
                <p className="text-xs text-right">12%</p>
              </div>
              <div className="mt-2">
                <p className="text-xs text-gray-400">Mutual Defection Rate</p>
                <div className="w-full bg-gray-700 rounded-full h-2.5 mt-1 mb-1">
                  <div className="bg-red-600 h-2.5 rounded-full" style={{ width: '88%' }}></div>
                </div>
                <p className="text-xs text-right">88%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Match Visualization */}
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Match Visualization</h2>
          <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
            <p className="text-gray-400">Interactive match visualization chart would appear here</p>
          </div>
          <div className="flex justify-center mt-4">
            <div className="flex items-center mr-6">
              <div className="w-4 h-4 bg-blue-400 rounded-sm mr-2"></div>
              <span className="text-sm">TitForTatBot</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-red-400 rounded-sm mr-2"></div>
              <span className="text-sm">AlwaysDefectBot</span>
            </div>
          </div>
        </div>

        {/* Round Details */}
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Round Details</h2>
            <div className="flex items-center">
              <label className="mr-2 text-sm">Show:</label>
              <select className="bg-gray-700 border border-gray-600 rounded-md py-1 px-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>All Rounds</option>
                <option>First 10 Rounds</option>
                <option>Last 10 Rounds</option>
                <option>Mutual Cooperation</option>
                <option>Mutual Defection</option>
              </select>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-700">
                  <th className="px-4 py-2 text-left">Round</th>
                  <th className="px-4 py-2 text-left">TitForTatBot</th>
                  <th className="px-4 py-2 text-left">AlwaysDefectBot</th>
                  <th className="px-4 py-2 text-left">TitForTatBot Score</th>
                  <th className="px-4 py-2 text-left">AlwaysDefectBot Score</th>
                  <th className="px-4 py-2 text-left">Response Time (ms)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                <tr>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2"><span className="text-green-400">Cooperate</span></td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2">0</td>
                  <td className="px-4 py-2">5</td>
                  <td className="px-4 py-2">12 / 8</td>
                </tr>
                <tr>
                  <td className="px-4 py-2">2</td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">10 / 7</td>
                </tr>
                <tr>
                  <td className="px-4 py-2">3</td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">9 / 8</td>
                </tr>
                <tr>
                  <td className="px-4 py-2">4</td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">11 / 7</td>
                </tr>
                <tr>
                  <td className="px-4 py-2">5</td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2"><span className="text-red-400">Defect</span></td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">1</td>
                  <td className="px-4 py-2">10 / 8</td>
                </tr>
                {/* More rows would be added here */}
              </tbody>
            </table>
          </div>
          <div className="flex justify-center mt-6">
            <nav className="flex items-center space-x-2">
              <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600 disabled:opacity-50">Previous</button>
              <button className="px-3 py-1 rounded-md bg-blue-600">1</button>
              <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">2</button>
              <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">3</button>
              <span className="px-3 py-1">...</span>
              <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">20</button>
              <button className="px-3 py-1 rounded-md bg-gray-700 hover:bg-gray-600">Next</button>
            </nav>
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
