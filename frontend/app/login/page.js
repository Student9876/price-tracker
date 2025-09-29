'use client';
import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import { loginUser } from '@/lib/authSlice';
import { Loader, AlertCircle } from 'lucide-react';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const dispatch = useDispatch();
    const router = useRouter();

    // useSelector reads data from the Redux store
    const { status, error, token } = useSelector((state) => state.auth);

    const handleSubmit = (e) => {
        e.preventDefault();
        // useDispatch sends an action to the Redux store
        dispatch(loginUser({ email, password }));
    };

    // This effect runs when the login is successful
    useEffect(() => {
        if (status === 'succeeded' && token) {
            router.push('/dashboard'); // Redirect to dashboard on success
        }
    }, [status, token, router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50">
            <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-lg">
                <h2 className="text-3xl font-bold text-center text-slate-800 mb-2">Sign In</h2>
                <p className="text-center text-slate-500 mb-8">Access your product tracking dashboard.</p>
                {status === 'failed' && error && (
                    <div className="bg-red-100 text-red-700 p-3 rounded-md mb-4 text-sm flex items-center">
                        <AlertCircle className="w-5 h-5 mr-2" />
                        {error}
                    </div>
                )}
                <form onSubmit={handleSubmit}>
                    {/* Form inputs are the same as the previous example */}
                    <div className="mb-4">
                        <label className="block text-slate-600 text-sm font-semibold mb-2" htmlFor="email">Email</label>
                        <input
                            type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
                            required
                        />
                    </div>
                    <div className="mb-6">
                        <label className="block text-slate-600 text-sm font-semibold mb-2" htmlFor="password">Password</label>
                        <input
                            type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
                            required
                        />
                    </div>
                    <button type="submit" disabled={status === 'loading'} className="w-full bg-indigo-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-indigo-400 flex justify-center">
                        {status === 'loading' ? <Loader className="animate-spin" /> : 'Login'}
                    </button>
                </form>
            </div>
        </div>
    );
}