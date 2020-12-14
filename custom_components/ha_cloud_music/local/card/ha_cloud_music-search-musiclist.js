class HaCloudMusicSearchMusicList extends HTMLElement {

    // 创建界面
    created(type, value) {
        this.type = type
        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('div');
        ha_card.className = 'ha-cloud-music-music-list'
        ha_card.innerHTML = `
        <div class="music-list">

        </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        .music-item {
            display: flex;margin-bottom: 10px;
            cursor: pointer;
        }
        .music-item img {
            width: 50px;
        }
        .music-info {
            text-align: right;
            flex: 1;
        }
        .music-info p {
            padding: 0 10px;
            margin: 5px 0;
        }
        .music-info p:first-child {
            text-align: left;
        }
        .music-info p:nth-child(2) {
            color: gray;
            font-size: 12px;
        }
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        let { $ } = this
        ha_cloud_music.showLoading()
        // 请求数据
        ha_cloud_music.fetchApi({
            type: `search-${type}`,
            name: value
        }).then(res => {
            const df = document.createDocumentFragment()
            res.forEach(({ id, name, singer, search_source, image }, index) => {
                const div = document.createElement('div')
                div.className = 'music-item'
                div.title = name
                div.innerHTML = `<div><img src="${image}" /></div>
                                    <div class="music-info">
                                        <p>${name} - ${singer}</p>
                                        <p> — ${search_source}</p>
                                    </div>`
                df.appendChild(div)
                div.onclick = () => {
                    ha_cloud_music.showLoading()
                    ha_cloud_music.fetchApi({ type: 'play_media', list: res, index }).finally(() => {
                        ha_cloud_music.hideLoading()
                    })
                }
            })
            $('.music-list').appendChild(df)
        }).finally(() => {
            ha_cloud_music.hideLoading()
        })
    }
}

// 定义DOM对象元素
customElements.define('ha_cloud_music-search-musiclist', HaCloudMusicSearchMusicList);