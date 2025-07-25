import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const DataContext = createContext();

export const DataProvider = ({ children }) => {
    const [availableYears, setAvailableYears] = useState([]);
    const [availableMonths, setAvailableMonths] = useState([]);

    const refreshAvailableDates = async () => {
        try {
            const response = await axios.get('/api/available-dates');
            setAvailableYears(response.data.years);
            setAvailableMonths(response.data.months);
        } catch (error) {
            console.error("Error fetching available dates:", error);
            const currentYear = new Date().getFullYear();
            setAvailableYears(Array.from({ length: 5 }, (_, i) => currentYear - 2 + i));
            setAvailableMonths(Array.from({ length: 12 }, (_, i) => ({ year: currentYear, month: i + 1 })));
        }
    };

    useEffect(() => {
        refreshAvailableDates();
    }, []);

    return (
        <DataContext.Provider value={{
            availableYears,
            availableMonths,
            refreshAvailableDates
        }}>
            {children}
        </DataContext.Provider>
    );
};