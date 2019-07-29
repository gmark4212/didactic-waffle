Vue.component('campaign', {
    mounted() {
        bulmaTagsinput.attach();
    },
    template: `<div>
    <div class="title">Campaign</div>
    <a href="" class="button is-light"><i class="fas fa-plus"></i>&nbsp;Add course</a>
    <br><br>

    <form action="#">
        <div class="field">
            <label class="label">Tags</label>
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

        <div class="field is-grouped">
            <div class="control">
                <button class="button is-link">Submit</button>
            </div>
            <div class="control">
                <button class="button is-text">Cancel</button>
            </div>
        </div>

    </form> 

</div>`
});