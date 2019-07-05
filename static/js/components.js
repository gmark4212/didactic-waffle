Vue.component('data-error', {
    template: `<p class="title is-3">
                <slot></slot>
            </p>'`
});

Vue.component('pie-chart', {
    extends: VueChartJs.Pie,
    props: ['skills', 'frequency'],
    mounted() {
        this.renderPieChart();
    },
    methods: {
        renderPieChart() {
            this.renderChart({
                labels: this.skills,
                datasets: [
                    {
                        backgroundColor: [
                            '#1abc9c',
                            '#2ecc71',
                            '#3498db',
                            '#9b59b6',
                            '#34495e',
                            '#f1c40f',
                            '#e67e22',
                            '#e74c3c',
                            '#ecf0f1',
                            '#95a5a6',
                            '#16a085',
                            '#27ae60',
                            '#2980b9',
                            '#8e44ad',
                            '#2c3e50',
                            '#f39c12',
                            '#d35400',
                            '#c0392b',
                            '#bdc3c7',
                            '#7f8c8d'
                        ],
                        data: this.frequency
                    }
                ]
            }, {
                responsive: true,
                maintainAspectRatio: false,
                pieceLabel: {
                    mode: 'percentage',
                    precision: 1
                }
            })
        }
    }
});

Vue.component('ads-card', {
    props: ['title', 'desc'],
    template: '    <div class="notification is-light">\n' +
        '            <p><h1 class="title is-6">{{ title }}</h1></p>\n' +
        '            <p>{{ desc }}</p>\n' +
        '            <br><p><a href=# class="button is-success">Explore</a></p>\n' +
        '        </div>'


});

