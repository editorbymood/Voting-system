// Chart.js configuration settings
const chartColors = {
    primary: 'rgba(78, 115, 223, 0.8)',
    success: 'rgba(40, 167, 69, 0.8)',
    info: 'rgba(23, 162, 184, 0.8)',
    warning: 'rgba(255, 193, 7, 0.8)',
    danger: 'rgba(220, 53, 69, 0.8)',
    secondary: 'rgba(108, 117, 125, 0.8)',
};

const chartDefaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
        },
        tooltip: {
            mode: 'index',
            intersect: false,
        }
    },
    scales: {
        y: {
            beginAtZero: true,
        }
    }
};

// Pie chart default configuration
function createPieChart(ctx, data) {
    return new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: ${value} votes (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Bar chart default configuration
function createBarChart(ctx, data) {
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Vote Count'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw} votes`;
                        }
                    }
                }
            }
        }
    });
}
