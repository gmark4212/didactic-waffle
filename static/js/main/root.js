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
                return data.filter(item => 'desc' in item) ;
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
                data = data
                    .filter(item => item.ads && item.ads.length > 0)
                    .map(item => item.ads);
                if (data) {
                    // right side ads
                    this.ads_side = {
                        'first': typeof data[0][0] === 'undefined' ? false : data[0][0]['campaign'],
                        'second': typeof data[0][1] === 'undefined' ? false : data[0][1]['campaign']
                    };
                //    TODO: Add grade ads
                //    TODO: Add card ads
                }
            }
        }

    }
});

grades.fetchSkills();
