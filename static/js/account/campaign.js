Vue.component('campaign-formset', {
    methods: {
        onButtonDelete(index) {
            this.$emit('deleted');
        }
    },
    props: ['course'],
    template: `        
        <div class="column is-6">
        <div class="box">
        <button class="delete is-pulled-right" @click="onButtonDelete"></button>
        
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
                {'id': 1, 'title': 'Python course', 'url': 'python.org', 'description': 'super course', 'skills': ['django','mongodb']}
            ]
        }
    },
    mounted() {
        bulmaTagsinput.attach();
    },
    methods: {
        addCourse() {
            this.forms.push({});
        },
        delCourse() {
            this.forms.pop();
        },
        saveCampaign() {
            console.log(this.forms);
        },
    },
    template: `<div>
    <div class="title">Campaign</div>
    
    <form>
    
        <div class="columns is-multiline">
            <campaign-formset 
            v-for="course in forms" @deleted="delCourse" 
            v-bind:course="course"
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