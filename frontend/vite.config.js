import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            }
        }
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: false,
        // Добавляем настройку для статических ресурсов
        assetsDir: 'assets',
        // Настройка для обработки ошибок сборки
        chunkSizeWarningLimit: 1600,
        // Оптимизация для Netlify
        rollupOptions: {
            output: {
                manualChunks: {
                    vendor: ['react', 'react-dom', 'react-router-dom'],
                    mui: ['@mui/material', '@mui/icons-material'],
                    charts: ['chart.js', 'react-chartjs-2', 'recharts']
                }
            }
        }
    }
}); 