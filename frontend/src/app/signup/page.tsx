import React from 'react';
import Link from 'next/link';

export default function Signup() {
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-4xl font-bold mb-6 text-center">Create Account</h1>
      <div className="bg-gray-800 bg-opacity-50 rounded-lg p-8">
        <form>
          <div className="mb-6">
            <label htmlFor="name" className="block text-sm font-medium mb-2">Full Name</label>
            <input
              type="text"
              id="name"
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="John Doe"
              required
            />
          </div>

          <div className="mb-6">
            <label htmlFor="email" className="block text-sm font-medium mb-2">Email Address</label>
            <input
              type="email"
              id="email"
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="your@email.com"
              required
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              id="password"
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              required
            />
            <p className="mt-1 text-sm text-gray-400">Password must be at least 8 characters long</p>
          </div>

          <div className="mb-6">
            <label htmlFor="confirm-password" className="block text-sm font-medium mb-2">Confirm Password</label>
            <input
              type="password"
              id="confirm-password"
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              required
            />
          </div>

          <div className="mb-6">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="terms"
                className="h-4 w-4 rounded border-gray-600 text-blue-600 focus:ring-blue-500"
                required
              />
              <label htmlFor="terms" className="ml-2 block text-sm text-gray-300">
                I agree to the <Link href="/terms" className="text-blue-400 hover:text-blue-300">Terms of Service</Link> and <Link href="/privacy" className="text-blue-400 hover:text-blue-300">Privacy Policy</Link>
              </label>
            </div>
          </div>

          <div className="mb-6">
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-md transition-colors"
            >
              Create Account
            </button>
          </div>

          <div className="text-center">
            <p className="text-gray-300">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-400 hover:text-blue-300">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
