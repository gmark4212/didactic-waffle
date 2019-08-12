Vue.component('input-tag', vueInputTag.default);

Vue.component('campaign-formset', {
    methods: {},
    props: ['course'],
    template: `        
        <div class="column is-6">
        <div class="box">
        <button class="delete is-pulled-right" @click="$emit('deleted', course.id)"></button>
        
        <div class="field">
            <label class="label">Title</label>
            <div class="control">
                <input class="input" type="text" placeholder="Best programming course ever" v-model="course.title">
            </div>
        </div>
        
        <div class="field">
            <label class="label">Skills</label>
            <div class="control">
                <input-tag v-model="course.skills" limit="5" placeholder="Add skills"></input-tag>
            </div>
        </div>        

        <div class="field">
            <label class="label">URL</label>
            <div class="control">
                <input class="input" type="text" placeholder="https://skoglee.com" v-model="course.url">
            </div>
        </div>

        <div class="field">
            <label class="label">Description</label>
            <div class="control">
                <textarea class="textarea" placeholder="" v-model="course.description"></textarea>
            </div>
        </div>
        
        </div>
        </div>
`
});

Vue.component('campaign', {
    data: function () {
        return {
            forms: [],
            saved: true
        }
    },
    mounted() {
        this.fetchUserCampaign();
    },
    watch: {
        forms: {
            handler: 'campaignChanged',
            deep: true
        }
    },
    methods: {
        campaignChanged() {
            this.saved = false;
        },
        fetchUserCampaign() {
            fetch('/campaign/fetch', {
                method: "post",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'request': 'campaign'})
            })
                .then(response => response.json())
                .then(data => {
                    if (data) {
                        this.forms = data;
                    }
                })
        },
        addCourse() {
            this.forms.push({'id': this.generateUUID()});
        },
        delCourse(cid) {
            this.forms = this.forms.filter((e) => {
                return e.id !== cid
            });
        },
        campaignSubmit() {
            fetch("/campaign/save", {
                method: "post",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.forms)
            })
                .then((response) => {
                    if (response.ok) {
                        this.saved = true;
                    }
                });
        },
        generateUUID() {
            let d = new Date().getTime();
            if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
                d += performance.now(); //use high-precision timer if available
            }
            let newGuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                let r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return newGuid;
        }
    },
    template: `<div>
    <div class="title">Campaign</div>
    
    <form @submit.prevent="campaignSubmit">
    
        <div class="columns is-multiline">
            <campaign-formset 
            v-for="(course, index)  in forms" @deleted="delCourse" 
            :course="course"
            :key="course.id"
            ></campaign-formset>
        </div>

         <div class="field is-grouped">
            <div class="control">
                <button class="button is-primary" @click="addCourse">
                <i class="fas fa-plus"></i>&nbsp;Add course</button>
            </div>
            <div class="control">
                <button type="submit" class="button is-link" :disabled="saved">
                    Save campaign
                </button>
            </div>
        </div>
        
    </form> 
</div>`
});
