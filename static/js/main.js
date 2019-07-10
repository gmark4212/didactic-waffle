const grades = new Vue({
        el: '#grades',
        data: {
            api: '/api/v1/skills/?search=',
            searchLine: 'python developer',
            skills: [],
            labels: [],
            freqs: [],
            fetching: false,
            api_visible: false,
            about_visible: false,
            advert_visible: false
        },
        computed: {
            detailedOnly: function () {
                let data = this.skills.data;
                if (data) {
                    data = data.filter(function (item) {
                        return 'desc' in item;
                    });
                    return data;
                }
            }
        },
        methods: {
            fetchSkills() {
                this.fetching = true;
                fetch(this.api + this.searchLine, {mode: 'no-cors'})
                    .then(response => response.json())
                    .then(data => {
                        this.skills = data.data;
                        this.labels = data.data.labels;
                        this.freqs = data.data.freqs;
                        this.fetching = false;
                        console.log(this.skills);
                    })
                    .catch(function (err) {
                        this.skills = [];
                        console.log('Fetch Error :-S', err);
                        this.fetching = false;
                    })
            }
        }

    })
;

grades.fetchSkills();
