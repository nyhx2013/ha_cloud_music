<template>
  <!--歌单详情-->
  <div class="details">
    <mm-loading v-model="mmLoadShow" />
    <music-list :list="list" @select="selectItem" />
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import { getPlaylistDetail, getUserCloudList } from 'api'
import MmLoading from 'base/mm-loading/mm-loading'
import MusicList from 'components/music-list/music-list'
import { formatTopSongs } from '@/utils/song'
import { loadMixin } from '@/utils/mixin'

export default {
  name: 'Detail',
  components: {
    MmLoading,
    MusicList
  },
  mixins: [loadMixin],
  data() {
    return {
      list: [] // 列表
    }
  },
  created() {
    // 获取歌单详情
    let id = this.$route.params.id
    if (id === '0') {
      getUserCloudList()
        .then(({ data }) => {
          if (data.code === 200) {
            this.list = data.data.map(item => {
              let simpleSong = item.simpleSong
              return {
                id: item.songId,
                name: item.songName,
                singer: item.artist,
                album: item.album,
                image: 'https://p4.music.126.net/xL_4lYc6XKR4dO0u-9HtxQ==/109951164032601371.jpg',
                duration: simpleSong.dt / 1000,
                url: `https://music.163.com/song/media/outer/url?id=${item.songId}.mp3`,
                type: 'cloud'
              }
            })
            this._hideLoad()
          } else {
            this.$mmToast(data.msg)
          }
        })
        .catch(ex => {
          this.$mmToast('需要登录')
        })
      return
    }
    getPlaylistDetail(id).then(res => {
      if (res.data.code === 200) {
        this.list = formatTopSongs(res.data.playlist.tracks)
        document.title = `${res.data.playlist.name} - mmPlayer在线音乐播放器`
        this._hideLoad()
      }
    })
  },
  methods: {
    // 播放暂停事件
    selectItem(item, index) {
      this.selectPlay({
        list: this.list,
        index
      })
    },
    ...mapActions(['selectPlay'])
  }
}
</script>

<style lang="less" scoped>
.details {
  position: relative;
  width: 100%;
  height: 100%;
  .musicList {
    width: 100%;
    height: 100%;
  }
}
</style>
