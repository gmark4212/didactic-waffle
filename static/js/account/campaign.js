Vue.component('campaign-formset', {
    methods: {
        onButtonDelete(index) {
            this.$emit('deleted');
        }
    },
    template: `        
        <div class="column is-6">
        <div class="box">
        <button class="delete is-pulled-right" @click="onButtonDelete"></button>
        
        <div class="field">
            <label class="label">Skills</label>
            <div class="control">
                <input class="input" type="tags" placeholder="Add Tag" value="">
            </div>
        </div>

        <div class="field">
            <label class="label">Title</label>
            <div class="control">
                <input class="input" type="text" placeholder="Best programming course ever">
            </div>
        </div>

        <div class="field">
            <label class="label">URL</label>
            <div class="control">
                <input class="input" type="text" placeholder="https://skoglee.com">
            </div>
        </div>

        <div class="field">
            <label class="label">Description</label>
            <div class="control">
                <textarea class="textarea" placeholder=""></textarea>
            </div>
        </div>
        
        </div>
        </div>`
});

Vue.component('campaign', {
    data: function () {
        return {
            forms: [
                {}
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
    },
    template: `<div>
    <div class="title">Campaign</div>
    
    <form action="#">
    
        <div class="columns is-multiline" id="form-boxes-container">
            <campaign-formset v-for="set in forms" @deleted="delCourse"></campaign-formset>
        </div>
        
         <div class="field is-grouped">
            <div class="control">
                <button class="button is-primary" @click="addCourse">
                <i class="fas fa-plus"></i>&nbsp;Add course</button>
            </div>
            <div class="control">
                <button class="button is-link">Save campaign</button>
            </div>
        </div>
        
    </form> 
</div>`
});