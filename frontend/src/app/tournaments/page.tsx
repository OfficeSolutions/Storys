import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Tournaments() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-blue-900 text-white">
      <Head>
        <title>Tournaments | Prisoner's Dilemma Arena</title>
        <meta name="description" content="Active and past tournaments in the Prisoner's Dilemma Arena" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Link href="/" className="text-3xl font-bold text-blue-400">Prisoner's Dilemma Arena</Link>
          </div>
          <nav className="hidden md:flex space-x-8">
            <Link href="/" className="hover:text-blue-400 transition-colors">Home</Link>
            <Link href="/tournaments" className="text-blue-400 transition-colors">Tournaments</Link>
            <Link href="/leaderboard" className="hover:text-blue-400 transition-colors">Leaderboard</Link>
            <Link href="/docs" className="hover:text-blue-400 transition-colors">API Docs</Link>
            <Link href="/login" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">Login</Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Tournaments</h1>
            <p className="text-gray-300">View active and past tournaments, match details, and results.</p>
          </div>
          <div className="mt-4 md:mt-0">
            <button className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-md transition-colors">
              Create Tournament
            </button>
          </div>
        </div>

        {/* Tournament Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button className="border-b-2 border-blue-500 py-4 px-1 text-blue-400 font-medium">
                Active Tournaments
              </button>
              <button className="border-b-2 border-transparent py-4 px-1 text-gray-400 hover:text-gray-300 font-medium">
                Past Tournaments
              </button>
              <button className="border-b-2 border-transparent py-4 px-1 text-gray-400 hover:text-gray-300 font-medium">
                My Tournaments
              </button>
            </nav>
          </div>
        </div>

        {/* Active Tournaments */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Tournament Card 1 */}
          <div className="bg-gray-800 bg-opacity-50 rounded-lg overflow-hidden shadow-lg">
            <div className="p-6">
              <div className="flex justify-between items-start">
                <h3 className="text-xl font-bold mb-2">Weekly Championship</h3>
                <span className="bg-green-600 text-xs px-2 py-1 rounded-full">Active</span>
              </div>
              <p className="text-gray-300 text-sm mb-4">Round-robin tournament with 200 rounds per match.</p>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-400">Participants</p>
                  <p className="text-lg font-semibold">12 Agents</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Progress</p>
                  <p className="text-lg font-semibold">68%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Started</p>
                  <p className="text-sm">Jun 15, 2025</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Ends</p>
                  <p className="text-sm">Jun 22, 2025</p>
                </div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4">
                <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '68%' }}></div>
              </div>
              <Link href="/tournaments/1" className="block text-center bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">
                View Details
              </Link>
            </div>
          </div>

          {/* Tournament Card 2 */}
          <div className="bg-gray-800 bg-opacity-50 rounded-lg overflow-hidden shadow-lg">
            <div className="p-6">
              <div className="flex justify-between items-start">
                <h3 className="text-xl font-bold mb-2">Newcomers Challenge</h3>
                <span className="bg-green-600 text-xs px-2 py-1 rounded-full">Active</span>
              </div>
              <p className="text-gray-300 text-sm mb-4">Special tournament for newly registered agents.</p>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-400">Participants</p>
                  <p className="text-lg font-semibold">5 Agents</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Progress</p>
                  <p className="text-lg font-semibold">32%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Started</p>
                  <p className="text-sm">Jun 16, 2025</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Ends</p>
                  <p className="text-sm">Jun 18, 2025</p>
                </div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4">
                <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '32%' }}></div>
              </div>
              <Link href="/tournaments/2" className="block text-center bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">
                View Details
              </Link>
            </div>
          </div>

          {/* Tournament Card 3 */}
          <div className="bg-gray-800 bg-opacity-50 rounded-lg overflow-hidden shadow-lg">
            <div className="p-6">
              <div className="flex justify-between items-start">
                <h3 className="text-xl font-bold mb-2">Elite Showdown</h3>
                <span className="bg-yellow-600 text-xs px-2 py-1 rounded-full">Starting Soon</span>
              </div>
              <p className="text-gray-300 text-sm mb-4">Invitation-only tournament for top-ranked agents.</p>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-400">Participants</p>
                  <p className="text-lg font-semibold">8 Agents</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Progress</p>
                  <p className="text-lg font-semibold">0%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Starts</p>
                  <p className="text-sm">Jun 18, 2025</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Ends</p>
                  <p className="text-sm">Jun 25, 2025</p>
                </div>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4">
                <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '0%' }}></div>
              </div>
              <Link href="/tournaments/3" className="block text-center bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">
                View Details
              </Link>
            </div>
          </div>
        </div>

        {/* Featured Tournament */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Featured Tournament: Weekly Championship</h2>
          
          <div className="bg-gray-800 bg-opacity-50 rounded-lg overflow-hidden shadow-lg p-6">
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-2">Tournament Details</h3>
              <p className="text-gray-300 mb-4">
                Our weekly championship features the best agents competing in a round-robin format.
                Each match consists of 200 rounds of the Prisoner's Dilemma game.
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-400">Status</p>
                  <p className="text-lg font-semibold text-green-400">Active</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Matches</p>
                  <p className="text-lg font-semibold">66 / 96</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Started</p>
                  <p className="text-sm">Jun 15, 2025 14:30 UTC</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Estimated Completion</p>
                  <p className="text-sm">Jun 17, 2025 22:15 UTC</p>
                </div>
              </div>
            </div>
            
            {/* Current Leaders */}
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-4">Current Leaders</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-900">
                      <th className="px-4 py-2 text-left">Rank</th>
                      <th className="px-4 py-2 text-left">Agent</th>
                      <th className="px-4 py-2 text-left">Matches</th>
                      <th className="px-4 py-2 text-left">Avg. Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    <tr>
                      <td className="px-4 py-2">1</td>
                      <td className="px-4 py-2">TitForTatBot</td>
                      <td className="px-4 py-2">11</td>
                      <td className="px-4 py-2 text-green-400">3.21</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2">2</td>
                      <td className="px-4 py-2">GrimTriggerBot</td>
                      <td className="px-4 py-2">11</td>
                      <td className="px-4 py-2 text-green-400">2.95</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2">3</td>
                      <td className="px-4 py-2">PavlovBot</td>
                      <td className="px-4 py-2">11</td>
                      <td className="px-4 py-2 text-green-400">2.82</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            {/* Recent Matches */}
            <div>
              <h3 className="text-xl font-bold mb-4">Recent Matches</h3>
              <div className="space-y-4">
                <div className="bg-gray-700 p-4 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <span className="font-medium">TitForTatBot</span>
                      <span className="mx-2 text-green-400">3.15</span>
                      <span className="text-gray-400">vs</span>
                      <span className="mx-2 text-red-400">1.95</span>
                      <span className="font-medium">AlwaysDefectBot</span>
                    </div>
                    <Link href="/matches/123" className="text-blue-400 hover:text-blue-300 text-sm">
                      View Details
                    </Link>
                  </div>
                </div>
                
                <div className="bg-gray-700 p-4 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <span className="font-medium">GrimTriggerBot</span>
                      <span className="mx-2 text-green-400">3.05</span>
                      <span className="text-gray-400">vs</span>
                      <span className="mx-2 text-yellow-400">2.15</span>
                      <span className="font-medium">RandomBot</span>
                    </div>
                    <Link href="/matches/124" className="text-blue-400 hover:text-blue-300 text-sm">
                      View Details
                    </Link>
                  </div>
                </div>
                
                <div className="bg-gray-700 p-4 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <span className="font-medium">PavlovBot</span>
                      <span className="mx-2 text-green-400">2.85</span>
                      <span className="text-gray-400">vs</span>
                      <span className="mx-2 text-green-400">2.75</span>
                      <span className="font-medium">ForgivingBot</span>
                    </div>
                    <Link href="/matches/125" className="text-blue-400 hover:text-blue-300 text-sm">
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 text-center">
                <Link href="/tournaments/1/matches" className="text-blue-400 hover:text-blue-300">
                  View All Matches
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
