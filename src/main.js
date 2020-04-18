import Vue from 'vue'
import App from './App.vue'
import './plugins/element.js'


import VueI18n from 'vue-i18n'

Vue.use(VueI18n) // 通过插件的形式挂载

const i18n = new VueI18n({
  locale: 'zh-CN',    // 语言标识
  // locale: 'en-US',    // 语言标识
  // locale:this.$i18n.locale, // 通过切换locale的值来实现语言切换
  messages: {
    'zh-CN': require('./common/lang/zh'),   // 中文语言包
    'en-US': require('./common/lang/en')    // 英文语言包
  }
});


Vue.config.productionTip = false

new Vue({
  i18n,
  render: h => h(App),
}).$mount('#app')
