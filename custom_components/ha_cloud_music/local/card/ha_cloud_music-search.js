class HaCloudMusicSearch extends HTMLElement {

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
        ha_card.className = 'ha_cloud_music-search'
        ha_card.innerHTML = `
<div class="search-input">
    <input type="search" value="" placeholder="请输入要搜索的关键词" />
</div>
<div class="search-radio">
    <label><input type="radio" name="search-radio" value="playlist" checked />歌单</label>
    <label><input type="radio" name="search-radio" value="djradio" />电台</label>
    <label><input type="radio" name="search-radio" value="ximalaya" />专辑</label>
    <label><input type="radio" name="search-radio" value="music" />音乐</label>
</div>
<div class="search-list">
    
</div>
`
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
.ha_cloud_music-search{}
.search-input{padding:10px;}
.search-input input{width:100%; padding:5px;}

.search-radio {display:flex; text-align: center; padding-bottom: 10px;}
.search-radio label{width:100%;}
`
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        let { $ } = this
        let txtSearchInput = $('.search-input input')
        txtSearchInput.onkeypress = (event) => {
            if (event.keyCode == 13) {
                searchAction()
            }
        }
        $('.search-radio').querySelectorAll("input[type='radio']").forEach(ele => {
            ele.onclick = () => {
                searchAction()
            }
        })

        const searchAction = () => {
            let value = txtSearchInput.value.trim()
            if (value) {
                txtSearchInput.value = ''
                let type = $(".search-radio input:checked").value
                ha_cloud_music.toast(`正在搜索【${value}】`)
                $('.search-list').innerHTML = ''
                ha_cloud_music.load(type == 'music' ? 'search-musiclist' : 'search-playlist').then(({ tagName }) => {
                    const element = document.createElement(tagName)
                    $('.search-list').appendChild(element)
                    element.created(type, value)
                })
            }
        }
    }
}
customElements.define('ha_cloud_music-search', HaCloudMusicSearch);