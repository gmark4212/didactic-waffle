const grades = new Vue({
        el: '#grades',
        data: {
            api: '/api/v1/skills/?search=',
            searchLine: 'data scientist',
            skills: [],
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
                        console.log(data);
                        this.skills = data;
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
