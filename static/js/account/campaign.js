Vue.component('campaign-formset', {
    methods: {},
    props: ['course'],
    template: `        
        <div class="column is-6">
        <div class="box">
        <button class="delete is-pulled-right" @click="$emit('deleted', course.id)"></button>
        
        <div class="field">
            <label class="label">Skills</label>
            <div class="control">
                <input class="input" type="tags" placeholder="Add Tag" v-model="course.skills">
            </div>
        </div>

        <div class="field">
            <label class="label">Title</label>
            <div class="control">
                <input class="input" type="text" placeholder="Best programming course ever" v-model="course.title">
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
        </div>`
});

Vue.component('campaign', {
    data: function () {
        return {
            forms: [
                {
                    'id': 0,
                    'title': 'Python course',
                    'url': 'python.org',
                    'description': 'super Python course',
                    'skills': ['django', 'mongodb']
                },
                {
                    'id': 1,
                    'title': 'Java course',
                    'url': 'java.org',
                    'description': 'java',
                    'skills': ['java', 'spring']
                },
                {
                    'id': 2,
                    'title': 'Node.JS course',
                    'url': 'nodejs.org',
                    'description': 'Node super course',
                    'skills': ['javascript', 'express']
                }
            ]
        }
    },
    mounted() {
        bulmaTagsinput.attach();
    },
    methods: {
        fetchCourses() {},
        addCourse() {
            this.forms.push({'id': this.generateUUID()});
        },
        delCourse(cid) {
            this.forms = this.forms.filter((e) => {
                return e.id !== cid
            });
        },
        saveCampaign() {
            console.log(this.forms);
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
    
    <form>
    
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
                <button class="button is-link" @click="saveCampaign">Save campaign</button>
            </div>
        </div>
        
    </form> 
</div>`
});