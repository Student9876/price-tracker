import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiService from './apiService';

// Thunk to fetch all tracked products
export const fetchProducts = createAsyncThunk(
    'products/fetchProducts',
    async (_, { getState, rejectWithValue }) => {
        try {
            const token = getState().auth.token;
            return await apiService.getTrackedProducts(token);
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

export const fetchSingleProduct = createAsyncThunk(
    'products/fetchSingle',
    async (id, { getState, rejectWithValue }) => {
        try {
            const token = getState().auth.token;
            return await apiService.getSingleProduct(id, token);
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

export const fetchProductHistory = createAsyncThunk(
    'products/fetchHistory',
    async (id, { getState, rejectWithValue }) => {
        try {
            const token = getState().auth.token;
            return await apiService.getProductHistory(id, token);
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);


// Thunk to add a new product
export const addProduct = createAsyncThunk(
    'products/addProduct',
    async (url, { getState, rejectWithValue, dispatch }) => {
        try {
            const token = getState().auth.token;
            await apiService.trackProduct(url, token);
            dispatch(fetchProducts()); // Re-fetch the list to show the new product
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

// Thunk to delete a product
export const deleteProduct = createAsyncThunk(
    'products/deleteProduct',
    async (id, { getState, rejectWithValue }) => {
        try {
            const token = getState().auth.token;
            await apiService.deleteTrackedProduct(id, token);
            return id; // Return the deleted ID on success
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

const productsSlice = createSlice({
    name: 'products',
    initialState: {
        items: [],
        selectedProduct: {
            details: null,
            history: [],
            status: 'idle',
        },
        status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
        error: null,
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchProducts.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(fetchProducts.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.items = action.payload;
            })
            .addCase(fetchProducts.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.payload;
            })
            .addCase(addProduct.pending, (state) => {
                // You could set a specific 'adding' status here if needed
            })
            .addCase(deleteProduct.fulfilled, (state, action) => {
                // Remove the deleted item from the state
                state.items = state.items.filter((item) => item.id !== action.payload);
            })
            .addCase(fetchSingleProduct.pending, (state) => {
                state.selectedProduct.status = 'loading';
            })
            .addCase(fetchSingleProduct.fulfilled, (state, action) => {
                state.selectedProduct.status = 'succeeded';
                state.selectedProduct.details = action.payload;
            })
            .addCase(fetchProductHistory.fulfilled, (state, action) => {
                state.selectedProduct.history = action.payload;
            });
    },
});

export default productsSlice.reducer;