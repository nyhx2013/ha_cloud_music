class HaCloudMusicVersion extends HTMLElement {

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
        ha_card.className = 'ha_cloud_music-version'
        ha_card.innerHTML = `
        <div class="version-info">
            <div class="line"></div>
            <a href="https://github.com/shaonianzhentan/ha_cloud_music" target="_blank">插件版本：<span class="version"></span></a>
            <div class="line"></div>
        </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        .version-info{text-align:center;display:flex;padding:10px 0;margin-top:10px;}
        .version-info a{text-decoration:none;color:gray;width: 300px;}
        .version-info .line{border-bottom:1px solid #ccc; height:10px;width:60%;}
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
        $('.version').textContent = stateObj.attributes.version
    }
}
customElements.define('ha_cloud_music-version', HaCloudMusicVersion);