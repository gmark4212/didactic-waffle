Vue.component('data-error', {
    template: `<p class="title is-3">
                <slot></slot>
            </p>'`
});

Vue.component('line-chart', {
    extends: VueChartJs.Line,
    mounted() {
        this.renderChart({
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            datasets: [
                {
                    label: 'Data One',
                    backgroundColor: '#1abc9c',
                    data: [40, 39, 10, 40, 39, 80, 40]
                },
                {
                    label: 'Data 2',
                    backgroundColor: '#34495e',
                    data: [30, 349, 150, 410, 139, 180, 240]
                }
            ]
        }, {responsive: true, maintainAspectRatio: false})
    }

});
