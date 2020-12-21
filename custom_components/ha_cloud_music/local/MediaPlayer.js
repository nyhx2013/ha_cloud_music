import {
    getAuth,
    getUser,
    callService,
    createConnection,
    subscribeEntities,
    ERR_HASS_HOST_REQUIRED
} from "./dist/index.js";

export class MediaPlayer {
    constructor(tokens) {
        this.client_id = `U${Date.now()}`
        this.login(tokens)
    }

    // 登录
    async login(tokens) {
        let auth;
        if (tokens) {
            auth = await getAuth({
                loadTokens() {
                    return JSON.parse(tokens)
                }
            });
        } else {
            try {
                auth = await getAuth({
                    loadTokens() {
                        try {
                            return JSON.parse(localStorage['hassTokens'])
                        } catch { }
                    },
                    saveTokens: (data) => {
                        localStorage['hassTokens'] = JSON.stringify(data)
                    }
                });
            } catch (err) {
                if (err === ERR_HASS_HOST_REQUIRED) {
                    const hassUrl = `${location.protocol}//${location.host}`
                    if (!hassUrl) return;
                    auth = await getAuth({ hassUrl });
                } else {
                    alert(`Unknown error: ${err}`);
                    return;
                }
            }
            if (location.search.includes("auth_callback=1")) {
                history.replaceState(null, "", location.pathname);
            }
        }

        this.ready(auth)
    }

    // 初始化
    async ready(auth) {
        const connection = await createConnection({ auth });
        this.connection = connection;
        getUser(connection).then(user => {
            // 初始化播放器
            this.initAudio()
            console.log("Logged in as", user);
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
        });
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
        const { audio, connection } = this
        this.sendMessage({
            type: "update",
            volume_level: audio.volume,
            is_volume_muted: audio.muted,
            media_duration: audio.duration,
            media_position_updated_at: new Date().toISOString(),
            media_position: audio.currentTime
        })
        await callService(connection, 'homeassistant', 'update_entity', {
            entity_id: "media_player.yun_yin_le"
        })
    }
}