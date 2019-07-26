Vue.component('left-side-menu', {
    data: function () {
        return {
            menu: [true, false, false, false, false]
        }
    },
    methods: {
        resetMenuActivity() {
            this.menu = [false, false, false, false, false]
        },
        selectItem(index) {
            this.resetMenuActivity();
            this.menu[index] = true;
            this.$emit('menu-selected', index)
        },
    },
    template: '<aside class="column is-2">\n' +
        '    <nav class="menu">\n' +
        '       <p class="menu-label">\n' +
        '            General\n' +
        '        </p>\n' +
        '        <ul class="menu-list">\n' +
        '            <li><a href="#" :class="{\'is-active\':menu[0]}" @click="selectItem(0)">Dashboard</a></li>\n' +
        '            <li><a href="#" :class="{\'is-active\':menu[1]}" @click="selectItem(1)">Campaign</a></li>\n' +
        '        </ul>\n' +
        '        <p class="menu-label">\n' +
        '            Administration\n' +
        '        </p>\n' +
        '        <ul class="menu-list">\n' +
        '            <li><a href="#" :class="{\'is-active\':menu[2]}" @click="selectItem(2)">Settings</a></li>\n' +
        '        </ul>\n' +
        '       <p class="menu-label">\n' +
        '            Transaction\n' +
        '        </p>\n' +
        '        <ul class="menu-list">\n' +
        '            <li><a href="#" :class="{\'is-active\':menu[3]}" @click="selectItem(3)">Payments</a></li>\n' +
        '            <li><a href="#" :class="{\'is-active\':menu[4]}" @click="selectItem(4)">Balance</a></li>\n' +
        '        </ul>\n' +
        '      </nav>\n' +
        '</aside>'
});

const account = new Vue({
    el: '#account_spa',
    data: {
        selected_menu: 0
    },
    methods: {
        onMenuSelect(value) {
            this.selected_menu = value
        }
    }
});

