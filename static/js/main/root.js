const grades = new Vue({
        el: '#grades',
        data: {
            api: '/api/v1/skills/?search=',
            searchLine: 'data scientist',
            skills: [],
            labels: [],
            freqs: [],
            ads_side: {},
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
            },
            sideBlockAds: function () {
                let data = this.skills.data;
                if (data) {
                    data = data.filter(function (item) {
                        return item.ads;
                    });
                    data = data.slice(0,2);
                    data = data[0]['ads'];
                    return {0: data[0]['campaign'], 1: data[1]['campaign']};
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
                        this.sortAds();
                    })
                    .catch(function (err) {
                        this.skills = [];
                        console.log('Fetch Error :-S', err);
                        this.fetching = false;
                    })
            },
            sortAds() {
                let data = this.skills.data;
                if (data) {
                    data = data.filter(function (item) {
                        return item.ads;
                    });
                    data = data.slice(0, 2);
                    data = data[0]['ads'];
                    this.ads_side = {'first': data[0]['campaign'], 'second': data[1]['campaign']};
                    console.log(this.ads_side);
                }
        }

    }
});

grades.fetchSkills();
