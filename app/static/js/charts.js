document.addEventListener('DOMContentLoaded', function () {
    const data = window.chartData;
    if (!data) return;

    // 1. Attendance Trend Chart
    const ctxAttendance = document.getElementById('attendanceTrendChart').getContext('2d');
    new Chart(ctxAttendance, {
        type: 'line',
        data: {
            labels: data.attendanceDates,
            datasets: [
                {
                    label: 'Eating (Expected Attendance)',
                    data: data.eatingCounts,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Skipping (Excused)',
                    data: data.skippingCounts,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });

    // 2. Meal Breakdown Chart (Historical Choices)
    const ctxBreakdown = document.getElementById('mealBreakdownChart').getContext('2d');
    new Chart(ctxBreakdown, {
        type: 'bar',
        data: {
            labels: ['Breakfast', 'Lunch', 'Dinner'],
            datasets: [
                {
                    label: 'Eating',
                    data: [
                        data.mealAgg.breakfast.eating,
                        data.mealAgg.lunch.eating,
                        data.mealAgg.dinner.eating
                    ],
                    backgroundColor: '#4f46e5'
                },
                {
                    label: 'Skipping',
                    data: [
                        data.mealAgg.breakfast.skipping,
                        data.mealAgg.lunch.skipping,
                        data.mealAgg.dinner.skipping
                    ],
                    backgroundColor: '#e2e8f0'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });

    // 3. Food Wastage Trend Chart
    const ctxWaste = document.getElementById('wasteTrendChart').getContext('2d');
    new Chart(ctxWaste, {
        type: 'bar',
        data: {
            labels: data.wasteDates,
            datasets: [
                {
                    label: 'Food Prepared (kg)',
                    data: data.preparedTrends,
                    backgroundColor: 'rgba(13, 148, 136, 0.6)',
                    borderColor: '#0d9488',
                    borderWidth: 1
                },
                {
                    label: 'Food Wasted (kg)',
                    data: data.wastedTrends,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: '#ef4444',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Weight in Kilograms (kg)'
                    }
                }
            }
        }
    });
});
