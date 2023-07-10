import App from './App'

import Vue from 'vue'
import './uni.promisify.adaptor'
import cuCustom from '@/public/colorui/components/cu-custom.vue'
Vue.component('cu-custom', cuCustom)

import uView from '@/public/uview-ui';
Vue.use(uView);

Vue.config.productionTip = false
App.mpType = 'app'
const app = new Vue({
	...App
})
app.$mount()