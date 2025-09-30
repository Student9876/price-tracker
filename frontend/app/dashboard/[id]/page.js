'use client';

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { fetchSingleProduct, fetchProductHistory } from '@/lib/productsSlice';
import { Loader } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ProductDetailPage() {
    const dispatch = useDispatch();
    const router = useRouter();
    const params = useParams(); // Gets parameters from the URL, e.g., { id: '1' }
    const { id } = params;

    const { token } = useSelector((state) => state.auth);
    const { details, history, status } = useSelector((state) => state.products.selectedProduct);

    useEffect(() => {
        if (!token) {
            router.push('/login');
        } else if (id) {
            dispatch(fetchSingleProduct(id));
            dispatch(fetchProductHistory(id));
        }
    }, [id, token, dispatch, router]);

    const formattedHistory = history.map(p => ({
        date: new Date(p.timestamp).toLocaleDateString('en-IN'),
        price: p.price,
    }));

    if (status === 'loading' || !details) {
        return <div className="min-h-screen flex items-center justify-center"><Loader className="animate-spin" size={48} /></div>;
    }

    return (
        <div className="bg-slate-50 min-h-screen">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <Link href="/dashboard" className="text-indigo-600 font-semibold mb-6 inline-block">&larr; Back to Dashboard</Link>
                <div className="bg-white p-6 rounded-xl shadow-lg grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <img src={details.product.image_urls[0]} alt={details.product.name} className="w-full h-80 object-contain rounded-lg" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">{details.product.name}</h1>
                        <p className="text-md text-slate-500 mt-1">{details.product.brand}</p>
                        <div className="mt-4 bg-indigo-50 p-4 rounded-lg">
                            <p className="text-3xl font-extrabold text-slate-900">{details.currency}{details.current_price}</p>
                            {details.mrp && <p className="text-sm text-slate-500 line-through">M.R.P: {details.currency}{details.mrp}</p>}
                        </div>
                        <a href={details.url} target="_blank" rel="noopener noreferrer" className="block w-full text-center mt-6 bg-orange-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-orange-600 transition">
                            View on Store
                        </a>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-lg mt-8">
                    <h2 className="text-xl font-semibold mb-4 text-slate-700">Price History</h2>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <LineChart data={formattedHistory}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" fontSize={12} />
                                <YAxis fontSize={12} />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="price" name="Price (INR)" stroke="#4f46e5" activeDot={{ r: 8 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}