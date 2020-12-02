class HaCloudMusicCard extends HTMLElement {

    constructor() {
        super()
        this.created()
    }
    // 创建界面
    created() {
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha_cloud_music-card'
        ha_card.innerHTML = `
         
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
    
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        let { $ } = this
    }

    updated(stateObj) {
        let { $ } = this
        
    }
}
customElements.define('ha_cloud_music-card', HaCloudMusicCard);