export class MediaPlayer {
    constructor() {
        this.client_id = `U${Date.now()}`
        this.ready()
    }

    // 初始化
    async ready() {
        const { connection } = window.ha_cloud_music.hass
        this.connection = connection
        // 初始化播放器
        this.initAudio()
        // 这里通知连接
        const { client_id } = this
        // 这里写代码咯
        connection.subscribeEvents((res) => {
            // console.log(res)
            const { audio } = this
            // 根据格式操作
            let evobj = res.data
            let value = evobj.data
            switch (evobj.type) {
                case 'init':
                    console.log('初始化数据：', value)
                    if (value.client_id == client_id) {
                        audio.src = value.media_url
                        audio.play()
                        setTimeout(() => {
                            audio.volume = value.volume_level
                            audio.currentTime = value.media_position
                        }, 500)
                    }
                    break;
                case 'tts': // 文字转语音
                    const ttsAudio = new Audio()
                    ttsAudio.src = value
                    ttsAudio.play()
                    break;
                case 'load':
                    audio.src = value
                    audio.play()
                    break;
                case 'play':
                    audio.play()
                    break;
                case 'pause':
                    audio.pause()
                    break;
                case 'volume_set':
                    audio.volume = value
                    this.updateAudio()
                    break;
                case 'media_position':
                    audio.currentTime = value
                    this.updateAudio()
                    break;
                case 'is_volume_muted':
                    audio.muted = value
                    this.updateAudio()
                    break;
            }
        }, 'ha_cloud_music_event')
        // 初始化请求
        this.sendMessage({
            type: 'init',
            client_id
        })
    }

    // 初始化播放器
    initAudio() {
        const audio = new Audio()
        let step = 0
        // 音乐进度
        audio.ontimeupdate = () => {
            if (step > 5) {
                this.updateAudio()
                step = 0
            }
            step++
        }
        this.audio = audio
    }

    // 发送信息
    sendMessage(data) {
        this.connection.sendMessage({
            type: 'ha_cloud_music_event',
            data
        })
    }

    // 音频更新
    async updateAudio() {
        const { audio } = this
        this.sendMessage({
            type: "update",
            volume_level: audio.volume,
            is_volume_muted: audio.muted,
            media_duration: audio.duration,
            media_position_updated_at: new Date().toISOString(),
            media_position: audio.currentTime
        })
        window.ha_cloud_music.callService('homeassistant.update_entity', {
            entity_id: "media_player.yun_yin_le"
        })
    }
}