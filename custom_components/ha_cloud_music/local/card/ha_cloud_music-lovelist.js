class HaCloudMusicLovelist extends HTMLElement {

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
        ha_card.className = 'ha_cloud_music-lovelist'
        ha_card.innerHTML = `<ol></ol>`
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        ol li{padding:10px; border-bottom:1px solid #eee;cursor:pointer;}
        ol li ha-icon{float:right;}
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        this.reload()
        ha_cloud_music.addEventListener('love_set', () => {
            this.reload()
        })
    }

    reload() {
        let { $ } = this
        ha_cloud_music.fetchApi({
            type: 'love_get'
        }).then(res => {
            const df = document.createDocumentFragment()
            let arr = res.data
            arr.forEach((ele, index) => {
                const li = document.createElement('li')
                li.dataset['index'] = index
                li.innerHTML = `
                    ${ele.song} - ${ele.singer}
                    <ha-icon icon="mdi:delete" title="删除"></ha-icon>
                `
                df.appendChild(li)
            })
            $('ol').innerHTML = ''
            $('ol').appendChild(df)
            $('ol').onclick = (event) => {
                const path = event.composedPath()
                const li = path[0]
                if (li.nodeName == 'LI') {
                    const list = arr
                    const index = parseInt(li.dataset['index'])
                    ha_cloud_music.toast(`开始播放【${list[index].name}】`)
                    // 播放FM
                    ha_cloud_music.fetchApi({ type: 'play_media', list, index })
                } else {
                    li = path[3]
                    const index = parseInt(li.dataset['index'])
                    const { id, type } = arr[index]
                    // 删除收藏
                    ha_cloud_music.fetchApi({ type: 'love_delete', id, music_type: type }).then(res => {
                        ha_cloud_music.toast(res.msg)
                        this.reload()
                    })
                }
            }
        })
    }

    updated(stateObj) {
        let { $ } = this

    }
}
customElements.define('ha_cloud_music-lovelist', HaCloudMusicLovelist);