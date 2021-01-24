class HaCloudMusicVoice extends HTMLElement {

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
        ha_card.className = 'ha_cloud_music-voice'
        ha_card.innerHTML = `
        <div id="inputPanel">
            <ha-icon class="input-mode" icon="mdi:microphone"></ha-icon>
            <input type="text" placeholder="请使用手机语音输入法" autofocus id="txtInput" />
        </div>
        <div class="list">
            <div class="left content">
                <button>😁</button>
                <div><span>
                播放音乐、暂停音乐、下一曲、<br/>
                上一曲、小点声音、大点声音
                </span></div>
            </div>
            <div class="right content">
                <div><span>播放新闻</span></div>
                <button data-cmd="播放新闻">😘</button>
            </div>
            <div class="left content">
                <button>😁</button>
                <div><span>新闻音频资源来自😋乐听头条</span></div>
            </div>
            <div class="right content">
                <div><span>我想听林俊杰的歌</span></div>
                <button data-cmd="我想听林俊杰的歌">😘</button>
            </div>
            <div class="left content">
                <button>😁</button>
                <div><span>林俊杰👌歌手来自网易云音乐</span></div>
            </div>
            <div class="right content">
                <div><span>播放歌曲明天你好</span></div>
                <button data-cmd="播放歌曲明天你好">😘</button>
            </div>
            <div class="left content">
                <button>😁</button>
                <div><span>明天你好😍歌曲来自网易云音乐</span></div>
            </div>
            <div class="right content">
                <div><span>播放专辑段子来了</span></div>
                <button data-cmd="播放专辑段子来了">😘</button>
            </div>
            <div class="left content">
                <button>😁</button>
                <div><span>段子来了😄来自喜马拉雅</span></div>
            </div>
            <div class="right content">
                <div><span>播放电台宋宇选读</span></div>
                <button data-cmd="播放电台宋宇选读">😘</button>
            </div>                
            <div class="left content">
                <button>😁</button>
                <div><span>宋宇选读😜来自网易云音乐</span></div>
            </div>
            <div class="right content">
                <div><span>播放歌单私人雷达</span></div>
                <button data-cmd="播放歌单私人雷达">😘</button>
            </div>     
            <div class="left content">
                <button>😁</button>
                <div><span>私人雷达😊来自网易云音乐哦</span></div>
            </div>
            <div class="right content">
                <div><span>播放广播中央人民广播电台</span></div>
                <button data-cmd="播放广播中央人民广播电台">😘</button>
            </div>
            <div class="left content">
                <button>😁</button>
                <div><span>电台🙌来自蜻蜓FM</span></div>
            </div>
        </div>
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
        #inputPanel{display:flex;align-items: center;text-align:center;}
        #txtInput {
           border-radius: 10px;
           outline: none;
           width:100%;
           box-sizing: border-box;
           padding: 8px 10px;
           border: 1px solid silver;
           margin: 10px;
       }

       .content {
           padding: 10px 0;
           display: flex;
           overflow: auto;
       }

       .content div {
           flex: 1;
       }

       .content span {
           display: inline-block;
           padding: 5px 10px 8px 10px;
       }

       .content button {
           border: none;
           font-size: 30px;
           outline: none;
           width: 55px;
           background-color: transparent;
       }

       .right {
           text-align: right;
       }

       .right span {
           background-color: purple;
           color: white;
           border-radius: 10px 10px 0px 10px;
           text-align: left;
       }

       .right button {
           float: right;

       }

       .left button {
           float: left;
       }

       .left {
           text-align: left;
       }

       .left span {
           background-color: white;
           border:1px solid #eee;
           color: #555;
           border-radius: 10px 10px 10px 0px;
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
        // 显示语音控制界面
        let inputMode = $('.input-mode')
        inputMode.onclick = () => {
            let isText = inputMode.icon == 'mdi:card-text'
            let icon = isText ? 'mdi:microphone' : 'mdi:card-text'
            inputMode.icon = icon
            ha_cloud_music.toast(isText ? '切换到语音模式，自动发送文本' : '切换到文本模式')
        }
        // 语音输入
        this.addMsg = (value) => {
            let div = document.createElement('div')
            div.className = `right content`
            div.innerHTML = `<div><span>${value}</span></div><button data-cmd="${value}">😘</button>`
            $(".list").insertBefore(div, $('.list>div'))

            ha_cloud_music.hass.callApi('POST', 'events/ha_voice_text_event', { text: value }).then(res => {
                ha_cloud_music.toast("命令发送成功")
            })
        }

        let txtInput = $('#txtInput')
        txtInput.oninput = this.throttle(() => {
            // 如果是文本模式，则不处理
            let isText = inputMode.icon == 'mdi:card-text'
            if (isText) return;

            let value = txtInput.value.trim()
            if (value) {
                txtInput.value = ''
                this.addMsg(value)
            }
        }, 1000)
        txtInput.onkeypress = (event) => {
            if (event.keyCode == 13) {
                let value = txtInput.value.trim()
                if (value) {
                    txtInput.value = ''
                    this.addMsg(value)
                }
            }
        }
        // 命令点击
        $('.list').addEventListener('click', (event) => {
            const path = event.composedPath()
            const ele = path[0]
            if ('cmd' in ele.dataset) {
                let text = ele.dataset['cmd']
                ha_cloud_music.hass.callApi('POST', 'events/ha_voice_text_event', { text }).then(res => {
                    ha_cloud_music.toast("命令发送成功")
                })
            }
        })

    }

    

    throttle(callback, time) {
        let timer = null
        return () => {
            if (timer) clearTimeout(timer)
            timer = setTimeout(() => {
                callback()
                timer = null
            }, time)
        }
    }

}
customElements.define('ha_cloud_music-voice', HaCloudMusicVoice);