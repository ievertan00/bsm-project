import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const DataContext = createContext();

export const DataProvider = ({ children }) => {
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
    const [availableYears, setAvailableYears] = useState([]);
    const [availableMonths, setAvailableMonths] = useState([]);

    const refreshAvailableDates = async () => {
        try {
            const response = await axios.get('/api/available-dates');
            const fetchedYears = response.data.years;
            const fetchedMonths = response.data.months;

            setAvailableYears(fetchedYears);
            setAvailableMonths(fetchedMonths);

            // Set initial selected year/month to the latest available, or current if none
            if (fetchedYears.length > 0) {
                const latestYear = Math.max(...fetchedYears);
                setSelectedYear(latestYear);
                
                // Filter months for the latest year
                const monthsForLatestYear = fetchedMonths.filter(m => m.year === latestYear).map(m => m.month);
                if (monthsForLatestYear.length > 0) {
                    setSelectedMonth(Math.max(...monthsForLatestYear));
                } else {
                    setSelectedMonth(new Date().getMonth() + 1); // Fallback to current month
                }
            } else {
                setSelectedYear(new Date().getFullYear());
                setSelectedMonth(new Date().getMonth() + 1);
            }

        } catch (error) {
            console.error("Error fetching available dates:", error);
            // Fallback to a default range if fetching fails
            const currentYear = new Date().getFullYear();
            setAvailableYears(Array.from({ length: 5 }, (_, i) => currentYear - 2 + i));
            setAvailableMonths(Array.from({ length: 12 }, (_, i) => ({ year: currentYear, month: i + 1 })));
            setSelectedYear(currentYear);
            setSelectedMonth(new Date().getMonth() + 1);
        }
    };

    useEffect(() => {
        refreshAvailableDates();
    }, []);

    // Effect to update selectedMonth when selectedYear changes
    useEffect(() => {
        const monthsForCurrentSelectedYear = availableMonths
            .filter(m => m.year === selectedYear)
            .map(m => m.month)
            .sort((a, b) => a - b);

        if (monthsForCurrentSelectedYear.length > 0) {
            // If the current selected month is not available for the new year, default to the first available month
            if (!monthsForCurrentSelectedYear.includes(selectedMonth)) {
                setSelectedMonth(monthsForCurrentSelectedYear[0]);
            }
        } else {
            // If no months are available for the selected year, reset month to current or a default
            setSelectedMonth(new Date().getMonth() + 1); // Or null, depending on desired behavior
        }
    }, [selectedYear, availableMonths, selectedMonth]); // Add selectedMonth to dependencies to prevent infinite loop

    return (
        <DataContext.Provider value={{
            selectedYear,
            setSelectedYear,
            selectedMonth,
            setSelectedMonth,
            availableYears,
            availableMonths,
            refreshAvailableDates // Expose the refresh function
        }}>
            {children}
        </DataContext.Provider>
    );
};