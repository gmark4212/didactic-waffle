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
        methods: {
            fetchSkills() {
                this.fetching = true;
                fetch(this.api + this.searchLine, {mode: 'no-cors'})
                    .then(response => response.json())
                    .then(data => {
                        this.skills = data.data;
                        this.labels = this.skills.labels;
                        this.freqs = this.skills.freqs;
                        this.fetching = false;
                    })
                    .catch(function (err) {
                        this.skills = [];
                        console.log('Fetch Error :-S', err);
                        this.fetching = false;
                    })
            }
        }

    });

grades.fetchSkills();
