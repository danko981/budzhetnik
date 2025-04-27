import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ru } from 'date-fns/locale';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <ThemeProvider>
            <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
                <AuthProvider>
                    <App />
                </AuthProvider>
            </LocalizationProvider>
        </ThemeProvider>
    </React.StrictMode>
); 