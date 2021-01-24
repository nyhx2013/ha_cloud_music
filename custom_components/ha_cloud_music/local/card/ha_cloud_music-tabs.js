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
            arr.push(`<span title="${title}">${title}</span>`)
            eleArr.push(ele)
        }
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha_cloud_music-tabs'
        ha_card.innerHTML = arr.join('')
        this.insertBefore(ha_card, this.children[0])
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
          .hide{display:none!important;}
          .ha_cloud_music-tabs{
            padding: 10px 0;
            display: grid;
            grid-template-columns: repeat(5, 20%);
            text-align: center;
            border-bottom: 1px solid #eee;
            margin-bottom: 5px;
          }
          .ha_cloud_music-tabs span{
            cursor: pointer;
          }
          .ha_cloud_music-tabs .active{
            color: var(--primary-color);
          }
        `
        this.appendChild(style);
        // 保存核心DOM对象
        this.$ = this.querySelector.bind(this)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        const toggleTabs = (title) => {
            let tabs = ha_card.querySelectorAll('span')
            for (let i = 0; i < eleArr.length; i++) {
                let ele = eleArr[i]
                if (ele.dataset['title'] == title) {
                    tabs[i].classList.add('active')
                    ele.classList.remove('hide')
                } else {
                    tabs[i].classList.remove('active')
                    ele.classList.add('hide')
                }
            }
        }
        let { $ } = this
        ha_card.onclick = (event) => {
            const path = event.composedPath()
            const ele = path[0]
            if (ele.nodeName == 'SPAN') {
                toggleTabs(ele.textContent.trim())
            }
        }
        toggleTabs('列表')
    }
}
customElements.define('ha_cloud_music-tabs', HaCloudMusicTabs);