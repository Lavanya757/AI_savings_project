var spendingChartInstance = null;
var monthlyBarChartInstance = null;

document.addEventListener('DOMContentLoaded', function ()) {
    console.log('chart_v2.js script loaded and running');

    // Pie Chart for Spending Patterns
    const spendingCtx = document.getElementById('spendingChart');
    if (spendingCtx) {
        const expenseCategoryDataElement = document.getElementById('expense-category-data');
        if (expenseCategoryDataElement) {
            let expenseCategoryData = {};
            try {
                expenseCategoryData = JSON.parse(expenseCategoryDataElement.textContent);
                console.log('Parsed expenseCategoryData:', expenseCategoryData);
            } catch (e) {
                console.error('Error parsing expense category data:', e);
            }

            const dataValues = Object.values(expenseCategoryData).map(value => Number(value));
            const dataLabels = Object.keys(expenseCategoryData);

            if (dataValues.length > 0) {
                if (spendingChartInstance) {
                    spendingChartInstance.destroy();
                }
                spendingChartInstance = new Chart(spendingCtx.getContext('2d'), {
                    type: 'pie',
                    data: {
                        labels: dataLabels,
                        datasets: [{
                            data: dataValues,
                            backgroundColor: [
                                '#FF6384',
                                '#36A2EB',
                                '#FFCE56',
                                '#4BC0C0',
                                '#9966FF',
                                '#FF9F40',
                                '#4BC0C0',
                                '#C9CBCF'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
                console.log('Pie chart created successfully', spendingChartInstance);
            }
        }
    }

    // Bar Chart for Recent Month Income and Cumulative Savings
    const barCtx = document.getElementById('monthlyBarChart');
    if (barCtx) {
        const incomeDataElement = document.getElementById('income-data');
        const savingsDataElement = document.getElementById('savings-data');

        if (incomeDataElement && savingsDataElement) {
            let incomeData = {};
            let savingsData = {};
            try {
                incomeData = JSON.parse(incomeDataElement.textContent);
                savingsData = JSON.parse(savingsDataElement.textContent);
                console.log('Parsed incomeData:', incomeData);
                console.log('Parsed savingsData:', savingsData);
            } catch (e) {
                console.error('Error parsing monthly financial data:', e);
            }

            // Get sorted months from income data keys
            const incomeMonths = Object.keys(incomeData).sort();
            const recentMonth = incomeMonths.length > 0 ? incomeMonths[incomeMonths.length - 1] : 'No Data';

            // Income value for recent month
            const recentIncome = incomeData[recentMonth] || 0;

            // Calculate cumulative savings up to recent month
            const sortedSavingsMonths = Object.keys(savingsData).sort();
            let cumulativeSavings = 0;
            for (const month of sortedSavingsMonths) {
                cumulativeSavings += Number(savingsData[month]);
                if (month === recentMonth) {
                    break;
                }
            }

            console.log('Recent Month:', recentMonth);
            console.log('Recent Income:', recentIncome);
            console.log('Cumulative Savings:', cumulativeSavings);

            if (monthlyBarChartInstance) {
                monthlyBarChartInstance.destroy();
            }

            monthlyBarChartInstance = new Chart(barCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: [recentMonth],
                    datasets: [
                        {
                            label: 'Income',
                            data: [recentIncome],
                            backgroundColor: '#4BC0C0'
                        },
                        {
                            label: 'Cumulative Savings',
                            data: [cumulativeSavings],
                            backgroundColor: '#FFCE56'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Recent Month'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Amount (₹)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            enabled: true,
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    if (context.parsed && context.parsed.y != null) {
                                        return context.dataset.label + ': ₹' + context.parsed.y.toLocaleString();
                                    } else {
                                        return context.dataset.label + ': N/A';
                                    }
                                }
                            }
                        }
                    }
                }
            });
            console.log('Monthly bar chart created successfully', monthlyBarChartInstance);
        }
    }
