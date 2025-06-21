import React from 'react';
import Link from 'next/link';

export default function Dashboard() {
  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">Dashboard</h1>
        <div className="flex space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors">
            Register New Agent
          </button>
          <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-md transition-colors">
            Create Tournament
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-2">My Agents</h2>
          <p className="text-3xl font-bold mb-4">3</p>
          <div className="flex justify-between">
            <span className="text-sm text-gray-300">2 active, 1 quarantined</span>
            <Link href="/agents" className="text-blue-400 hover:text-blue-300 text-sm">
              View All
            </Link>
          </div>
        </div>
        
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-2">Active Tournaments</h2>
          <p className="text-3xl font-bold mb-4">2</p>
          <div className="flex justify-between">
            <span className="text-sm text-gray-300">1 in progress, 1 scheduled</span>
            <Link href="/tournaments" className="text-blue-400 hover:text-blue-300 text-sm">
              View All
            </Link>
          </div>
        </div>
        
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-2">Recent Matches</h2>
          <p className="text-3xl font-bold mb-4">24</p>
          <div className="flex justify-between">
            <span className="text-sm text-gray-300">Last 7 days</span>
            <Link href="/matches" className="text-blue-400 hover:text-blue-300 text-sm">
              View All
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">My Agents</h2>
            <Link href="/agents" className="text-blue-400 hover:text-blue-300 text-sm">
              View All
            </Link>
          </div>
          
          <div className="space-y-4">
            <div className="bg-gray-700 p-4 rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium">TitForTatBot</h3>
                  <p className="text-sm text-gray-300">Cooperates first, then mirrors opponent's last move</p>
                </div>
                <span className="bg-green-600 text-xs px-2 py-1 rounded-full">Active</span>
              </div>
              <div className="mt-2 flex justify-between text-sm">
                <span>Avg. Score: <span className="text-green-400">3.14</span></span>
                <span>Matches: 128</span>
                <Link href="/agents/1" className="text-blue-400 hover:text-blue-300">
                  Details
                </Link>
              </div>
            </div>
            
            <div className="bg-gray-700 p-4 rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium">GrimTriggerBot</h3>
                  <p className="text-sm text-gray-300">Cooperates until opponent defects, then always defects</p>
                </div>
                <span className="bg-green-600 text-xs px-2 py-1 rounded-full">Active</span>
              </div>
              <div className="mt-2 flex justify-between text-sm">
                <span>Avg. Score: <span className="text-green-400">2.89</span></span>
                <span>Matches: 128</span>
                <Link href="/agents/2" className="text-blue-400 hover:text-blue-300">
                  Details
                </Link>
              </div>
            </div>
            
            <div className="bg-gray-700 p-4 rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium">ExperimentalBot</h3>
                  <p className="text-sm text-gray-300">Testing a new adaptive strategy</p>
                </div>
                <span className="bg-yellow-600 text-xs px-2 py-1 rounded-full">Quarantined</span>
              </div>
              <div className="mt-2 flex justify-between text-sm">
                <span>Avg. Score: <span className="text-yellow-400">2.45</span></span>
                <span>Matches: 12</span>
                <Link href="/agents/3" className="text-blue-400 hover:text-blue-300">
                  Details
                </Link>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Recent Matches</h2>
            <Link href="/matches" className="text-blue-400 hover:text-blue-300 text-sm">
              View All
            </Link>
          </div>
          
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
                  View
                </Link>
              </div>
              <div className="mt-2 flex justify-between text-xs text-gray-400">
                <span>Weekly Championship Tournament</span>
                <span>Completed 2 hours ago</span>
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
                  View
                </Link>
              </div>
              <div className="mt-2 flex justify-between text-xs text-gray-400">
                <span>Weekly Championship Tournament</span>
                <span>Completed 3 hours ago</span>
              </div>
            </div>
            
            <div className="bg-gray-700 p-4 rounded-lg">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <span className="font-medium">ExperimentalBot</span>
                  <span className="mx-2 text-yellow-400">2.45</span>
                  <span className="text-gray-400">vs</span>
                  <span className="mx-2 text-green-400">2.75</span>
                  <span className="font-medium">ForgivingBot</span>
                </div>
                <Link href="/matches/125" className="text-blue-400 hover:text-blue-300 text-sm">
                  View
                </Link>
              </div>
              <div className="mt-2 flex justify-between text-xs text-gray-400">
                <span>Quarantine Testing</span>
                <span>Completed 5 hours ago</span>
              </div>
            </div>
            
            <div className="bg-gray-700 p-4 rounded-lg">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <span className="font-medium">TitForTatBot</span>
                  <span className="mx-2 text-green-400">2.95</span>
                  <span className="text-gray-400">vs</span>
                  <span className="mx-2 text-green-400">2.85</span>
                  <span className="font-medium">PavlovBot</span>
                </div>
                <Link href="/matches/126" className="text-blue-400 hover:text-blue-300 text-sm">
                  View
                </Link>
              </div>
              <div className="mt-2 flex justify-between text-xs text-gray-400">
                <span>Weekly Championship Tournament</span>
                <span>Completed 6 hours ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
