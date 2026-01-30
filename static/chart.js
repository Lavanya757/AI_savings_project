var spendingChartInstance = null;
var monthlyBarChartInstance = null;

document.addEventListener('DOMContentLoaded', function () {
    console.log('chart.js script loaded and running');

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

    // Bar Chart for Total Income and Total Savings with double JSON parse fix
    const barCtx = document.getElementById('monthlyBarChart');
    if (barCtx) {
        const incomeDataElement = document.getElementById('income-data');
        const savingsDataElement = document.getElementById('savings-data');

        if (incomeDataElement && savingsDataElement) {
            let incomeData = {};
            let savingsData = {};
            try {
                // Double parse to handle double-encoded JSON string
                incomeData = JSON.parse(JSON.parse(incomeDataElement.textContent));
                savingsData = JSON.parse(JSON.parse(savingsDataElement.textContent));
                console.log('Parsed incomeData:', incomeData);
                console.log('Parsed savingsData:', savingsData);
            } catch (e) {
                console.error('Error parsing monthly financial data:', e);
            }

            // Calculate total income and total savings
            const totalIncome = Object.values(incomeData).reduce((acc, val) => acc + Number(val), 0);
            const totalSavings = Object.values(savingsData).reduce((acc, val) => acc + Number(val), 0);

            console.log('Total Income:', totalIncome);
            console.log('Total Savings:', totalSavings);

            const labels = ['Total Income', 'Total Savings'];
            const dataValues = [totalIncome, totalSavings];

            if (monthlyBarChartInstance) {
                monthlyBarChartInstance.destroy();
            }

            monthlyBarChartInstance = new Chart(barCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Amount (₹)',
                        data: dataValues,
                        backgroundColor: ['#4BC0C0', '#FFCE56']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Category'
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
                            display: false
                        },
                        tooltip: {
                            enabled: true,
                            callbacks: {
                                label: function(context) {
                                    if (context.parsed && context.parsed.y != null) {
                                        return '₹' + context.parsed.y.toLocaleString();
                                    } else {
                                        return 'N/A';
                                    }
                                }
                            }
                        }
                    }
                }
            });
            console.log('Monthly bar chart created successfully with total income and savings', monthlyBarChartInstance);
        }
    }
});
