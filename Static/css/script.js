document.addEventListener('DOMContentLoaded', () => {
    fetchData();

    setInterval(fetchData, 10000); // Fetch data every 10 seconds

    async function fetchData() {
        try {
            const response = await fetch('/network_data');
            const data = await response.json();
            renderCharts(data);
            renderTables(data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    function renderCharts(data) {
        const ctxApps = document.getElementById('applicationsChart').getContext('2d');
        const ctxRecs = document.getElementById('receiversChart').getContext('2d');

        if (window.applicationsChart instanceof Chart) {
            window.applicationsChart.destroy();
        }

        if (window.receiversChart instanceof Chart) {
            window.receiversChart.destroy();
        }

        window.applicationsChart = new Chart(ctxApps, {
            type: 'line',
            data: {
                labels: data.top_applications.map(app => app.name),
                datasets: [{
                    label: 'Bytes',
                    data: data.top_applications.map(app => app.bytes),
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        window.receiversChart = new Chart(ctxRecs, {
            type: 'pie',
            data: {
                labels: data.top_receivers.map(rec => rec.hostname),
                datasets: [{
                    data: data.top_receivers.map(rec => rec.bytes),
                    backgroundColor: data.top_receivers.map((_, i) => `hsl(${i * 30}, 70%, 50%)`)
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    function renderTables(data) {
        const appsTable = document.querySelector('#applicationsTable tbody');
        const recsTable = document.querySelector('#receiversTable tbody');

        appsTable.innerHTML = '';
        recsTable.innerHTML = '';

        data.top_applications.forEach(app => {
            const row = `<tr>
                <td>${app.name}</td>
                <td>${app.bytes.toFixed(2)}</td>
                <td>${app.packets}</td>
                <td>${app.percent.toFixed(2)}%</td>
            </tr>`;
            appsTable.innerHTML += row;
        });

        data.top_receivers.forEach(rec => {
            const row = `<tr>
                <td>${rec.hostname}</td>
                <td>${rec.bytes.toFixed(2)}</td>
                <td>${rec.packets}</td>
                <td>${rec.percent.toFixed(2)}%</td>
            </tr>`;
            recsTable.innerHTML += row;
        });
    }
});
