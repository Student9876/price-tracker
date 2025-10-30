const API_URL = process.env.NEXT_PUBLIC_API_URL;

// A helper function to handle API responses
async function handleResponse(response) {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "An unknown error occurred" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return response.json();
}

const apiService = {
    /**
     * Logs in a user.
     * @param {string} email - The user's email.
     * @param {string} password - The user's password.
     * @returns {Promise<object>} The token data.
     */
    login: async (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        console.log(email, password);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params,
        });
        return handleResponse(response);
    },

    /**
     * Registers a new user.
     * @param {string} email - The new user's email.
     * @param {string} password - The new user's password.
     * @returns {Promise<object>} The new user data.
     */
    register: async (email, password) => {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        return handleResponse(response);
    },

    /**
     * Fetches the current user's data using a token.
     * @param {string} token - The user's JWT.
     * @returns {Promise<object>} The current user's data.
     */
    getCurrentUser: async (token) => {
        const response = await fetch(`${API_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        return handleResponse(response);
    },

    /**
     * Fetches all products tracked by the current user.
     * @param {string} token - The user's JWT.
     * @returns {Promise<Array>} A list of tracked products.
     */
    getTrackedProducts: async (token) => {
        const response = await fetch(`${API_URL}/track`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        return handleResponse(response);
    },

    /**
  * Fetches all products tracked by the current user.
  * @param {string} token - The user's JWT.
  * @returns {Promise<Array>} A list of tracked products.
  */
    getTrackedProducts: async (token) => {
        const response = await fetch(`${API_URL}/track`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        return handleResponse(response);
    },

    /**
     * Adds a new product URL for the user to track.
     * @param {string} url - The product URL.
     * @param {string} token - The user's JWT.
     * @returns {Promise<object>} The newly scraped product details.
     */
    trackProduct: async (url, token) => {
        const response = await fetch(`${API_URL}/track`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ urls: [url] }),
        });
        return handleResponse(response);
    },

    /**
     * Deletes a tracked product for the current user.
     * @param {number} id - The ID of the tracked product.
     * @param {string} token - The user's JWT.
     * @returns {Promise<object>} The success message.
     */
    deleteTrackedProduct: async (id, token) => {
        const response = await fetch(`${API_URL}/track/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        return handleResponse(response);
    },

    getSingleProduct: async (id, token) => {
        const response = await fetch(`${API_URL}/track/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        return handleResponse(response);
    },

    getProductHistory: async (id, token) => {
        const response = await fetch(`${API_URL}/track/${id}/history`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        return handleResponse(response);
    },
};

export default apiService;