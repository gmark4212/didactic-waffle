Vue.component('settings', {
    data: function () {
        return {
            customer: []
        }
    },
    mounted() {
        this.fetchCustomer();
    },
    methods: {
        fetchCustomer() {
            fetch('/account/customer/', {
                method: "get",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    this.customer = [];
                    if (data) {
                        this.customer = data;
                    }
                })
        },

    },
    template: `<div>

<div class="field">
<label class="label">Name</label>
  <p class="control">
    <input class="input" :value="customer.name">
  </p>
</div>

<div class="field">
<label class="label">E-mail</label>
  <p class="control has-icons-left has-icons-right">
    <input class="input" type="email" :value="customer.email" disabled>
    <span class="icon is-small is-left">
      <i class="fas fa-envelope"></i>
    </span>
  </p>
</div>

<div class="field">
<label class="label">Stripe ID</label>
  <p class="control">
    <input class="input" :value="customer.stripe_id" disabled>
  </p>
</div>

<div class="field">
<label class="label">Current campaign paid</label>
  <p class="control">
    <input class="input" :value="customer.paid" disabled>
  </p>
</div>


</div>`
});