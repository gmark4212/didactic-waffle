Vue.component('payment', {
    data: function () {
        return {
            public_key: 'pk_test_7qWc36Li8coNnbkqgXKBtpqV009cvA8sTF',
            displayError: undefined,
            customer: undefined,
            result: undefined
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
                    if (data) {
                        this.customer = data;
                    }
                })
        },
        checkout() {
            let stripe = Stripe(this.public_key);
            let params = {
                items: [{plan: 'plan_FeCNCWp990RaQy', quantity: 1}],
                successUrl: 'https://skoglee.com/payment/success',
                cancelUrl: 'https://skoglee.com/payment/canceled',
                customerEmail: this.customer.email
            };

            if (this.customer.stripe_id) {
                params['clientReferenceId'] = this.customer.stripe_id
            }

            stripe.redirectToCheckout(params)
                .then(function (result) {
                    this.result = result;
                        if (result.error) {
                            this.displayError = result.error.message;
                        }
                    }
                );
        },
    },
    template: `<div>

<div class="notification is-danger" v-if="displayError">
    {{ displayError }}
</div>

<div class="pricing-table">

  <div class="pricing-plan is-primary is-active">
    <div class="plan-header">Starter</div>
    <div class="plan-price"><span class="plan-price-amount"><span class="plan-price-currency">$</span>5</span>/month</div>
    <div class="plan-items">
      <div class="plan-item">50 clicks limit</div>
      <div class="plan-item">3 courses limit</div>
      <div class="plan-item">-</div>
      <div class="plan-item">-</div>
    </div>
    <div class="plan-footer">
        <div v-if="customer.paid"><strong>Active plan</strong></div>
        <button class="button is-primary is-fullwidth" @click="checkout" v-else>Pay per month</button>
    </div>
  </div>

  <div class="pricing-plan is-info">
    <div class="plan-header">Startup</div>
    <div class="plan-price"><span class="plan-price-amount"><span class="plan-price-currency">$</span>20</span>/month</div>
    <div class="plan-items">
      <div class="plan-item">300 clicks limit</div>
      <div class="plan-item">10 courses limit</div>
      <div class="plan-item">Support</div>
      <div class="plan-item">-</div>
    </div>
    <div class="plan-footer">
      <button class="button is-fullwidth" disabled="disabled" title="Coming soon">Choose</button>
    </div>
  </div>

  <div class="pricing-plan is-success">
    <div class="plan-header">Global</div>
    <div class="plan-price"><span class="plan-price-amount"><span class="plan-price-currency">$</span>60</span>/month</div>
    <div class="plan-items">
      <div class="plan-item">Maximum clicks</div>
      <div class="plan-item">Unlimited courses</div>
      <div class="plan-item">Premium support</div>
      <div class="plan-item">Top positions</div>
    </div>
    <div class="plan-footer">
      <button class="button is-fullwidth" disabled="disabled" title="Coming soon">Choose</button>
    </div>
  </div>

</div>

</div>

`
});