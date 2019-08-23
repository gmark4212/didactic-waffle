Vue.component('history', {
    data: function () {
        return {
            history: []
        }
    },
    mounted() {
        this.fetchHistory();
    },
    methods: {
        fetchHistory() {
            fetch('/account/payment/history/', {
                method: "get",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data) {
                        this.history = data;
                    }
                })
        },

    },
    template: `<div class="container">
    <table class="table" v-if="history.length">
        <thead>
        <tr>
            <th>Created</th>
            <th>Amount</th>
            <th>Paid til</th>
            <th>Status</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="charge in history">
            <td>{{ charge.created_dt }}</td>
            <td>{{ charge.amount }} $</td>
            <td>{{ charge.paid_til_dt }}</td>
            <td>{{ charge.status }}</td>
        </tr>
        </tbody>
    </table>
    <div v-else>
        <progress class="progress is-small is-info" max="100">60%</progress>
    </div>
</div>`
});