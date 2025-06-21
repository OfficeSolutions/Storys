import React from 'react';
import Link from 'next/link';

export default function Login() {
  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-4xl font-bold mb-6 text-center">Login</h1>
      <div className="bg-gray-800 bg-opacity-50 rounded-lg p-8">
        <form>
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
            <div className="flex justify-end mt-1">
              <Link href="/forgot-password" className="text-sm text-blue-400 hover:text-blue-300">
                Forgot password?
              </Link>
            </div>
          </div>

          <div className="mb-6">
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-md transition-colors"
            >
              Sign In
            </button>
          </div>

          <div className="text-center">
            <p className="text-gray-300">
              Don't have an account?{' '}
              <Link href="/signup" className="text-blue-400 hover:text-blue-300">
                Sign up
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
