import React, { createContext, useState, useContext, useMemo, useEffect } from 'react';
import { createTheme, ThemeProvider as MUIThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Создаем контекст
const ThemeContext = createContext();

// Хук для доступа к контексту
export const useTheme = () => useContext(ThemeContext);

// Дополнительные параметры светлой темы
const lightThemeOptions = {
    palette: {
        mode: 'light',
        primary: {
            main: '#2E7D32',
            light: '#60ad5e',
            dark: '#005005',
        },
        secondary: {
            main: '#1565C0',
            light: '#5e92f3',
            dark: '#003c8f',
        },
        error: {
            main: '#D32F2F',
        },
        warning: {
            main: '#FFA000',
        },
        info: {
            main: '#0288D1',
        },
        success: {
            main: '#388E3C',
        },
        background: {
            default: '#f5f5f5',
            paper: '#ffffff',
        },
        text: {
            primary: 'rgba(0, 0, 0, 0.87)',
            secondary: 'rgba(0, 0, 0, 0.6)',
        },
    },
    typography: {
        fontFamily: 'Roboto, Arial, sans-serif',
        h1: {
            fontSize: '2rem',
            fontWeight: 500,
        },
        h2: {
            fontSize: '1.75rem',
            fontWeight: 500,
        },
        h3: {
            fontSize: '1.5rem',
            fontWeight: 500,
        },
        h4: {
            fontSize: '1.25rem',
            fontWeight: 500,
        },
        h5: {
            fontSize: '1.1rem',
            fontWeight: 500,
        },
        h6: {
            fontSize: '1rem',
            fontWeight: 500,
        },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    borderRadius: 8,
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.08)',
                },
            },
        },
    },
};

// Дополнительные параметры темной темы
const darkThemeOptions = {
    palette: {
        mode: 'dark',
        primary: {
            main: '#4CAF50',
            light: '#80e27e',
            dark: '#087f23',
        },
        secondary: {
            main: '#42A5F5',
            light: '#80d6ff',
            dark: '#0077c2',
        },
        error: {
            main: '#EF5350',
        },
        warning: {
            main: '#FFB74D',
        },
        info: {
            main: '#4FC3F7',
        },
        success: {
            main: '#66BB6A',
        },
        background: {
            default: '#121212',
            paper: '#1E1E1E',
        },
        text: {
            primary: '#ffffff',
            secondary: 'rgba(255, 255, 255, 0.7)',
        },
    },
    typography: {
        fontFamily: 'Roboto, Arial, sans-serif',
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    borderRadius: 8,
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.2), 0 1px 3px rgba(0, 0, 0, 0.3)',
                },
            },
        },
    },
};

export const ThemeProvider = ({ children }) => {
    // Получаем сохраненную тему из localStorage или используем light по умолчанию
    const [mode, setMode] = useState(() => {
        const savedMode = localStorage.getItem('theme');
        return savedMode || 'light';
    });

    // При изменении режима сохраняем в localStorage
    useEffect(() => {
        localStorage.setItem('theme', mode);
    }, [mode]);

    // Переключение темы
    const toggleTheme = () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
    };

    // Создаем объект темы в зависимости от режима
    const theme = useMemo(
        () => createTheme(mode === 'light' ? lightThemeOptions : darkThemeOptions),
        [mode]
    );

    // Значение, которое будет доступно через useTheme
    const value = {
        mode,
        toggleTheme,
        theme,
    };

    return (
        <ThemeContext.Provider value={value}>
            <MUIThemeProvider theme={theme}>
                <CssBaseline />
                {children}
            </MUIThemeProvider>
        </ThemeContext.Provider>
    );
}; 