<template>
  <!--歌单详情-->
  <div class="details">
    <mm-loading v-model="mmLoadShow" />
    <music-list
      :list="list"
      @select="selectItem"
    >
      <div
        slot="listBtn"
        class="list-btn"
      >
        <span @click="loadMore">加载更多</span>
      </div>
    </music-list>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import { getFmList, getDjProgram, getXMLYlist } from 'api'
import MmLoading from 'base/mm-loading/mm-loading'
import MusicList from 'components/music-list/music-list'
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
      list: [], // 列表
      id: '',
      type: '',
      page: 1,
      size: 12,
      isEnd: false
    }
  },
  created() {
    this.id = this.$route.params.id
    this.type = this.$route.query.type
    this.loadMore()
  },
  methods: {
    loadMore() {
      let { type, id, page, isEnd } = this
      if (isEnd) return
      this.mmLoadShow = true

      if (type === '163') {
        this.loadDjProgram({ id, page })
      } else if (type === 'xmly') {
        this.loadXMLYlist({ id, page })
      } else {
        this.loadFmList({ id, page })
      }
    },
    // 获取DJ详情
    loadDjProgram({ id, page }) {
      let size = 30
      getDjProgram(id, (page - 1) * size, size).then(res => {
        let { code, programs } = res.data
        let arr = []
        if (code === 200) {
          programs.forEach(item => {
            let { id, duration } = item.mainSong
            let { brand, nickname } = item.dj
            arr.push({
              id,
              name: item.name,
              album: brand,
              image: item.coverUrl,
              duration: duration / 1000,
              type: 'djradio',
              singer: nickname,
              url: '' + id
            })
          })
        }
        Array.prototype.push.apply(this.list, arr)
        this.list.splice(0, 0)
        this._hideLoad()
        this.page += 1
      })
    },
    // 获取歌单详情
    loadFmList({ id, page }) {
      getFmList({ id, page }).then(res => {
        Array.prototype.push.apply(this.list, res.list)
        this.list.splice(0, 0)
        this._hideLoad()
        this.page += 1
        if (this.list.length >= res.total) this.isEnd = true
      })
    },
    // 获取歌单详情
    loadXMLYlist({ id, page }) {
      getXMLYlist({ id, page }).then(res => {
        Array.prototype.push.apply(this.list, res.list)
        this.list.splice(0, 0)
        this._hideLoad()
        this.page += 1
        if (this.list.length >= res.total) this.isEnd = true
      })
    },
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
    .list-btn {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 50px;
      span {
        padding: 5px 20px;
        cursor: pointer;
        user-select: none;
        &:hover {
          color: @text_color_active;
        }
      }
    }
  }
}
</style>
