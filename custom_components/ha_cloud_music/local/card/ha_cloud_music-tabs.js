class HaCloudMusicTabs extends HTMLElement {

    constructor() {
        super()
        this.created()
    }
    // 创建界面
    created() {
        /* ***************** 基础代码 ***************** */
        let arr = []
        let eleArr = []
        for (let ele of this.children) {
            const title = ele.dataset['title']
            arr.push(`<mwc-tab id="${title}" label="${title}"></mwc-tab>`)
            eleArr.push(ele)
        }
        // 创建面板
        const ha_card = document.createElement('mwc-tab-bar');
        ha_card.innerHTML = arr.join('')
        this.insertBefore(ha_card, this.children[0])
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
          .hide{display:none!important;}         
        `
        this.appendChild(style);
        // 保存核心DOM对象
        this.$ = this.querySelector.bind(this)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        const toggleTabs = (title) => {
            for (let i = 0; i < eleArr.length; i++) {
                let ele = eleArr[i]
                if (ele.dataset['title'] == title) {
                    ele.classList.remove('hide')
                } else {
                    ele.classList.add('hide')
                }
            }
        }
        let { $ } = this
        ha_card.addEventListener("MDCTab:interacted", (event) => {
            // console.log(event.detail.tabId)
            toggleTabs(event.detail.tabId)
        })
        toggleTabs('列表')
    }
}
customElements.define('ha_cloud_music-tabs', HaCloudMusicTabs);