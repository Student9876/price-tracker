'use client';

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { fetchSingleProduct, fetchProductHistory, deleteProduct } from '@/lib/productsSlice'; // Added deleteProduct
import { Loader, Trash2 } from 'lucide-react'; // Added Trash2
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ProductDetailPage() {
    const dispatch = useDispatch();
    const router = useRouter();
    const params = useParams();
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

    const handleDelete = () => {
        if (window.confirm('Are you sure you want to stop tracking this product?')) {
            dispatch(deleteProduct(id)).then(() => {
                router.push('/dashboard');
            });
        }
    };

    const formattedHistory = history.map(p => ({
        // Format date nicely (e.g., "Oct 29")
        date: new Date(p.timestamp).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
        price: p.price,
    }));

    if (status === 'loading' || !details) {
        return <div className="min-h-screen flex items-center justify-center"><Loader className="animate-spin text-indigo-600" size={48} /></div>;
    }

    return (
        <div className="bg-slate-100 min-h-screen">
            {/* Simple Header for Detail Page */}
            <header className="bg-white shadow-sm sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <Link href="/dashboard">
                        <h1 className="text-xl font-bold text-slate-800 cursor-pointer">
                            Price<span className="text-indigo-600">Track</span>
                        </h1>
                    </Link>
                    {/* Optional: Add user info/logout here too if needed */}
                </div>
            </header>

            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <Link href="/dashboard" className="text-indigo-600 font-semibold mb-6 inline-block hover:underline">&larr; Back to Dashboard</Link>

                {/* --- Product Summary Section --- */}
                <section className="bg-white p-6 rounded-xl shadow-lg grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                    <div className="md:col-span-1 flex justify-center items-center">
                        {details.product.image_urls && details.product.image_urls.length > 0 ? (
                            <img src={details.product.image_urls[0]} alt={details.product.name} className="max-h-64 object-contain rounded-lg" />
                        ) : (
                            <div className="h-64 bg-slate-200 flex items-center justify-center text-slate-500 rounded-lg">No Image</div>
                        )}
                    </div>
                    <div className="md:col-span-2">
                        <h1 className="text-2xl font-bold text-slate-800 leading-tight">{details.product.name}</h1>
                        <p className="text-md text-slate-500 mt-1 mb-4">{details.product.brand}</p>
                        <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-100">
                            <p className="text-xs text-slate-600 mb-1">Current Price:</p>
                            <p className="text-3xl font-extrabold text-slate-900">{details.currency}{details.current_price}</p>
                            {details.mrp && <p className="text-sm text-slate-500 line-through">M.R.P: {details.currency}{details.mrp}</p>}
                        </div>
                        <div className="flex flex-col sm:flex-row gap-3 mt-6">
                            <a href={details.url} target="_blank" rel="noopener noreferrer" className="flex-1 text-center bg-orange-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-orange-600 transition">
                                View on Store
                            </a>
                            <button
                                onClick={handleDelete}
                                className="flex-1 text-center bg-red-100 text-red-700 font-bold py-3 px-4 rounded-lg hover:bg-red-200 transition flex items-center justify-center gap-2"
                            >
                                <Trash2 size={16} /> Stop Tracking
                            </button>
                        </div>
                    </div>
                </section>

                {/* --- Price History Chart --- */}
                <section className="bg-white p-6 rounded-xl shadow-lg mb-8">
                    <h2 className="text-xl font-semibold mb-4 text-slate-700">Price History</h2>
                    {formattedHistory.length > 1 ? (
                        <div style={{ width: '100%', height: 300 }}>
                            <ResponsiveContainer>
                                <LineChart data={formattedHistory} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                    <XAxis dataKey="date" fontSize={12} tick={{ fill: '#64748b' }} />
                                    <YAxis fontSize={12} tick={{ fill: '#64748b' }} />
                                    <Tooltip contentStyle={{ backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '0.5rem' }} />
                                    <Legend wrapperStyle={{ fontSize: "14px" }} />
                                    <Line type="monotone" dataKey="price" name={`Price (${details.currency})`} stroke="#4f46e5" strokeWidth={2} activeDot={{ r: 6 }} dot={{ r: 3 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <p className="text-slate-500 text-center py-10">Not enough price history yet to display a chart.</p>
                    )}
                </section>

                {/* --- Key Features Section --- */}
                {details.product.key_features && details.product.key_features.length > 0 && (
                    <section className="bg-white p-6 rounded-xl shadow-lg mb-8">
                        <h2 className="text-xl font-semibold mb-4 text-slate-700">Key Features</h2>
                        <ul className="list-disc list-inside space-y-2 text-slate-600 text-sm">
                            {details.product.key_features.map((feature, index) => (
                                <li key={index}>{feature}</li>
                            ))}
                        </ul>
                    </section>
                )}

                {/* --- Specifications Section --- */}
                {details.product.specifications && Object.keys(details.product.specifications).length > 0 && (
                    <section className="bg-white p-6 rounded-xl shadow-lg">
                        <h2 className="text-xl font-semibold mb-4 text-slate-700">Specifications</h2>
                        <div className="overflow-x-auto">
                            <table className="min-w-full text-sm">
                                <tbody>
                                    {Object.entries(details.product.specifications).map(([key, value]) => (
                                        <tr key={key} className="border-b border-slate-200">
                                            <th className="py-2 px-4 bg-slate-50 text-left font-semibold text-slate-600 w-1/3">{key}</th>
                                            <td className="py-2 px-4 text-slate-700">{value}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </section>
                )}

            </main>
        </div>
    );
}