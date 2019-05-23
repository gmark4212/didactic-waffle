const app = new Vue({
        el: '#app',
        data: {
            api: '/api/skills/?search=',
            searchLine: 'программист python',
            skills: []
        },
        methods: {
            fetchSkills() {
                fetch(this.api + this.searchLine, {mode: 'no-cors'})
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                        this.skills = data;
                    })
                    .catch(function (err) {
                        this.skills = [];
                        console.log('Fetch Error :-S', err);
                    })
            },
        }

    });

app.fetchSkills();
