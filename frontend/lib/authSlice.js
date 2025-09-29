// lib/authSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import apiService from './apiService';

// CORRECTED: loginUser now saves the token and fetches user data
export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const tokenData = await apiService.login(email, password);
      // --- CRUCIAL STEP 1: Save the token to persistent storage ---
      localStorage.setItem('token', tokenData.access_token);

      // --- CRUCIAL STEP 2: Use the new token to get user details ---
      const user = await apiService.getCurrentUser(tokenData.access_token);

      return { user, token: tokenData.access_token };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// This thunk checks for an existing session on app load
export const checkAuth = createAsyncThunk(
  'auth/checkAuth',
  async (_, { rejectWithValue }) => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const user = await apiService.getCurrentUser(token);
        return { user, token }; // Success: return user and token
      } catch (error) {
        localStorage.removeItem('token'); // Token is invalid, remove it
        return rejectWithValue(error.message);
      }
    }
    return rejectWithValue('No token found');
  }
);


const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: null,
    status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
    error: null,
  },
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.status = 'idle';
      localStorage.removeItem('token');
    },
  },
  // CORRECTED: extraReducers now handles all states for BOTH thunks
  extraReducers: (builder) => {
    builder
      // Cases for loginUser
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
        state.user = null;
        state.token = null;
      })
      // Cases for checkAuth (This was missing)
      .addCase(checkAuth.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(checkAuth.rejected, (state) => {
        state.status = 'idle';
        state.user = null;
        state.token = null;
      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;