const config = {
    API_URL: import.meta.env.VITE_API_URL || (
        import.meta.env.PROD
            ? '/api'  // Relative URL in production (behind nginx reverse proxy)
            : 'http://localhost:5001/api'
    ),
};

export default config;
