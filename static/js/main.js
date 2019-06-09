const app = new Vue({
        el: '#app',
        data: {
            api: '/api/skills/?search=',
            searchLine: 'data scientist',
            skills: [],
            fetching: false
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

app.fetchSkills();
