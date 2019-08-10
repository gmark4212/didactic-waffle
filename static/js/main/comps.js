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
    },
    watch: {
        skills() {
            this.renderPieChart();
        }
    }
});

Vue.component('ads-card', {
    props: ['title', 'desc', 'url'],
    template: '    <div class="notification is-light">\n' +
        '            <p><h1 class="title is-6">{{ title }}</h1></p>\n' +
        '            <p>{{ desc|truncate(200) }}</p>\n' +
        '            <br><p><a :href="`${url}`" class="button is-success" target="_blank">Learn</a></p>\n' +
        '        </div>'


});

Vue.component('skill-card', {
    props: ['skill'],
    template: '<div class="card">\n' +
        '  <div class="card-content">\n' +
        '    <div class="media">\n' +
        '      <div class="media-left">\n' +
        '        <figure class="image is-64x64">\n' +
        '          <a :href="`${skill.site}`" target="_blank"><img :src="`${skill.logo}`" alt=""></a>\n' +
        '        </figure>\n' +
        '      </div>\n' +
        '      <div class="media-content">\n' +
        '        <a :href="`${skill.site}`" target="_blank"><p class="title is-4">{{ skill._id }}</p></a>\n' +
        '        <p class="subtitle is-6">{{ skill.ctg }}</p>\n' +
        '      </div>\n' +
        '    </div>\n' +
        '    <div class="content">\n' +
        '      {{ skill.desc }}\n' +
        '      <br>\n' +
        '      <a href="">Learn</a>\n' +
        '    </div>\n' +
        '  </div>\n' +
        '</div>'
});

Vue.component('skill-media', {
    props: ['skill'],
    template: '<article class="media">\n' +
        '  <figure class="media-left">\n' +
        '    <p class="image is-64x64">\n' +
        '      <img :src="`${skill.logo}`" alt="">\n' +
        '    </p>\n' +
        '  </figure>\n' +
        '  <div class="media-content">\n' +
        '    <div class="content">\n' +
        '      <p>\n' +
        '        <strong>{{ skill._id }}</strong> <small>#{{ skill.ctg }}</small>\n' +
        '        <br>\n' +
        '        {{ skill.desc }}\n' +
        '      </p>\n' +
        '    </div>' +
        '</div>\n' +
        '</article>'
});
