<template>
  <div v-loading="loading">
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="input-container">
          <el-input v-model="videoUrl" placeholder="请输入 bilibili 视频链接"></el-input>
          <el-button type="primary" @click="parseVideo" style="margin-left: 20px;">解析</el-button>
        </div>
      </el-col>
      <el-col :span="4">
        <el-select v-model="language" placeholder="请选择">
          <el-option label="自动识别" value="auto"></el-option>
          <el-option label="中文" value="zh"></el-option>
          <el-option label="英文" value="en"></el-option>
          <el-option label="日文" value="ja"></el-option>
        </el-select>
      </el-col>
      <el-col :span="8" style="display: flex;align-items: center;height: 40px;">
        <el-checkbox v-model="use_large">use large</el-checkbox>
        <el-checkbox v-model="translator">外译中</el-checkbox>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="8">
        <video ref="player" class="plyr" controls>
          <source src="" type="">
          <track kind="captions" label="中文" src="" srclang="zh" default>
        </video>
      </el-col>
      <el-col :span="8">
        <div style="max-height: 300px; overflow: auto;font-size: 20px;">
          <div v-html="txt_content"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <el-button @click="summary()" style="margin-left: 20px;" v-if="txt_content">一建总结</el-button>
        <div style="max-height: 300px; overflow: auto;font-size: 20px;">
          <div v-html="sum_content"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>
  
<script>
import axios from 'axios';
import 'plyr/dist/plyr.css'; // Import Plyr styles
import Plyr from 'plyr'; // Import Plyr library

export default {
  props: {
    baseUrl: String
  },
  data() {
    return {
      videoUrl: '', // 输入的视频链接
      player: null,
      txt_content: '',
      loading: false,
      sum_content: '',
      video_path: '',
      audio_path: '',

      language: 'auto',
      use_large: false,
      translator: false

    };
  },
  components: {
    Plyr
  },
  mounted() {
    this.initPlyr();
  },
  methods: {
    summary() {
      if (!this.txt_content) {
        alert("请先转写内容");
      }
      const formData = {
        txt_content: this.txt_content.replace('<br/>', ''),
        max_tokens: 100
      };
      this.loading = true;

      axios.post(this.baseUrl + '/summary', formData)
        .then(response => {
          this.sum_content = response.data;
        })
        .catch(error => {
          this.$message.error('总结失败');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    // 视频解析
    parseVideo() {

      if (!this.videoUrl) {
        alert("请输入视频链接");
      }
      this.loading = true;
      axios.get(this.baseUrl + '/online_download?online_url=' + this.videoUrl)
        .then(response => {
          this.video_path = response.data.video_path;
          this.audio_path = response.data.audio_path;
          this.submitForm(this.video_path)
        })
        .catch(error => {
          this.$message.error('表单提交失败');
          this.loading = false;
        })
        .finally(() => {
        });
    },
    // 初始化播放器
    initPlyr() {
      this.player = new Plyr(this.$refs.player, {
        // 自动播放
        autoplay: false,
        // 默认音量（0 到 1 之间的值）
        volume: 0.5,
        captions: { active: true, language: 'auto' },
        controls: [
          'play-large',
          'play',
          'progress',
          'current-time',
          'volume',
          'captions',
          'settings',
          'fullscreen',
        ]
      });
    },
    // 开始转写
    submitForm(filePath) {
      const formData = {
        filePath: filePath,
        model: this.use_large ? 'large' : 'tiny',
        language: this.language,
        translator: this.translator
      };
      this.loading = true;
      axios.post(this.baseUrl + '/transcription', formData)
        .then(response => {
          this.txt_content = response.data.txt_content.replace(/\n/g, '<br/>');
          this.getSubtitleContent(filePath)
        })
        .catch(error => {
          this.$message.error('表单提交失败');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    // 获取字幕内容
    getSubtitleContent(sub_path) {
      axios.get(this.baseUrl + '/sub?sub_path=' + sub_path.replace(/\.[^.]+$/, '.vtt'))
        .then(response => {
          this.reloadPlyr(sub_path, URL.createObjectURL(new Blob([response.data], { type: 'text/vtt' })))
        })
        .catch(error => {
          console.error('Failed to load subtitle:', error);
        });
    },
    // 重新加载播放器
    reloadPlyr(videoUrl, subSrc) {
      this.player.source = {
        type: 'video',
        sources: [
          {
            src: this.baseUrl + '/video?file_path=' + videoUrl,
            type: 'video/mp4',
          },
        ],
        tracks: [
          {
            kind: 'captions',
            label: '中文',
            src: subSrc,
            srclang: 'zh',
            default: true
          }
        ],
      };
    },
  },
};
</script>
<style>
.plyr {
  max-width: 100%;
  max-height: 100vh;
}

.input-container {
  display: flex;
  align-items: center;
}

.el-row {
  margin-bottom: 20px;

  &:last-child {
    margin-bottom: 0;
  }
}
</style>