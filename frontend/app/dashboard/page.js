'use client';
import { useSelector, useDispatch } from 'react-redux';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { fetchProducts, addProduct, deleteProduct } from '@/lib/productsSlice';
import { logout } from '@/lib/authSlice';
import { Search, Loader, AlertCircle, Trash2, LogOut } from 'lucide-react';

// A reusable card component for displaying a product
const ProductCard = ({ product, onDelete }) => (
    <Link href={`/dashboard/${product.id}`} className="block group">
        <div className="bg-white rounded-lg shadow-md overflow-hidden group-hover:shadow-xl transition-shadow duration-300 flex flex-col h-full">
            {/* This is the part that was missing */}
            <div className="p-4 flex-grow">
                {/* Check if image URLs exist before trying to display one */}
                {product.product.image_urls && product.product.image_urls.length > 0 ? (
                    <img
                        src={product.product.image_urls[0]}
                        alt={product.product.name}
                        className="w-full h-40 object-contain mb-4"
                    />
                ) : (
                    <div className="w-full h-40 bg-slate-200 flex items-center justify-center text-slate-500">No Image</div>
                )}
                <h3 className="text-sm font-semibold text-slate-800 h-10 overflow-hidden" title={product.product.name}>
                    {product.product.name}
                </h3>
                <p className="text-xs text-slate-500 mt-1">{product.product.brand}</p>
            </div>

            {/* This bottom part with price and delete button is the same as before */}
            <div className="p-4 bg-slate-50 border-t border-slate-200">
                <p className="text-lg font-bold text-slate-900">{product.currency}{product.current_price}</p>
                {product.mrp && <p className="text-xs text-slate-500 line-through">M.R.P: {product.currency}{product.mrp}</p>}
                <div className="mt-4">
                    <button
                        onClick={(e) => { e.preventDefault(); onDelete(product.id); }}
                        className="w-full bg-red-100 text-red-700 text-xs font-bold py-2 px-3 rounded-md hover:bg-red-200 transition-colors flex items-center justify-center gap-1"
                    >
                        <Trash2 size={14} /> Stop Tracking
                    </button>
                </div>
            </div>
        </div>
    </Link>
);


export default function DashboardPage() {
    const [url, setUrl] = useState('');
    const dispatch = useDispatch();
    const router = useRouter();

    const { token, user } = useSelector((state) => state.auth);
    const { items: products, status, error } = useSelector((state) => state.products);

    // Effect to protect the route and fetch initial data
    useEffect(() => {
        if (!token) {
            router.push('/login');
        } else {
            dispatch(fetchProducts());
        }
    }, [token, router, dispatch]);

    const handleAddProduct = (e) => {
        e.preventDefault();
        if (url) {
            dispatch(addProduct(url));
            setUrl('');
        }
    };

    const handleDeleteProduct = (id) => {
        if (window.confirm('Are you sure you want to stop tracking this product?')) {
            dispatch(deleteProduct(id));
        }
    };

    const handleLogout = () => {
        dispatch(logout());
        router.push('/login');
    }

    // Prevents flashing content before redirect
    if (!token) {
        return <div className="min-h-screen flex items-center justify-center"><Loader className="animate-spin" /></div>;
    }

    return (
        <div className="min-h-screen bg-slate-100">
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <Link href="/dashboard">
                        <h1 className="text-2xl font-bold text-slate-800 cursor-pointer">
                            Price<span className="text-indigo-600">Track</span>
                        </h1>
                    </Link>
                    {user && (
                        <div className="flex items-center gap-4">
                            <span className="text-sm text-slate-600 hidden sm:block">Welcome, {user.email}</span>
                            <button onClick={handleLogout} title="Logout" className="p-2 rounded-full text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors">
                                <LogOut size={20} />
                            </button>
                        </div>
                    )}
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="bg-white p-6 rounded-xl shadow-sm mb-8">
                    <form onSubmit={handleAddProduct} className="flex flex-col sm:flex-row gap-4">
                        <div className="relative flex-grow">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                            <input
                                type="url" value={url} onChange={(e) => setUrl(e.target.value)}
                                placeholder="Paste product URL to start tracking..."
                                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg"
                            />
                        </div>
                        <button type="submit" className="bg-indigo-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-indigo-700">
                            Track Product
                        </button>
                    </form>
                </div>

                {status === 'loading' && <div className="text-center py-10"><Loader className="animate-spin inline-block text-indigo-600" /></div>}
                {status === 'failed' && <div className="text-center text-red-600"><AlertCircle className="inline mr-2" /> {error}</div>}

                {status === 'succeeded' && (
                    products.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                            {products.map(product => (
                                <ProductCard key={product.id} product={product} onDelete={handleDeleteProduct} />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-20 bg-white rounded-lg shadow-sm">
                            <h3 className="text-xl font-semibold text-slate-700">Your tracking list is empty</h3>
                            <p className="text-slate-500 mt-2">Paste a product URL above to get started!</p>
                        </div>
                    )
                )}
            </main>
        </div>
    );
}